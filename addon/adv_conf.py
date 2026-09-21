"""
Advanced config: field config AST and field config visitor
"""

import io
import logging
import os
import typing as T
from abc import ABC, abstractmethod
from enum import IntEnum

import anki.notes
import requests

from . import _typing as _T
from . import constants as C
from . import misc, noteManager, queryApi

logger = logging.getLogger('dict2Anki.adv_conf')


class FConfVisitor(ABC):
    """Called by field config AST to do varias things based on different
    implementations.
    """

    @abstractmethod
    def visit_api(self, api: str) -> bool:
        pass

    @abstractmethod
    def visit_empty(self) -> bool:
        pass

    @abstractmethod
    def visit_note_flag(self, flag: int) -> bool:
        pass


class ApiFConfVisitor(FConfVisitor):
    """Fetching query APIs, store results in `query_cache`. also download audios
    to temp folder.
    """

    def __init__(self, word: str, field: str, query_cache: dict[str, T.Optional[_T.QueryWordData]]):
        self.word = word
        self.field = field
        self.query_cache = query_cache

    def visit_api(self, api: str) -> bool:
        query_api = queryApi.apis.get(api)
        if query_api is None:
            return False

        api_data = self.query_cache.setdefault(api, query_api.query(self.word))

        if api_data is None:
            return False

        def download_audio() -> bool:
            if url := api_data[self.field]:
                return self._download_audio(query_api.session, url)

            logger.warning(
                f'Cannot download audio: URL is empty! word: {self.word}, field: {self.field}, API data: (next line)\n{api_data}'
            )
            return False

        if self.field == C.F_AMEPRON or self.field == C.F_BREPRON:
            return download_audio()

        return True

    def visit_empty(self) -> bool:
        return True

    def visit_note_flag(self, flag: int) -> bool:
        return False

    def _download_audio(self, session: requests.Session, url: str) -> bool:
        ret = True

        dst_dir = misc.tmp_audio_dir()
        os.makedirs(dst_dir, exist_ok=True)

        fpath = os.path.join(
            dst_dir,
            misc.audio_fname(self.field, self.word),
        )
        try:
            misc.download_file(session, fpath, url)
            logger.info(f'发音下载完成：{fpath}, {url}')
        except Exception as e:
            ret = False
            logger.warning(f'下载{fpath}, {url}，异常: {e}')
            misc.rm_file(fpath)

        return ret


class NoteFConfVisitor(FConfVisitor):
    """update note field value"""

    def __init__(
        self,
        word: str,
        field: str,
        note: anki.notes.Note,
        query_cache: dict[str, T.Optional[_T.QueryWordData]],
        out_flag_ref: T.Optional[list[int]],
    ):
        """
        Args:
            out_set_flag: a list of single int to indicate whether flag should
                be set. 0 means do not set.
        """
        self.word = word
        self.field = field
        self.note = note
        self.query_cache = query_cache
        self.out_flag_ref = out_flag_ref

    def visit_api(self, api: str) -> bool:
        api_data = self.query_cache.get(api)

        if api_data is None:
            return False

        return noteManager.set_field(self.note, self.field, api_data)

    def visit_empty(self) -> bool:
        noteManager.empty_field(self.note, self.field)
        return True

    def visit_note_flag(self, flag: int) -> bool:
        if self.out_flag_ref is not None:
            self.out_flag_ref[0] = flag
        noteManager.set_flag([self.note], flag)
        return False


class MoveAudioFConfVisitor(FConfVisitor):
    """Only for *Pron field to move mp3 files"""

    def __init__(self, word: str, field: str):
        self.word = word
        self.field = field

    def visit_api(self, api: str) -> bool:
        """move file {field}_{word}.mp3 from {system_tmp}/Dict2Anki/audios to anki media dir"""

        fname = misc.audio_fname(self.field, self.word)
        audio_from = os.path.join(misc.tmp_audio_dir(), fname)
        audio_to = noteManager.media_path(fname)

        return misc.mv_file(audio_from, audio_to)

    def visit_empty(self) -> bool:
        return True

    def visit_note_flag(self, flag: int) -> bool:
        return False


class CallbackFConfVisitor(FConfVisitor):
    def __init__(
        self,
        api_callback: T.Optional[T.Callable[[str], bool]] = None,
        empty_callback: T.Optional[T.Callable[..., None]] = None,
        note_flag_callback: T.Optional[T.Callable[[int], None]] = None,
    ):
        self.api_callback = api_callback
        self.empty_callback = empty_callback
        self.note_flag_callback = note_flag_callback

    def visit_api(self, api: str) -> bool:
        if self.api_callback:
            return self.api_callback(api)
        return False

    def visit_empty(self) -> bool:
        if self.empty_callback:
            self.empty_callback()
        return True

    def visit_note_flag(self, flag: int) -> bool:
        if self.note_flag_callback:
            self.note_flag_callback(flag)
        return False


