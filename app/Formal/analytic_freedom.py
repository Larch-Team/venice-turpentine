"""
Tutaj umieść dokumentację swojego pluginu
"""
import typing as tp
import Formal.__utils__ as utils

SOCKET = 'Formal'
VERSION = '0.2.0'

PRECEDENCE = {
    'and':3,
    'or':3,
    'imp':2,
    'not':4
}

def get_operator_precedence() -> dict[str, int]:
    """Zwraca siłę wiązania danych spójników, im wyższa, tym mocniej wiąże (negacja ma najwyższą przykładowo)"""
    return PRECEDENCE

def prepare_for_proving(statement: utils.Sentence) -> utils.Sentence:
    """Przygotowuje zdanie do dowodzenia - czyszczenie, dodawanie elementów"""
    return utils.add_prefix(statement, 'not', "~")


def check_closure(branch: list[utils.Sentence], used: set[tuple[str]]) -> tp.Union[None, tuple[utils.close.Close, str]]:
    """Sprawdza możliwość zamknięcia gałęzi, zwraca obiekty zamknięcia oraz komunikat do wyświetlenia"""
    return None


### SYNTAX CHECKING

def synchk_transcribe(sentence):
    s = []
    for el in sentence:
        if el in ['(', ')']:
            s.append(el)
        else:
            elem = el.split('_')
            if elem[0] == 'sentvar':
                s.append("s")
            elif elem[0] == 'not':
                s.append("1")
            elif elem[0] in ('and', 'or', 'imp'):
                s.append("2")
    return "".join(s)


def special_replace(string, old, new, index_list):
    while string.find(old) != -1:
        a = string.find(old)
        string = string.replace(old, new, 1)
        del index_list[a:a+len(old)]
        index_list.insert(a, None)
    return string, index_list


def reduce_(sentence):
    prev_sentence = ''
    sentence = synchk_transcribe(sentence)
    indexes = list(range(len(sentence)))
    while prev_sentence != sentence:
        prev_sentence = sentence
        for to_replace in ('1s', 's2s', '(s)'):
            sentence, indexes = special_replace(sentence, to_replace, "s", indexes)
    return sentence, indexes


def find_all(a_str, sub):
    start = 0
    while True:
        start = a_str.find(sub, start)
        if start == -1:
            return
        yield start
        start += len(sub)


def check_syntax(sentence: utils.Sentence) -> tp.Union[str, None]:
    """Sprawdza poprawność zapisu tokenizowanego zdania, zwraca informacje o błędach w formule"""
    reduced, indexes = reduce_(sentence)
    if reduced == 's':
        # ok
        return None
    if 's' not in reduced:
        return 'Zdanie nie zawiera żadnych zmiennych'

    if 'ss' in reduced:
        return 'W zdaniu znajdują się dwie zmienne lub formuły niepołączone spójnikiem'

    if '(' in reduced:
        errors = find_all(reduced, '(')
        for er in errors:
            return f'Otwarcie nawiasu na pozycji {indexes[er]+1} nie ma zamknięcia'

    if ')' in reduced:
        errors = find_all(reduced, '(')
        for er in errors:
            return f'Zamknięcie nawiasu na pozycji {indexes[er]+1} nie ma otwarcia'

    if 's2' in reduced:
        errors = find_all(reduced, 's2')
        for er in errors:
            return f'Spójnik dwuargumentowy na pozycji {indexes[er]+2} nie ma prawego argumentu'

    if '2s' in reduced:
        errors = find_all(reduced, '2s')
        for er in errors:
            return f'Spójnik dwuargumentowy na pozycji {indexes[er]+1} nie ma lewego argumentu'
    raise Exception('Zdanie nie jest poprawne')


### TEMPLATE CIĄG DALSZY

def get_rules() -> dict[str, str]:
    """Zwraca reguły rachunku z opisem"""
    pass


def get_needed_context(rule_name: str) -> tuple[utils.ContextDef]:
    """Zwraca informacje o wymaganym przez daną regułę kontekście w formie obiektów ContextDef"""
    return [
        utils.ContextDef(
            variable='sentenceID', 
            official='Sentence Number', 
            docs='The number of the sentence in this branch', 
            type_='sentenceID'),
        utils.ContextDef(
            variable='tokenID', 
            official='Token Number', 
            docs='The index of a token in a sentence', 
            type_=int)
    ]


def get_used_types() -> tuple[str]:
    pass


def use_rule(name: str, branch: list[utils.Sentence], used: utils.History, context: dict[str, tp.Any], decisions: dict[str, tp.Any]) -> tuple[utils.SentenceTupleStructure, utils.HistoryTupleStructure, dict[str, tp.Any]]:
    """
    Używa określonej reguły na podanej gałęzi.
    Więcej: https://www.notion.so/szymanski/Gniazda-w-Larchu-637a500c36304ee28d3abe11297bfdb2#98e96d34d3c54077834bc0384020ff38

    :param name: Nazwa używanej reguły, listę można uzyskać z pomocą Formal.get_rules()
    :type name: str
    :param branch: Lista zdań w gałęzi, na której została użyta reguła
    :type branch: list[utils.Sentence]
    :param used: Obiekt historii przechowujący informacje o już rozłożonych zdaniach
    :type used: utils.History
    :param context: kontekst wymagany do zastosowania reguły, listę można uzyskać z pomocą Formal.get_needed_context(rule)
        Kontekst reguł: https://www.notion.so/szymanski/Zarz-dzanie-kontekstem-regu-2a5abea2a1bc492e8fa3f8b1c046ad3a
    :type context: dict[str, tp.Any]
    :param auto: , defaults to False
    :type auto: bool, optional
    :return: Struktura krotek, reprezentująca wynik reguły oraz strukturę reprezentującą operacje do wykonania na zbiorze zamknięcia.
        Struktury krotek: https://www.notion.so/szymanski/Reprezentacja-dowod-w-w-Larchu-cd36457b437e456a87b4e0c2c2e38bd5#014dccf44246407380c4e30b2ea598a9
        Zamykanie gałęzi: https://www.notion.so/szymanski/Zamykanie-ga-zi-53249279f1884ab4b6f58bbd6346ec8d
    :rtype: tuple[tp.Union[tuple[tuple[utils.Sentence]], None], tp.Union[tuple[tuple[tp.Union[int, Callable, utils.Sentence]]], None]]
    """
