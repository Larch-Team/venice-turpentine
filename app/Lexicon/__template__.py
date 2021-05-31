"""
Tutaj umieść dokumentację swojego pluginu
"""
import typing as tp
import Lexicon.__utils__ as utils

SOCKET = 'Lexicon'
VERSION = '0.0.1'


def tokenize(statement: str, used_tokens: tp.Iterable[str], defined: dict[str, str] = dict()) -> utils.Sentence:
    pass


def get_lexem(token: str) -> str:
    """Returns the lexem which was used to find the token"""
    pass


def get_type(token: str) -> str:
    """Returns the type of a token"""
    pass


def join_to_string(s: utils.Sentence) -> str:
    """Writes the sentence as a string, where tokens are written as `<[token type]_[lexem]>`"""
    pass


def sign_list(type_: str) -> list[str]:
    """Zwraca listę potencjalnych znaków dla typów zmiennych (sentvar, predicate itp.)"""
    pass