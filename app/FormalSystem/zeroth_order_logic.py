"""
Tabele analityczne KRZ w stylizacji Smullyana bez formuł sygnowanych.
"""
import typing as tp
import FormalSystem.__utils__ as utils

SOCKET = 'FormalSystem'
VERSION = '0.0.1'


# Rule definition

USED_TYPES = ('and', 'or', 'imp', 'not', 'sentvar')
PRECEDENCE = {
    'and':3,
    'or':3,
    'imp':2,
    'not':4
}

def red_neg(x):
    return utils.reduce_prefix(x, 'not', PRECEDENCE)

RULES = {
    'true and': utils.Rule(
        symbolic="A and B / A; B",
        docs="Rozkładanie prawdziwej koniunkcji. Wymaga wskazania zdania w gałęzi.",
        func=lambda x: utils.strip_around(x, 'and', False, PRECEDENCE),
        context = None,
        reusable=False
    ),
    'false and': utils.Rule(
        symbolic="~(A and B) / ~A | ~B",
        docs="Rozkładanie fałszywej koniunkcji. Wymaga wskazania zdania w gałęzi.",
        func=lambda x: utils.add_prefix(utils.strip_around(
            red_neg(x), 'and', True, PRECEDENCE), 'not', '~'),
        context = None,
        reusable=False
    ),
    'false or': utils.Rule(
        symbolic="~(A or B) / ~A; ~B",
        docs="Rozkładanie fałszywej alternatywy. Wymaga wskazania zdania w gałęzi.",
        func=lambda x: utils.add_prefix(utils.strip_around(
            red_neg(x), 'or', False, PRECEDENCE), 'not', '~'),
        context = None,
        reusable=False
    ),
    'true or': utils.Rule(
        symbolic="(A or B) / A | B",
        docs="Rozkładanie prawdziwej alternatywy. Wymaga wskazania zdania w gałęzi.",
        func=lambda x: utils.strip_around(x, 'or', True, PRECEDENCE),
        context = None,
        reusable=False
    ),
    'false imp': utils.Rule(
        symbolic="~(A -> B) / A; ~B",
        docs="Rozkładanie fałszywej implikacji. Wymaga wskazania zdania w gałęzi.",
        func=lambda x: utils.select(utils.strip_around(red_neg(x),'imp', False, PRECEDENCE), ((False, True),), lambda y: utils.add_prefix(y, 'not', '~')),
        context = None,
        reusable=False
    ),
    'true imp': utils.Rule(
        symbolic="(A -> B) / ~A | B",
        docs="Rozkładanie prawdziwej implikacji. Wymaga wskazania zdania w gałęzi.",
        func=lambda x: utils.select(utils.strip_around(x, 'imp', True, PRECEDENCE), ((True,), (False,)), lambda y: utils.add_prefix(y, 'not', '~')),
        context = None,
        reusable=False
    ),
    'double not': utils.Rule(
        symbolic="~~A / A",
        docs="Usuwanie podwójnej negacji. Wymaga wskazania zdania w gałęzi.",
        func=lambda x: utils.reduce_prefix(
            utils.reduce_prefix(utils.empty_creator(x), 'not', PRECEDENCE), 'not', PRECEDENCE),
        context = None,
        reusable=False
    )
}


# __template__

@utils.cleaned
def prepare_for_proving(statement: utils.Sentence) -> utils.Sentence:
    """Przygotowuje zdanie do dowodzenia - czyszczenie, dodawanie elementów"""
    return statement


def check_closure(branch: list[utils.Sentence], used: set[tuple[str]]) -> tp.Union[None, tuple[utils.close.Close, str]]:
    """Sprawdza możliwość zamknięcia gałęzi, zwraca obiekty zamknięcia oraz komunikat do wyświetlenia"""
    for num1, statement_1 in enumerate(branch):
        for num2, statement_2 in enumerate(branch):
            if statement_1[0].startswith('not') and not statement_2[0].startswith('not'):
                negated, statement = statement_1, statement_2
            elif statement_2[0].startswith('not') and not statement_1[0].startswith('not'):
                negated, statement = statement_2, statement_1
            else:
                continue

            if utils.reduce_prefix(negated, 'not', PRECEDENCE) == statement:
                return utils.close.Contradiction(sentID1 = num1, sentID2=num2), "Sentences contradict. The branch was closed."

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

def get_rules() -> dict[str, str]:
    """Zwraca reguły rachunku z opisem"""
    return {
        name: "\n".join((rule.symbolic, rule.docs))
        for name, rule in RULES.items()
    }


def get_used_types() -> tuple[str]:
    return USED_TYPES


def use_rule(name: str, branch: list[utils.Sentence], used: utils.History, context: dict[str, tp.Any], auto: bool = False) -> tuple[tp.Union[tuple[tuple[utils.Sentence]], None], tp.Union[tuple[tuple[tp.Union[int, callable, utils.Sentence]]], None]]:
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
    
    rule = RULES[name]
    statement_ID = context['sentenceID']

    # Sentence getting
    if statement_ID < 0 or statement_ID > len(branch)-1:
        raise utils.FormalSystemError("No such sentence")

    tokenized_statement = branch[statement_ID]

    if not rule.reusable and tokenized_statement in used: # Used sentence filtering
        raise utils.FormalSystemError("This sentence was already used in a non-reusable rule")

    # Rule usage
    fin = rule.func(tokenized_statement)
    if fin:
        return fin, len(fin)*([[0]] if rule.reusable else [[tokenized_statement]])
    else:
        return None, None


def get_needed_context(rule_name: str) -> tuple[utils.ContextDef]:
    """Zwraca informacje o wymaganym przez daną regułę kontekście w formie obiektów ContextDef"""
    return tuple([utils.ContextDef(variable='sentenceID', official='Sentence Number', docs='The number of the sentence in this branch', type_='sentenceID')])
    
def get_operator_precedence() -> dict[str, int]:
    """Zwraca siłę wiązania danych spójników, im wyższa, tym mocniej wiąże (negacja ma najwyższą przykładowo)"""
    return PRECEDENCE