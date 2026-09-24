from addon.adv_conf import (
    AndFConfAST,
    ApiFConfAST,
    CallbackFConfVisitor,
    EmptyFConfAST,
    Lexer,
    NoteFlagFConfAST,
    OrFConfAST,
    Parser,
)


def test_lexer_tok_api():
    s = ' \napi\n '
    lexer = Lexer(s)
    tok = lexer.get_next_tok()

    assert tok == Lexer.Token.Api
    assert lexer.get_next_tok() == Lexer.Token.EOF


def test_lexer_tok_flag():
    s = ' \nflag\n '
    lexer = Lexer(s)
    tok = lexer.get_next_tok()

    assert tok == Lexer.Token.Flag
    assert lexer.get_next_tok() == Lexer.Token.EOF


def test_lexer_tok_colon():
    s = ' \n:\n '
    lexer = Lexer(s)
    tok = lexer.get_next_tok()

    assert tok == ord(':')
    assert lexer.get_next_tok() == Lexer.Token.EOF


def test_lexer_tok_number():
    s = ' \n100\n '
    lexer = Lexer(s)
    tok = lexer.get_next_tok()

    assert tok == lexer.Token.NumVal
    assert 100 == lexer.num_val
    assert lexer.get_next_tok() == Lexer.Token.EOF


def test_lexer_tok_unquoted_str():
    """
    One ore more continuous characters:
    first char: not empty and not digit and not one of `:()&|"`,
    second and subsequent: not empty and not `:` and not whitespace
    """
    s = '_0_0_!@&'
    lexer = Lexer(s)
    tok = lexer.get_next_tok()

    assert tok == Lexer.Token.StrVal
    assert lexer.str_val == '_0_0_!@'
    assert lexer.get_next_tok() == ord('&')

    # single character string
    s = '\n @ 0'
    lexer = Lexer(s)
    tok = lexer.get_next_tok()

    assert tok == lexer.Token.StrVal
    assert lexer.str_val == '@'
    assert lexer.get_next_tok() == Lexer.Token.NumVal


def test_lexer_tok_quoted_str():
    s = '\\"*()^^(()^) '
    quoted = '"' + s + '"'
    lexer = Lexer(quoted)
    tok = lexer.get_next_tok()

    assert tok == lexer.Token.StrVal
    assert lexer.str_val == '"*()^^(()^) '

    # EOF without ending `"`
    quoted = '"' + s
    lexer = Lexer(quoted)
    tok = lexer.get_next_tok()

    assert tok == lexer.Token.StrVal
    assert lexer.str_val == '"*()^^(()^) '
    assert lexer.get_next_tok() == Lexer.Token.EOF


def test_lexer_tok_paren():
    s = ' \n)(\n '
    lexer = Lexer(s)
    tok = lexer.get_next_tok()

    assert tok == ord(')')
    assert lexer.get_next_tok() == ord('(')
    assert lexer.get_next_tok() == Lexer.Token.EOF


def test_parser_api():
    s = 'api:hello'
    parser = Parser(Lexer(s))
    ast, err = parser.parse()

    assert isinstance(ast, ApiFConfAST)
    assert str(ast) == s


def test_parser_api_quoted():
    s = 'api:"hello world"'
    parser = Parser(Lexer(s))
    ast, err = parser.parse()

    assert isinstance(ast, ApiFConfAST)
    assert str(ast) == 'api:hello world'


def test_parser_api_error():
    s = 'api::'
    parser = Parser(Lexer(s))
    ast, err = parser.parse()

    assert ast is None and err


def test_parser_flag():
    s = 'flag:1'
    parser = Parser(Lexer(s))
    ast, err = parser.parse()

    assert isinstance(ast, NoteFlagFConfAST)
    assert str(ast) == s


def test_parser_flag_error():
    s = 'flag:abc'
    parser = Parser(Lexer(s))
    ast, err = parser.parse()

    assert ast is None and err


def test_parser_empty():
    s = ' \n\n '
    parser = Parser(Lexer(s))
    ast, err = parser.parse()

    assert isinstance(ast, EmptyFConfAST)


def test_parser_paren():
    s = 'api:world'
    paren_s = '(' + s + ')'
    parser = Parser(Lexer(paren_s))
    ast, err = parser.parse()

    assert isinstance(ast, ApiFConfAST)
    assert str(ast) == s


def test_parser_and_or():
    s = ' \n(api:"hello world" & api:meow | flag:123) | (flag:321 | api:hello_world)\n '
    parser = Parser(Lexer(s))
    ast, err = parser.parse()

    assert isinstance(ast, OrFConfAST)
    assert str(ast) == '(((api:hello world & api:meow) | flag:123) | (flag:321 | api:hello_world))'