class FConfAST(ABC):
    @abstractmethod
    def eval(self, visitor: FConfVisitor) -> bool:
        pass

    @abstractmethod
    def __str__(self):
        return str('')

    @abstractmethod
    def __repr__(self):
        return self.__str__()


class EmptyFConfAST(FConfAST):
    def eval(self, visitor: FConfVisitor) -> bool:
        return visitor.visit_empty()

    def __str__(self):
        return super().__str__()

    def __repr__(self):
        return super().__repr__()


class AndFConfAST(FConfAST):
    def __init__(self, left: FConfAST, right: FConfAST):
        self.left = left
        self.right = right

    def eval(self, visitor: FConfVisitor) -> bool:
        return self.left.eval(visitor) and self.right.eval(visitor)

    def __str__(self):
        return f'({str(self.left)} & {str(self.right)})'

    def __repr__(self):
        return self.__str__()


class OrFConfAST(FConfAST):
    def __init__(self, left: FConfAST, right: FConfAST):
        self.left = left
        self.right = right

    def eval(self, visitor: FConfVisitor) -> bool:
        return self.left.eval(visitor) or self.right.eval(visitor)

    def __str__(self):
        return f'({self.left}) | ({self.right})'

    def __repr__(self):
        return self.__str__()


class ApiFConfAST(FConfAST):
    def __init__(self, api: str):
        self.api = api

    def eval(self, visitor: FConfVisitor) -> bool:
        return visitor.visit_api(self.api)

    def __str__(self):
        return f'api:{self.api}'

    def __repr__(self):
        return self.__str__()


class NoteFlagFConfAST(FConfAST):
    def __init__(self, flag: int):
        self.flag = flag

    def eval(self, visitor: FConfVisitor) -> bool:
        """always return False"""
        visitor.visit_note_flag(self.flag)
        return False

    def __str__(self):
        return f'flag:{self.flag}'

    def __repr__(self):
        return self.__str__()


class Lexer:
    class Token(IntEnum):
        EOF = -1
        Api = -2
        Flag = -3
        StrVal = -5
        NumVal = -6

    def __init__(self, fc_str: str):
        self.stream = io.StringIO(fc_str)
        self.str_val = ''
        self.num_val = 0

        self.last_char = ' '  # single UTF-8 char, initial value is a space
        self.curr_tok = 0

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def getchar(self):
        """
        read one UTF-8 character
        """
        return self.stream.read(1)

    def close(self):
        self.stream.close()

    def get_next_tok(self):
        self.curr_tok = self.gettok()
        return self.curr_tok

    def gettok(self):
        """
        get token
        """
        # skip whitespace
        while self.last_char.isspace():
            self.last_char = self.getchar()

        if (
            self.last_char
            and not self.last_char.isdigit()
            and self.last_char != ':'
            and self.last_char != '('
            and self.last_char != ')'
            and self.last_char != '&'
            and self.last_char != '|'
            and self.last_char != '"'
        ):
            # string = [^0-9:\(\)&\|"][^: ]*
            chunk = [self.last_char]

            self.last_char = self.getchar()
            while not self.last_char.isspace() and self.last_char != ':':
                chunk.append(self.last_char)
                self.last_char = self.getchar()

            self.str_val = ''.join(chunk)
            if self.str_val == 'api':
                return Lexer.Token.Api
            if self.str_val == 'flag':
                return Lexer.Token.Flag
            return Lexer.Token.StrVal

        if self.last_char.isdigit():
            # Number: [0-9]+
            chunk = [self.last_char]

            self.last_char = self.getchar()
            while self.last_char.isdigit():
                chunk.append(self.last_char)
                self.last_char = self.getchar()

            self.num_val = int(''.join(chunk))
            return Lexer.Token.NumVal

        if self.last_char == '"':
            # double-quote-string
            chunk = []
            while True:
                self.last_char = self.getchar()
                if self.last_char == '':  # EOF
                    break
                if self.last_char == '\\':
                    # read next char as literal
                    self.last_char = self.getchar()
                    if self.last_char == '':  # EOF
                        break
                    chunk.append(self.last_char)
                elif self.last_char == '"':
                    # eat char `"`
                    self.last_char = self.getchar()
                    break
                else:
                    chunk.append(self.last_char)

            self.str_val = ''.join(chunk)
            return Lexer.Token.StrVal

        if self.last_char:
            # unknown char, just return its UTF-8 value
            curr_char = self.last_char
            self.last_char = self.getchar()
            return ord(curr_char)

        return Lexer.Token.EOF


