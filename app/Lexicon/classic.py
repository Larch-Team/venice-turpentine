"""
Transkrypcja basic.py na nowy format definicji języka
"""
import Lexicon.__utils__ as utils

SOCKET = 'Lexicon'
VERSION = '0.0.1'

Lex = utils.Lexicon()

with utils.use_language('propositional'):
    with utils.use_language('uses negation'):
        Lex['not'] = 'not', '~', r'\!'
    Lex['and'] = 'oraz', 'and', r'\^', '&'
    Lex['or'] = 'lub', 'or', r'\|', 'v'
    Lex['imp'] = 'imp', '->'
    with utils.find_new():
        Lex['sentvar'] = r'[a-z]'
    with utils.no_generation():
        Lex['sentvar'] = r'\w+'

with utils.use_language('predicate'):
    Lex['forall'] = 'forall', '/\\', 'A'
    Lex['exists'] = 'exists', '\\/', 'E'
    with utils.find_new():
        Lex['constant'] = r'[a-t]', r'\d'
        Lex['indvar'] = r'[u-z]'
        Lex['predicate'] = r'[P-Z]'
        Lex['function'] = r'[F-O]'

with utils.use_language('sequent calculus'):
    Lex['turnstile'] = '=>', '|-'
    Lex['sep'] = ';'
    Lex['falsum'] = 'bot', 'F'


def get_lexicon() -> utils.Lexicon:
    return Lex