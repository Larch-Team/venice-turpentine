from article import Article
from exceptions import EngineError, UserMistake
from proof import Proof
from typing import Union
from misc import get_plugin_path


SOCKET = 'Assistant'
VERSION = '0.0.1'

articles = Article.read(get_plugin_path(__file__, 'articles'),
                        'Baza wiedzy.html'                        
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
        return mistake_check(mistakes[0]) or mistakes[0].default
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
    if mistake.name == 'wrong rule':
        return [f'<p>Nie możesz użyć wybranej reguły dla formuły {mistake.additional["premiss"].getReadable()}. Wybierz inną regułę.</p>']
    elif mistake.name == 'wrong precedense':
        return [f'<p>Nie możesz rozłożyć formuły {mistake.additional["premiss"].getReadable()} w ten sposób. Wybierz inny spójnik.</p>']


def mistake_syntax(mistake: UserMistake) -> Union[list[str], None]:
    """
    Wywoływany do interpretacji błędu zwróconego przez socket Formal podczas sprawdzania syntaksu

    :param mistake: Obiekt popełnionego błędu
    :type mistake: UserMistake
    :return: Lista podpowiedzi, jeden str na odpowiedź
    :rtype: list[str] | None
    """
    if mistake.name == 'no variables':
        return ['<p>Zdanie nie zawiera żadnych zmiennych. Sprawdź, czy Twoja formuła ma zmienne (np. p, a, x) i spójniki logiczne (np. and, or, implikacja).</p>']
    elif mistake.name == 'nothing between formulas':
        return ['<p>W zdaniu znajdują się dwie zmienne lub formuły niepołączone spójnikiem. Sprawdź, czy między każdą parą zmiennych znajduje się spójnik.</p>']
    elif mistake.name == 'bracket left open':
        return ['<p>Brakuje prawego nawiasu. Popraw formułę.</p>']
    elif mistake.name == 'bracket not opened':
        return ['<p>Brakuje lewego nawiasu. Popraw formułę.</p>']
    elif mistake.name == 'no right':
        return ['<p>Brakuje drugiej zmiennej dla spójnika and, or, lub implikacji, który wymaga dwóch argumentów. Popraw formułę.</p>']
    elif mistake.name == 'no left':
        return ['<p>Brakuje pierwszej zmiennej dla spójnika and, or, lub implikacji, który wymaga dwóch argumentów. Popraw formułę.</p>']
    elif mistake.name == 'no sign symbols':
        return ['<p>Wpisz tylko formułę, którą chcesz udowodnić, bez symboli sygnowania (T, F)</p>']