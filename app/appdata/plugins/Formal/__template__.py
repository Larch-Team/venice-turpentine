"""
Tutaj umieść dokumentację swojego pluginu
"""
import typing as tp
from exceptions import UserMistake
import plugins.Formal.__utils__ as utils
from history import History
from proof import Proof
from sentence import Sentence
from usedrule import UsedRule

SOCKET = 'Formal'
VERSION = '0.4.0'

def generate_formula(length: int, vars: int) -> Sentence:
    f = utils.generate_wff(length, {
        2 : [], # Spójniki jednoargumentowe
        1 : []  # Spójniki dwuargumentowe
    }, vars, '') # Typ zmiennej domyślnej
    assert (p := check_syntax(f)) is None, f"Formuła jest niepoprawna: {p}"
    return f

def get_tags() -> tuple[str]:
    pass

def get_operator_precedence() -> dict[str, int]:
    """Zwraca siłę wiązania danych spójników, im wyższa, tym mocniej wiąże (negacja ma najwyższą przykładowo)"""
    pass


def prepare_for_proving(statement: Sentence) -> Sentence:
    """Przygotowuje zdanie do dowodzenia - czyszczenie, dodawanie elementów"""
    pass


def check_closure(branch: list[Sentence], used: History) -> tp.Union[None, tuple[utils.close.Close, str]]:
    """Sprawdza możliwość zamknięcia gałęzi, zwraca obiekty zamknięcia oraz komunikat do wyświetlenia"""
    pass


def check_syntax(tokenized_statement: Sentence) -> tp.Union[UserMistake, None]:
    """Sprawdza poprawność zapisu tokenizowanego zdania, zwraca informacje o błędach w formule"""
    pass


def get_rules_docs() -> dict[str, str]:
    """Zwraca reguły rachunku z opisem"""
    pass

def get_rules_symbolic() ->  dict[str, str]:
    """Zwraca reguły w formie symbolicznej rachunku z opisem"""
    pass

def get_needed_context(rule_name: str) -> tuple[utils.ContextDef]:
    """Zwraca informacje o wymaganym przez daną regułę kontekście w formie obiektów ContextDef"""
    pass


def solver(proof: Proof) -> bool:
    pass


def checker(rule: UsedRule, conclusion: Sentence) -> tp.Union[UserMistake, None]:
    """
    Na podstawie informacji o użytych regułach i podanym wyniku zwraca informacje o błędach. None wskazuje na poprawność wyprowadzenia wniosku z reguły.
    Konceptualnie przypomina zbiory Hintikki bez reguły o niesprzeczności.
    """
    # Przenieś poniższą funkcję poza checker, tutaj jest umieszczona tylko po to, aby nie naruszać wzorca.
    def find_rule(sentence: Sentence) -> str:
        main, other = sentence.getComponents()
        if main is None:
            return None
        if main.startswith('not_'):
            negated = 'false'
            main, _ = other.getComponents()
        else:
            negated = 'true'

        if main.startswith('not_'):
            return 'double not'
        else:
            return f"{negated} {main.split('_')[0]}"
        
    premiss = rule.get_premisses()['sentenceID']  # Istnieje tylko jedna
    entailed = None #RULES[rule.rule].strict(premiss) # You need to define a rule dictionary
    if conclusion in sum(entailed, []) and find_rule(premiss) == rule.rule:
        return None
    else:
        return f"'{rule.rule}' can't be used on '{premiss.getReadable()}'"

def use_rule(name: str, branch: list[Sentence], used: utils.History, context: dict[str, tp.Any], decisions: dict[str, tp.Any]) -> tuple[utils.SentenceTupleStructure, utils.HistoryTupleStructure, dict[str, tp.Any]]:
    """
    Używa określonej reguły na podanej gałęzi.
    Więcej: https://www.notion.so/szymanski/Gniazda-w-Larchu-637a500c36304ee28d3abe11297bfdb2#98e96d34d3c54077834bc0384020ff38

    :param name: Nazwa używanej reguły, listę można uzyskać z pomocą Formal.get_rules_docs()
    :type name: str
    :param branch: Lista zdań w gałęzi, na której została użyta reguła
    :type branch: list[Sentence]
    :param used: Obiekt historii przechowujący informacje o już rozłożonych zdaniach
    :type used: utils.History
    :param context: kontekst wymagany do zastosowania reguły, listę można uzyskać z pomocą Formal.get_needed_context(rule)
        Kontekst reguł: https://www.notion.so/szymanski/Zarz-dzanie-kontekstem-regu-2a5abea2a1bc492e8fa3f8b1c046ad3a
    :type context: dict[str, tp.Any]
    :param decisions: Zbiór podjętych przez program decyzji (mogą być czymkolwiek), które nie wynikają deterministycznie z przesłanek, używane jest do odtworzenia reguł przy wczytywaniu dowodu.
    :type decisions: dict[str, Any]
    :return: Struktura krotek, reprezentująca wynik reguły oraz strukturę reprezentującą operacje do wykonania na zbiorze zamknięcia.
        Struktury krotek: https://www.notion.so/szymanski/Reprezentacja-dowod-w-w-Larchu-cd36457b437e456a87b4e0c2c2e38bd5#014dccf44246407380c4e30b2ea598a9
        Zamykanie gałęzi: https://www.notion.so/szymanski/Zamykanie-ga-zi-53249279f1884ab4b6f58bbd6346ec8d
    :rtype: tuple[tp.Union[tuple[tuple[Sentence]], None], tp.Union[tuple[tuple[tp.Union[int, Callable, Sentence]]], None]]
    """
    pass
