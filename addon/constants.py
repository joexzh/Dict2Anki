VERSION = 'v7.2.4'
RELEASE_URL = 'https://github.com/joexzh/Dict2Anki'
VERSION_CHECK_API = 'https://api.github.com/repos/joexzh/Dict2Anki/releases/latest'
ADDON_NAME = 'Dict2Anki-ng'
ADDON_FULL_NAME = f'{ADDON_NAME}-{VERSION}'
MODEL_NAME = ADDON_NAME # 若不兼容旧模板，需要修改模板名称

F_DEFINITION = 'definition'
F_SENTENCE = 'sentence'
F_SENTENCE_FRONT = 'sentenceFront'
F_SENTENCE_BACK = 'sentenceBack'
F_PHRASE = 'phrase'
F_PHRASE_FRONT = 'phraseFront'
F_PHRASE_BACK = 'phraseBack'
F_IMAGE = 'image'
F_BREPHONETIC = 'BrEPhonetic' # 英式音标
F_AMEPHONETIC = 'AmEPhonetic' # 美式音标
F_BREPRON = 'BrEPron' # 英式发音
F_AMEPRON = 'AmEPron' # 美式发音
F_NOPRON = 'noPron'
F_TERM = 'term'
F_CONGEST = 'congest' # 限流

BASIC_OPTION = [F_DEFINITION, F_SENTENCE, F_PHRASE, F_IMAGE, F_BREPHONETIC, F_AMEPHONETIC]  # 顺序和名称不可修改
EXTRA_OPTION = [F_BREPRON, F_AMEPRON, F_NOPRON]  # 顺序和名称不可修改
MODEL_FIELDS = [F_TERM, F_DEFINITION, F_SENTENCE_FRONT, F_SENTENCE_BACK, F_PHRASE_FRONT, F_PHRASE_BACK, F_IMAGE, F_BREPHONETIC, F_AMEPHONETIC, F_BREPRON, F_AMEPRON]  # 名称不可修改

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36'