def test_parser_unknown_prefix():
    s = ' \n123\n flag:123'
    parser = Parser(Lexer(s))
    ast, err = parser.parse()

    assert ast is None and err


def test_parser_unknown_suffix():
    s = 'api:api222 "today is a good day"'
    parser = Parser(Lexer(s))
    ast, err = parser.parse()

    assert ast is None and err


def test_ast_empty():
    called = 0

    def callback():
        nonlocal called
        called = 1

    visitor = CallbackFConfVisitor(empty_callback=callback)
    ast = EmptyFConfAST()
    ast.eval(visitor)

    assert called == 1


def test_ast_eval_api():
    api_: str = ''

    def callback(api: str) -> bool:
        nonlocal api_
        api_ = api
        return True

    visitor = CallbackFConfVisitor(api_callback=callback)
    ast = ApiFConfAST('test')
    ast.eval(visitor)

    assert api_ == 'test'


def test_ast_eval_flag():
    flag_ = 0

    def callback(flag: int):
        nonlocal flag_
        flag_ = flag

    visitor = CallbackFConfVisitor(note_flag_callback=callback)
    ast = NoteFlagFConfAST(1)
    ast.eval(visitor)

    assert flag_ == 1


def test_ast_eval_l_or_r():
    """test AST with form (ast OR ast)"""
    # case 1: all return true
    # only the first AST should be evaluated

    api_1 = ''

    def callback_1(api: str) -> bool:
        nonlocal api_1
        api_1 += api
        return True

    ast_l = ApiFConfAST('l_')
    ast_r = ApiFConfAST('r_')
    ast_or = OrFConfAST(ast_l, ast_r)
    b = ast_or.eval(CallbackFConfVisitor(api_callback=callback_1))

    assert b is True
    assert api_1 == 'l_'

    # case 2: all return false
    # all ASTs should be evaluated

    api_2 = ''

    def callback_2(api: str) -> bool:
        nonlocal api_2
        api_2 += api
        return False

    ast_l = ApiFConfAST('l_')
    ast_r = ApiFConfAST('r_')
    ast_or = OrFConfAST(ast_l, ast_r)
    b = ast_or.eval(CallbackFConfVisitor(api_callback=callback_2))

    assert b is False
    assert api_2 == 'l_r_'


def test_ast_eval_ll_or_lr_or_r():
    """test AST with form ((ast OR ast) OR ast)"""

    # case 1: all return true
    # only the AST should be evaluated

    api_1 = ''

    def make_ast_():
        ast_ll = ApiFConfAST('ll_')
        ast_lr = ApiFConfAST('lr_')
        ast_or_l = OrFConfAST(ast_ll, ast_lr)
        ast_r = ApiFConfAST('r_')
        ast_or = OrFConfAST(ast_or_l, ast_r)
        return ast_or

    def callback_1(api: str) -> bool:
        nonlocal api_1
        api_1 += api
        return True

    ast_or = make_ast_()
    b = ast_or.eval(CallbackFConfVisitor(api_callback=callback_1))

    assert b is True
    assert api_1 == 'll_'

    # case 2: all return false
    # all ASTs should be evaluated

    api_2 = ''

    def callback_2(api: str) -> bool:
        nonlocal api_2
        api_2 += api
        return False

    ast_or = make_ast_()
    b = ast_or.eval(CallbackFConfVisitor(api_callback=callback_2))

    assert b is False
    assert api_2 == 'll_lr_r_'


def test_ast_eval_l_and_rl_or_rr():
    """test AST with form (ast AND (ast OR ast))"""

    # case 1: all return true
    # only left and left of right should be evaluated

    api_1 = ''

    def make_ast_():
        ast_l = ApiFConfAST('l_')
        ast_rl = ApiFConfAST('rl_')
        ast_rr = ApiFConfAST('rr_')
        ast_or_r = OrFConfAST(ast_rl, ast_rr)
        ast_and = AndFConfAST(ast_l, ast_or_r)
        return ast_and

    def callback_1(api: str) -> bool:
        nonlocal api_1
        api_1 += api
        return True

    ast_and = make_ast_()
    b = ast_and.eval(CallbackFConfVisitor(api_callback=callback_1))

    assert b is True
    assert api_1 == 'l_rl_'

    # case 2: all return false
    # only the first AST should be evaluated

    api_2 = ''

    def callback_2(api: str) -> bool:
        nonlocal api_2
        api_2 += api
        return False

    ast_and = make_ast_()
    b = ast_and.eval(CallbackFConfVisitor(api_callback=callback_2))

    assert b is False
    assert api_2 == 'l_'
