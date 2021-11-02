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
    if len(proof.nodes.children) == 0:
        return ["<p>Jak zacząć? Kliknij główny spójnik i zacznij rozkładać formuły.</p>"]
    try:
        mistakes = proof.check()
    except EngineError:
        mistakes = []
    if mistakes:
        return mistake_check(mistakes[0])
    moves = proof.copy().solve()
    while moves and not moves[0].auto:
        moves.pop(0)
    if moves:
        s = moves[0].get_premisses()['sentenceID']
        return [f"<p>Teraz rozłóż formułę {s.getReadable()}.", "<p><details><summary>Spróbuj zrobić to samodzielnie, a jeśli masz wątpliwości jak to zrobić, kliknij tutaj</summary>", f"Spróbuj rozłożyć spójnik {s.getLexems()[moves[0].context['tokenID']]}</details></p>"]
    else:
        return ['<p>To koniec! Wszystkie formuły są rozłożone. Możesz przejść dalej.</p>']


def hint_start() -> Union[list[str], None]:
    """
    Wykonywana przy rozpoczęciu nowego dowodu

    :return: Lista podpowiedzi, jeden str na odpowiedź
    :rtype: list[str] | None
    """
    return ['Po prostu wpisz formułę, którą chcesz zbadać. Nie musisz jej negować.', 'Powodzenia!']


# Mistake correction

def mistake_userule(mistake: UserMistake) -> Union[list[str], None]:
    """
    Wykonywana przy wywołaniu przez użytkownika pomocy

    :param proof: Aktualny obiekt dowodu
    :type proof: Proof | None
    :return: Lista podpowiedzi, jeden str na odpowiedź
    :rtype: list[str] | None
    """
    if mistake.name == 'already used':
        return ['<p>Ta formuła jest już rozłożona. Wybierz inną.</p>']
    elif mistake.name == 'cannot perform':
        return ['<p>Nie możesz teraz usunąć tej negacji. Najpierw rozłóż inną formułę, później wróć do negacji.</p>']        


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