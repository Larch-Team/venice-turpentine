"""
Zastępstwo zeroth_order_logic z zaimplementowanym checkerem opartych na intuicjach zbiorów Hintikki oraz prostym solverem. Korzysta z nowo wprowadzonych drzew regułowych. Reguły działają na bazie tablic Smullyana. Po raz pierwszy zaimplementowany został system naiwny.
"""
import typing as tp

import plugins.Formal.__utils__ as utils
from exceptions import UserMistake, RaisedUserMistake
from history import History
from analytic_signed.solver import find_rule as find_rule, _solver
from analytic_signed.signed import *
from analytic_freedom.syntax_check import reduce_, find_all
from proof import Proof
from rule import SentenceID, SentenceTupleStructure, TokenID
from sentence import Sentence
from usedrule import UsedRule

SOCKET = 'Formal'
VERSION = '0.4.0'

PRECEDENCE = {
    'and': 3,
    'or': 3,
    'imp': 2,
    'not': 4
}

def generate_formula(sess: utils.Session_, length: int, vars: int) -> Sentence:
    f = utils.generate_wff(sess, length, {
        2 : ['and', 'or', 'imp'],
        1 : ['not']
    }, vars, 'sentvar')
    assert (p := check_syntax(f)) is None, f"Formuła jest niepoprawna: {p}"
    return f

def get_operator_precedence() -> dict[str, int]:
    """Zwraca siłę wiązania danych spójników, im wyższa, tym mocniej wiąże (negacja ma najwyższą przykładowo)"""
    return PRECEDENCE


def prepare_for_proving(statement: Sentence) -> Sentence:
    """Przygotowuje zdanie do dowodzenia - czyszczenie, dodawanie elementów"""
    return convert_to_signed(utils.add_prefix(statement, 'not', "~"))


def get_tags() -> tuple[str]:
    return 'propositional', 'uses negation', 'signed'


# SYNTAX CHECKING

def check_syntax(sentence: Sentence) -> tp.Union[UserMistake, None]:
    """Sprawdza poprawność zapisu tokenizowanego zdania, zwraca informacje o błędach w formule"""
    if any((i.startswith('sign') for i in sentence.getTypes())):
        return UserMistake('no sign symbols', 'Program samodzielnie sygnuje formuły, znaki te są zarezerwowane')
    reduced, indexes = reduce_(sentence)
    if reduced == 's':
        # ok
        return None
    if 's' not in reduced:
        return UserMistake('no variables', 'Zdanie nie zawiera żadnych zmiennych')

    if 'ss' in reduced:
        return UserMistake('nothing between formulas', 'W zdaniu znajdują się dwie zmienne lub formuły niepołączone spójnikiem')

    if '(' in reduced:
        errors = find_all(reduced, '(')
        for er in errors:
            return UserMistake('bracket left open', f'Otwarcie nawiasu na pozycji {indexes[er]+1} nie ma zamknięcia', {'pos': indexes[er]})

    if ')' in reduced:
        errors = find_all(reduced, ')')
        for er in errors:
            return UserMistake('bracket not opened', f'Zamknięcie nawiasu na pozycji {indexes[er]+1} nie ma otwarcia', {'pos': indexes[er]})

    if 's2' in reduced:
        errors = find_all(reduced, 's2')
        for er in errors:
            return UserMistake('no right', f'Spójnik dwuargumentowy na pozycji {indexes[er+1]+1} nie ma prawego argumentu', {'pos': indexes[er]})

    if '2s' in reduced:
        errors = find_all(reduced, '2s')
        for er in errors:
            return UserMistake('no left', f'Spójnik dwuargumentowy na pozycji {indexes[er]+1} nie ma lewego argumentu', {'pos': indexes[er]})
    raise Exception('Zdanie nie jest poprawne')

class SignedSmullyan(utils.Smullyan):
    
    def _strict(self, sentence: Sentence) -> tp.Union[None, SentenceTupleStructure]:
        return convert_to_signed(super()._strict(convert_from_signed(sentence)))
    
    def _naive(self, branch: list[Sentence], sentenceID: SentenceID, tokenID: TokenID) -> tp.Union[None, SentenceTupleStructure]:
        if len(branch[sentenceID]) == 1:
            addID = 0 if branch[sentenceID][0].startswith('signfalse_') else -1
        else:
            addID = 1 if branch[sentenceID][0].startswith('signfalse_') else -1
        return convert_to_signed(super()._naive([convert_from_signed(i) for i in branch], sentenceID, tokenID+addID))
    
# RULES

RULES = {
    'double not': utils.Rule(
        name='double not',
        symbolic="F~A / TA",
        docs="Usuwanie podwójnej negacji. Wymaga wskazania zdania w gałęzi.",
        reusable=False
    ),
    'true and': SignedSmullyan(
        name='true and',
        symbolic="T(A and B) / TA; TB",
        docs="Rozkładanie prawdziwej koniunkcji. Wymaga wskazania zdania w gałęzi oraz rozkładanego spójnika.",
        reusable=False
    ),
    'false or': SignedSmullyan(
        name='false or',
        symbolic="F(A or B) / FA; FB",
        docs="Rozkładanie fałszywej alternatywy. Wymaga wskazania zdania w gałęzi oraz rozkładanego spójnika.",
        reusable=False
    ),
    'false imp': SignedSmullyan(
        name='false imp',
        symbolic="F(A -> B) / TA; FB",
        docs="Rozkładanie fałszywej implikacji. Wymaga wskazania zdania w gałęzi oraz rozkładanego spójnika.",
        reusable=False
    ),
    'true or': SignedSmullyan(
        name='true or',
        symbolic="T(A or B) / TA | TB",
        docs="Rozkładanie prawdziwej alternatywy. Wymaga wskazania zdania w gałęzi oraz rozkładanego spójnika.",
        reusable=False
    ),
    'false and': SignedSmullyan(
        name='false and',
        symbolic="F(A and B) / FA | FB",
        docs="Rozkładanie fałszywej koniunkcji. Wymaga wskazania zdania w gałęzi oraz rozkładanego spójnika.",
        reusable=False
    ),
    'true imp': SignedSmullyan(
        name='true imp',
        symbolic="T(A -> B) / FA | TB",
        docs="Rozkładanie prawdziwej implikacji. Wymaga wskazania zdania w gałęzi oraz rozkładanego spójnika.",
        reusable=False
    )
}