class Parser:
    def __init__(self, lexer: Lexer):
        self.lexer = lexer

    def parse_api_expr(self) -> tuple[T.Optional[ApiFConfAST], str]:
        """
        'api' ':' (string | '"' string '"')
        """
        self.lexer.get_next_tok()  # eat (consume) 'api'

        next_tok = self.lexer.get_next_tok()
        if next_tok != ord(':'):
            return None, 'Error: expect colon `:` after `api`'

        next_tok = self.lexer.get_next_tok()
        if next_tok == Lexer.Token.StrVal:
            api = self.lexer.str_val
            self.lexer.get_next_tok()  # eat
            return ApiFConfAST(api), ''

        return None, 'Error: expect (quoted-)string after `api:`'

    def parse_flag_expr(self) -> tuple[T.Optional[NoteFlagFConfAST], str]:
        """
        'flag' ':' number
        """
        self.lexer.get_next_tok()  # eat 'flag'

        next_tok = self.lexer.get_next_tok()
        if next_tok != ord(':'):
            return None, 'Error, expect colon `:` after `flag`'

        next_tok = self.lexer.get_next_tok()
        if next_tok == Lexer.Token.NumVal:
            self.lexer.get_next_tok()  # eat number
            return NoteFlagFConfAST(self.lexer.num_val), ''

        return None, 'Error: expect number after `flag:`'

    def parse_paren_expr(self) -> tuple[T.Optional[FConfAST], str]:
        """
        '(' expr ')'
        """
        self.lexer.get_next_tok()  # eat '('

        ast, err = self.parse_expr()
        if not ast:
            return ast, err

        if self.lexer.curr_tok != ord(')'):
            return None, 'Error: missing `)` after expression'

        self.lexer.get_next_tok()  # eat ')'
        return ast, err

    def parse_primary(self) -> tuple[T.Optional[FConfAST], str]:
        """
        paren_expr
        api_expr
        flag_expr
        """
        curr_tok = self.lexer.curr_tok
        if curr_tok == ord('('):
            return self.parse_paren_expr()
        elif curr_tok == Lexer.Token.Api:
            return self.parse_api_expr()
        elif curr_tok == Lexer.Token.Flag:
            return self.parse_flag_expr()
        else:
            return None, 'Error: unknown token when expecting an expression'

    def parse_expr(self) -> tuple[T.Optional[FConfAST], str]:
        lhs, err = self.parse_primary()
        if lhs is None:
            return lhs, err

        return self.parse_rhs(lhs)

    def parse_rhs(self, lhs: FConfAST) -> tuple[T.Optional[FConfAST], str]:
        while True:
            op = self.lexer.curr_tok
            if op != ord('&') and op != ord('|'):
                return lhs, ''

            rhs, err = self.parse_primary()
            if rhs is None:
                return rhs, err

            if op == ord('&'):
                lhs = AndFConfAST(lhs, rhs)
            else:
                lhs = OrFConfAST(lhs, rhs)

    def parse(self) -> tuple[T.Optional[FConfAST], str]:
        with self.lexer:
            next_tok = self.lexer.get_next_tok()
            if next_tok == Lexer.Token.EOF:
                return EmptyFConfAST(), ''

            # unknown suffix guard
            ast, err = self.parse_expr()
            if self.lexer.curr_tok != Lexer.Token.EOF:
                return None, 'Error: unexpected pattern after expression'
            return ast, err


def make_ast(fc_str: str) -> tuple[T.Optional[FConfAST], str]:
    """Make AST from field config str.

    Returns: If parse succeed, tuple[0] is not None. If fail, tuple[0] is None,
    and tuple[1] is error message.

    """
    parser = Parser(Lexer(fc_str))
    return parser.parse()


def get_api_set(asts: T.Iterable[FConfAST]) -> set[str]:
    api_set: set[str] = set()

    def api_callback(api: str) -> bool:
        api_set.add(api)
        return False

    for ast in asts:
        ast.eval(CallbackFConfVisitor(api_callback))
    return api_set


def get_invalid_api_set(asts: T.Iterable[FConfAST]) -> set[str]:
    invalid_api_set: set[str] = set()

    for api in get_api_set(asts):
        if not queryApi.apis.get(api):
            invalid_api_set.add(api)
    return invalid_api_set


def ensure_ast_dict_errmsg_for_ui(
    ast_dict: dict[str, tuple[T.Optional[FConfAST], str]],
) -> tuple[dict[str, FConfAST], str]:
    """ensure ASTs are valid (not None and all API valid), Otherwise, return
    empty dict and error message

    """
    msg_chunk = []
    for field, ast_tuple in ast_dict.items():
        if not ast_tuple[0]:
            msg_chunk.append(f'无法解析配置[{field}]：{ast_tuple[1]}\n')
    if invalid_api_set := get_invalid_api_set((ast for ast, _err in ast_dict.values() if ast)):
        msg_chunk.append(f'无法加载模块{invalid_api_set}\n')
    if msg_chunk:
        msg_chunk.append('请检查配置！')
        return ({}, ''.join(msg_chunk))

    return ({field: ast_tuple[0] for field, ast_tuple in ast_dict.items() if ast_tuple[0] is not None}, '')


def eval_asts_set_note(
    word: str,
    note: anki.notes.Note,
    query_cache: dict[str, T.Optional[_T.QueryWordData]],
    ast_dict: dict[str, FConfAST],
    flag_ref: T.Optional[list[int]] = None,
):
    for field, ast in ast_dict.items():
        ast.eval(NoteFConfVisitor(word, field, note, query_cache, flag_ref))
