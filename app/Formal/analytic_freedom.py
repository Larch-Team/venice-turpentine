"""
Tutaj umieść dokumentację swojego pluginu
"""
from collections import namedtuple
import typing as tp
import Formal.__utils__ as utils
from proof import Proof
from rule import Rule, SentenceID
from sentence import Sentence
from usedrule import UsedRule

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


### RULES

RULES = {}
RULES |= {
    'double not': utils.Rule(
        name='double not',
        symbolic="~~A / A",
        docs="Usuwanie podwójnej negacji. Wymaga wskazania zdania w gałęzi.",
        reusable=False,
        children=(RULES['true and'])
    ),
    'true and': utils.Smullyan(
        name='true and',
        symbolic="A and B / A; B",
        docs="Rozkładanie prawdziwej koniunkcji. Wymaga wskazania zdania w gałęzi oraz rozkładanej koniunkcji.",
        reusable=False,
        children=(RULES['false or'])
    ),
    'false or': utils.Smullyan(
        name='false or',
        symbolic="~(A or B) / ~A; ~B",
        docs="Rozkładanie fałszywej alternatywy. Wymaga wskazania zdania w gałęzi.",
        reusable=False,
        children=(RULES['false imp'])
    ),
    'false imp': utils.Smullyan(
        name='false imp',
        symbolic="~(A -> B) / A; ~B",
        docs="Rozkładanie fałszywej implikacji. Wymaga wskazania zdania w gałęzi.",
        reusable=False,
        children=(RULES['true or'])
    ),
    'true or': utils.Smullyan(
        name='true or',
        symbolic="(A or B) / A | B",
        docs="Rozkładanie prawdziwej alternatywy. Wymaga wskazania zdania w gałęzi.",
        reusable=False,
        children=(RULES['false and'])
    ),
    'false and': utils.Smullyan(
        name='false and',
        symbolic="~(A and B) / ~A | ~B",
        docs="Rozkładanie fałszywej koniunkcji. Wymaga wskazania zdania w gałęzi.",
        reusable=False,
        children=(RULES['true imp'])
    ),
    'true imp': utils.Smullyan(
        name='true imp',
        symbolic="(A -> B) / ~A | B",
        docs="Rozkładanie prawdziwej implikacji. Wymaga wskazania zdania w gałęzi.",
        reusable=False
    )
}

double_not = RULES['double not']

@double_not.setStrict
def strict_doublenot(sentence: Sentence):
    return utils.reduce_prefix(utils.reduce_prefix(sentence, 'neg'), 'neg')

@double_not.setNaive
def naive_doublenot(branch: list[Sentence], sentID: SentenceID):
    return utils.reduce_prefix(utils.reduce_prefix(branch[sentID], 'neg'), 'neg')


### CHECKER


# def checker(rule: UsedRule, conclusion: Sentence) -> bool:
#     # sourcery skip: merge-duplicate-blocks
#     premiss = rule.get_premisses()[0]
#     connective, use_result = premiss.getMainConnective()
#     if connective.startswith('neg'):
#         # zastosowanie reguły dla prawdziwości na zanegowanej formule
#         if rule.rule.startswith('true'):
#             return False
#         connective, use_result = use_result[0].getMainConnective()
#     # zastosowanie reguły dla fałszywości na niezanegowanej formule
#     elif rule.rule.startswith('false'):
#         return False

#     # Zastosowanie reguły dla złego spójnika
#     if not connective.startswith(rule.rule.split()[1]):
#         return False
#     # Sprawdzenie, czy reguły zastosowano na poprawnej instancji spójnika
#     else:
#         return conclusion.getNonNegated() in {i.getNonNegated() for i in use_result}


def checker(rule: UsedRule, conclusion: Sentence) -> bool:
    """
    Na podstawie informacji o użytych regułach i podanym wyniku zwraca wartość prawda/fałsz informującą o wyprowadzalności wniosku z reguły.
    Konceptualnie przypomina zbiory Hintikki bez reguły o niesprzeczności.
    """
    premiss = rule.get_premisses()[0] # Istnieje tylko jedna
    entailed = RULES[rule.rule].strict(premiss)
    return conclusion in sum(entailed, [])


### SOLVER


def solver(proof: Proof) -> list[str]:
    pass


### INNE


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
                return utils.close.Contradiction(sentenceID1 = num1+1, sentenceID2 = num2+1), "Sentences contradict. The branch was closed."

    return None


def get_used_types() -> tuple[str]:
    return ('and', 'or', 'imp', 'not', 'sentvar')


def get_rules_docs() -> dict[str, str]:
    """Zwraca reguły rachunku z opisem"""
    return {rule.name:rule.__doc__ for rule in RULES.values()}


def get_needed_context(rule_name: str) -> tuple[utils.ContextDef]:
    """Zwraca informacje o wymaganym przez daną regułę kontekście w formie obiektów ContextDef"""
    return RULES[rule_name].context


def use_rule(name: str, branch: list[utils.Sentence], used: utils.History, context: dict[str, tp.Any], decisions: dict[str, tp.Any]) -> tuple[utils.SentenceTupleStructure, utils.HistoryTupleStructure, dict[str, tp.Any]]:  
    """
    Używa określonej reguły na podanej gałęzi.
    Więcej: https://www.notion.so/szymanski/Gniazda-w-Larchu-637a500c36304ee28d3abe11297bfdb2#98e96d34d3c54077834bc0384020ff38

    :param name: Nazwa używanej reguły, listę można uzyskać z pomocą Formal.get_rules_docs()
    :type name: str
    :param branch: Lista zdań w gałęzi, na której została użyta reguła
    :type branch: list[utils.Sentence]
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
    :rtype: tuple[tp.Union[tuple[tuple[utils.Sentence]], None], tp.Union[tuple[tuple[tp.Union[int, Callable, utils.Sentence]]], None]]
    """
    rule = RULES[name]
    sentenceID = context['sentenceID']

    if sentenceID < 0 or sentenceID >= len(branch):
        raise utils.FormalError("No such sentence")
    sentence = branch[sentenceID]

    if not rule.reusable and sentence in used: # Used sentence filtering
        raise utils.FormalError("This sentence was already used in a non-reusable rule")

    # Rule usage
    important_context = {i:j for i,j in context.items() if i in {i.variable for i in rule.context}}
    fin = rule.naive(branch, **important_context)
    if fin:
        return fin, len(fin)*([[0]] if rule.reusable else [[sentence]]), None
    else:
        return None, None, None
