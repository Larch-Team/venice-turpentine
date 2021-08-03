from article import Article
from exceptions import UserMistake
from proof import Proof
from typing import Union

SOCKET = 'Assistant'
VERSION = '0.0.1'


# Knowledge base

def get_articles() -> dict[str, Article]:
    """
    Return all of the articles with their names as keys
    """
    return {}


# Hints

def hint_command(proof: Union[Proof, None]) -> Union[list[str], None]:
    """
    Wykonywana przy wywołaniu przez użytkownika pomocy.
    Proof to faktyczna kopia dowodu, zachowaj ostrożność.

    :param proof: Aktualny obiekt dowodu
    :type proof: Proof | None
    :return: Lista podpowiedzi, jeden str na odpowiedź
    :rtype: list[str] | None
    """
    pass


def hint_start() -> Union[list[str], None]:
    """
    Wykonywana przy rozpoczęciu nowego dowodu

    :return: Lista podpowiedzi, jeden str na odpowiedź
    :rtype: list[str] | None
    """
    return ["<b>Logika -> Psychika</b>", "Powodzenia!"]


# Mistake correction

def mistake_userule(mistake: UserMistake) -> Union[list[str], None]:
    """
    Wykonywana przy wywołaniu przez użytkownika pomocy

    :param proof: Aktualny obiekt dowodu
    :type proof: Proof | None
    :return: Lista podpowiedzi, jeden str na odpowiedź
    :rtype: list[str] | None
    """
    pass


def mistake_check(mistake: UserMistake) -> Union[list[str], None]:
    """
    Wywoływany do interpretacji błędu zwróconego przez socket Formal podczas sprawdzania dowodu

    :param mistake: Obiekt popełnionego błędu
    :type mistake: UserMistake
    :return: Lista podpowiedzi, jeden str na odpowiedź
    :rtype: list[str] | None
    """
    pass


def mistake_syntax(mistake: UserMistake) -> Union[list[str], None]:
    """
    Wywoływany do interpretacji błędu zwróconego przez socket Formal podczas sprawdzania syntaksu

    :param mistake: Obiekt popełnionego błędu
    :type mistake: UserMistake
    :return: Lista podpowiedzi, jeden str na odpowiedź
    :rtype: list[str] | None
    """
    pass