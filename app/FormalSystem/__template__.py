"""
Tutaj umieść dokumentację swojego pluginu
"""
import typing as tp
import FormalSystem.__utils__ as utils

SOCKET = 'FormalSystem'
VERSION = '0.0.1'


def get_operator_precedence() -> dict[str, int]:
    """Zwraca siłę wiązania danych spójników, im wyższa, tym mocniej wiąże (negacja ma najwyższą przykładowo)"""
    pass


def prepare_for_proving(statement: utils.Sentence) -> utils.Sentence:
    """Przygotowuje zdanie do dowodzenia - czyszczenie, dodawanie elementów"""
    pass


def check_closure(branch: list[utils.Sentence], used: set[tuple[str]]) -> tp.Union[None, tuple[utils.close.Close, str]]:
    """Sprawdza możliwość zamknięcia gałęzi, zwraca obiekty zamknięcia oraz komunikat do wyświetlenia"""
    pass


def check_syntax(tokenized_statement: utils.Sentence) -> tp.Union[str, None]:
    """Sprawdza poprawność zapisu tokenizowanego zdania, zwraca informacje o błędach w formule"""
    pass


def get_rules() -> dict[str, str]:
    """Zwraca reguły rachunku z opisem"""
    pass


def get_needed_context(rule_name: str) -> tuple[utils.ContextDef]:
    """Zwraca informacje o wymaganym przez daną regułę kontekście w formie obiektów ContextDef"""
    pass


def get_used_types() -> tuple[str]:
    pass


def use_rule(name: str, branch: list[utils.Sentence], used: utils.History, context: dict[str, tp.Any], auto: bool) -> tuple[tp.Union[tuple[tuple[utils.Sentence]], None], tp.Union[tuple[tuple[tp.Union[int, callable, utils.Sentence]]], None]]:
    """
    Używa określonej reguły na podanej gałęzi.
    Więcej: https://www.notion.so/szymanski/Gniazda-w-Larchu-637a500c36304ee28d3abe11297bfdb2#98e96d34d3c54077834bc0384020ff38

    :param name: Nazwa używanej reguły, listę można uzyskać z pomocą FormalSystem.get_rules()
    :type name: str
    :param branch: Lista zdań w gałęzi, na której została użyta reguła
    :type branch: list[utils.Sentence]
    :param used: Obiekt historii przechowujący informacje o już rozłożonych zdaniach
    :type used: utils.History
    :param context: kontekst wymagany do zastosowania reguły, listę można uzyskać z pomocą FormalSystem.get_needed_context(rule)
        Kontekst reguł: https://www.notion.so/szymanski/Zarz-dzanie-kontekstem-regu-2a5abea2a1bc492e8fa3f8b1c046ad3a
    :type context: dict[str, tp.Any]
    :param auto: , defaults to False
    :type auto: bool, optional
    :return: Struktura krotek, reprezentująca wynik reguły oraz strukturę reprezentującą operacje do wykonania na zbiorze zamknięcia.
        Struktury krotek: https://www.notion.so/szymanski/Reprezentacja-dowod-w-w-Larchu-cd36457b437e456a87b4e0c2c2e38bd5#014dccf44246407380c4e30b2ea598a9
        Zamykanie gałęzi: https://www.notion.so/szymanski/Zamykanie-ga-zi-53249279f1884ab4b6f58bbd6346ec8d
    :rtype: tuple[tp.Union[tuple[tuple[utils.Sentence]], None], tp.Union[tuple[tuple[tp.Union[int, callable, utils.Sentence]]], None]]
    """
    pass