double_not = RULES['double not']

ROOT_RULE = RULES['double not']
RULES['double not'].children = (RULES['true and'],)
RULES['true and'].children = (RULES['false or'],)
RULES['false or'].children = (RULES['false imp'],)
RULES['false imp'].children = (RULES['true or'],)
RULES['true or'].children = (RULES['false and'],)
RULES['false and'].children = (RULES['true imp'],)


@double_not.setStrict
def strict_doublenot(sentence: Sentence):
    return convert_to_signed(utils.reduce_prefix(utils.reduce_prefix(utils.empty_creator(convert_from_signed(sentence)), 'not'), 'not'))


@double_not.setNaive
def naive_doublenot(branch: list[Sentence], sentenceID: SentenceID):
    f = convert_from_signed(branch[sentenceID])
    res = utils.reduce_prefix(utils.reduce_prefix(utils.empty_creator(f), 'not'), 'not')
    if res is None:
        raise RaisedUserMistake('cannot perform', "This rule cannot be performed")
    return convert_to_signed(res)


# CHECKER

def group_by_rules(proof: Proof) -> dict[str, list[utils.SignedSentence]]:
    """
    Grupuje formuły w dowodzie do kontenerów na podstawie reguł, których można na nich użyć
    """
    containers = {i: [] for i in RULES.keys()}
    for leaf in proof.nodes.getleaves():
        branch, closed = leaf.getbranch_sentences()
        if closed:
            continue

        for num, sentence in enumerate(branch):
            if sentence in leaf.history:
                continue

            if (rule := find_rule(sentence)) is not None:
                containers[rule].append(
                    utils.SignedSentence(convert_from_signed(sentence), leaf.branch, num))
    return containers

def checker(rule: UsedRule, conclusion: Sentence) -> tp.Union[UserMistake, None]:
    """
    Na podstawie informacji o użytych regułach i podanym wyniku zwraca informacje o błędach. None wskazuje na poprawność wyprowadzenia wniosku z reguły.
    Konceptualnie przypomina zbiory Hintikki bez reguły o niesprzeczności.
    """
    conclusion = convert_from_signed(conclusion)
    premiss = rule.get_premisses()['sentenceID']  # Istnieje tylko jedna
    entailed = RULES[rule.rule].strict(premiss)
    if not entailed:
        return UserMistake('wrong rule', f"'{rule.rule}' can't be used on '{premiss.getReadable()}'", {'rule':rule.rule, 'premiss':premiss})
    elif conclusion in sum(convert_from_signed(entailed), ()) and find_rule(premiss) == rule.rule:
        return None
    else:
        return UserMistake('wrong precedence', f"Check which connective is the main one in '{premiss.getReadable()}'", {'rule':rule.rule, 'premiss':premiss})


# SOLVER


def solver(proof: Proof) -> bool:
    """ 
    Funkcja solvera, zwraca informację, czy dowód udało się ukończyć (powinna być zawsze True)
    """
    containers = group_by_rules(proof)
    s = _solver(proof, ROOT_RULE, containers, check_closure)
    proof.metadata['used_solver'] = s
    return s


def check_closure(branch: list[Sentence], used: History) -> tp.Union[None, tuple[utils.close.Close, str]]:
    """Sprawdza możliwość zamknięcia gałęzi, zwraca obiekty zamknięcia oraz komunikat do wyświetlenia"""
    for num1, statement_1 in enumerate(branch):
        for num2, statement_2 in enumerate(branch[num1+1:]):
            if statement_1[1:] == statement_2[1:] and statement_1[0] != statement_2[0]:
                return utils.close.Contradiction(sentenceID1=num1+1, sentenceID2=num2+1), "Sentences contradict. The branch was closed."

    if all(i in used or len(i)==2 for i in branch):
        return utils.close.Emptiness, "Nothing else to be done, branch was closed."
    return None


def get_rules_docs() -> dict[str, str]:
    """Zwraca reguły rachunku z opisem"""
    return {rule.name: rule.__doc__ for rule in RULES.values()}

def get_rules_symbolic() -> dict[str, str]:
    """Zwraca reguły rachunku z zapisem symbolicznym"""
    return {rule.name: rule.symbolic for rule in RULES.values()}


def get_needed_context(rule_name: str) -> tuple[utils.ContextDef]:
    """Zwraca informacje o wymaganym przez daną regułę kontekście w formie obiektów ContextDef"""
    return RULES[rule_name].context if RULES.get(rule_name) else None


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
    rule = RULES[name]
    sentenceID = context['sentenceID']

    if sentenceID < 0 or sentenceID >= len(branch):
        raise RaisedUserMistake("no such sentence", "No such sentence")
    sentence = branch[sentenceID]

    if not rule.reusable and sentence in used:  # Used sentence filtering
        raise RaisedUserMistake("already used",
            "This sentence was already used in a non-reusable rule")

    # Rule usage
    important_context = {i: j for i, j in context.items() if i in {
        i.variable for i in rule.context}}
    fin = rule.naive(branch, **important_context)
    if fin:
        return fin, len(fin)*([[0]] if rule.reusable else [[sentence]]), None
    else:
        return None, None, None
