from article import Article
from exceptions import EngineError, UserMistake
from proof import Proof
from typing import Union
from misc import get_plugin_path


SOCKET = 'Assistant'
VERSION = '0.0.1'

articles = Article.read(get_plugin_path(__file__, 'articles'),
                        'main.html'                        
)

# Knowledge base

def get_articles() -> dict[str, Article]:
    """
    Return all of the articles with their names as keys
    """
    return articles


# Hints

def hint_command(proof: Union[Proof, None]) -> Union[list[str], None]:
    """
    Wykonywana przy wywołaniu przez użytkownika pomocy.
    Proof to faktyczny dowód, zachowaj ostrożność.

    :param proof: Aktualny obiekt dowodu
    :type proof: Proof | None
    :return: Lista podpowiedzi, jeden str na odpowiedź
    :rtype: list[str] | None
    """
    try:
        mistakes = proof.check()
    except EngineError:
        mistakes = []
    if mistakes:
        return mistake_check(mistakes[0])
    moves = proof.copy().solve()
    if moves:
        return [articles['main']['rule'], f"Spójrz na zdanie: <code>{moves[0].get_premisses()['sentenceID']}</code>"]
    else:
        return ['To koniec brachu']


def hint_start() -> Union[list[str], None]:
    """
    Wykonywana przy rozpoczęciu nowego dowodu

    :return: Lista podpowiedzi, jeden str na odpowiedź
    :rtype: list[str] | None
    """
    return [articles['main']['start_text'], "Powodzenia!"]


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