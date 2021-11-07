"""
Transkrypcja basic.py na nowy format definicji języka
"""
from plugins.Lexicon.__utils__ import *

SOCKET = 'Lexicon'
VERSION = '0.0.1'

Lex = Lexicon()

with use_language('signed'):
    Lex['signtrue'] = 'T'
    Lex['signfalse'] = 'F'

with use_language('propositional'):
    with use_language('uses negation'):
        Lex['not'] = 'not', '~', r'\!'
    Lex['and'] = 'oraz', 'and', r'\^', '&'
    Lex['or'] = 'lub', 'or', r'\|', 'v'
    Lex['imp'] = 'imp', '->'
    with find_new():
        Lex['sentvar'] = r'[a-z]'
    with no_generation():
        Lex['sentvar'] = r'\w+'

with use_language('predicate'):
    Lex['forall'] = 'forall', '/\\', 'A'
    Lex['exists'] = 'exists', '\\/', 'E'
    with find_new():
        Lex['constant'] = r'[a-t]', r'\d'
        Lex['indvar'] = r'[u-z]'
        Lex['predicate'] = r'[P-Z]'
        Lex['function'] = r'[F-O]'

with use_language('sequent calculus'):
    Lex['turnstile'] = r'=>', r'\|-'
    Lex['sep'] = ';'
    Lex['falsum'] = 'bot', 'F'


def get_lexicon() -> Lexicon:
    return Lex