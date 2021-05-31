"""
Rachunek sekwentów z mechanizmem kontroli pętli oraz priorytetyzowaniem formuł opracowany na podstawie: 
Howe, J. M. (1997, May). Two loop detection mechanisms: a comparison. In International Conference on Automated Reasoning with Analytic Tableaux and Related Methods (pp. 188-200). Springer, Berlin, Heidelberg.

Działa silniej od int_seqcal_swiss, dowody mogą czasem się nie udać

Implementacja opisana w:
https://github.com/PogromcaPapai/Larch/blob/24e1391c183d08842aa0cf7df971eeb01a1a9885/media/int_seqcal%20-%20implementacja.pdf
"""
import typing as tp
import FormalSystem.__utils__ as utils

SOCKET = 'FormalSystem'
VERSION = '0.0.1'


USED_TYPES = ('and', 'or', 'imp', 'sentvar', 'sep', 'turnstile','falsum')
PRECEDENCE = {
    'and': 4,
    'or': 4,
    'imp': 3,
    'sep': 2,
    'turnstile': 1
}

debrac = utils.reduce_brackets

def is_sequent(l, s) -> bool:
    buffor = []
    for i in l:
        if i.startswith('sep_'):
            if buffor == s:
                return True
            else:
                buffor = []
        else:
            buffor.append(i)
    return buffor == s


def sep(part: utils.Sentence = None) -> list[str]:
    if part is None or (len(part)>0 and not part[0].startswith('sep_;')):
        return ['sep_;']
    else:
        return []


# Zarządzanie priorytetem w zdaniach


def stoup_find(s: utils.Sentence) -> tp.Union[int, None]:
    count = 0
    for seq in s:
        if seq.startswith(f"sep_"):
            count += 1
        elif seq == "^":
            return count


def stoup_add(tree: tuple[tuple[utils.Sentence]], rule_name: str, new: bool = False) -> tuple[tuple[utils.Sentence]]:
    if rule_name.endswith('left_imp'):
        return (tree[0], (['^']+tree[1][0],))
    elif rule_name.endswith('left_or'):
        return tree
    elif rule_name.endswith('left_and'):
        if new:
            return tree
        ntree = ["^"]+tree[0][0]
        for i, seq in enumerate(ntree[0][0]):
            if seq.startswith("sep_"):
                break
        ntree.insert(i+1, "^")
        return ((ntree,),)
        


def stoupManager(func):
    def wrapped(auto: bool, left, right, num, *args):
        if not auto:
            return func(left, right, num, *args)
        if (priority := stoup_find(left)) is not None:
            if priority == num-1:
                res_left, res_right = func([i for i in left if i != "^"], right, num, *args)
                if res_left is not None:
                    return stoup_add(res_left, func.__name__), res_right
            else:
                raise utils.FormalSystemError("There is a sequent that is prioritized")
        else:
            res_left, res_right = func([i for i in left if i != "^"], right, num, *args)
            if res_left is not None:
                return stoup_add(res_left, func.__name__, True), res_right
    return wrapped


def stoupBlock(func):
    def wrapped(auto: bool, left, *args):
        if not auto:
            return func(left, *args)
        if stoup_find(left) is not None:
            raise utils.FormalSystemError("Rule can't be performed on sequents with an established priority")
        else:
            return func(left, *args)
    return wrapped


# Rule definition


@stoupManager
def rule_left_and(left: utils.Sentence, right: utils.Sentence, num: int):
    """ A,B,... => ...
        ______________
        A&B,... => ...
    """
    try:
        conj = utils.pop_part(left, 'sep', num-1)
    except IndexError:
        return (None, None)
    
    split = utils.strip_around(conj, 'and', False, PRECEDENCE)
    if split is None or split[0] is None:
        return (None, None)
    split = split[0]
    return ((debrac(split[0])+sep()+debrac(split[1])+sep(left)+left,),), ((right,),)


@stoupBlock
def rule_right_and(left: utils.Sentence, right: utils.Sentence):
    """ ... => A      ... => B
        __________________________
        ... => A&B
    """
    conj = utils.pop_part(right, 'sep', 0)
    if conj is None:
        return (None, None)

    split = utils.strip_around(conj, 'and', False, PRECEDENCE)
    if split is None or split[0] is None:
        return (None, None)
    split = split[0]
    return ((left,),(left,),), ((debrac(split[0]),),(debrac(split[1]),),)


@stoupManager
def rule_left_or(left: utils.Sentence, right: utils.Sentence, num: int):
    """ A,... => ...  B,... => ...
        __________________________
        AvB,... => ...
    """
    try:
        conj = utils.pop_part(left, 'sep', num-1)
    except IndexError:
        return (None, None)
    
    split = utils.strip_around(conj, 'or', False, PRECEDENCE)
    if split is None or split[0] is None:
        return (None, None)
    split = split[0]
    return ((debrac(split[0])+sep(left)+left,),(debrac(split[1])+sep(left)+left,),), ((right,),(right,),)


@stoupBlock
def rule_right_or(left: utils.Sentence, right: utils.Sentence, side: str, used: list[tuple[str]]):
    """ ... => (A,B)[side]
        ______________
        ... => AvB
    """
    if not right or side not in ('l', 'r','find'):
        return (None, None)

    split = utils.strip_around(right, 'or', False, PRECEDENCE)
    if split is None or split[0] is None:
        return (None, None)
    left_split, right_split = split[0]


    if side=='l':
        ret = left_split
    elif side=='r':
        ret = right_split
    else:
        if is_sequent(left, left_split):
            ret = left_split
        elif is_sequent(left, right_split):
            ret = right_split
        else:
            # Default case
            ret = max(split[0], key=len)

    if ret in used:
        raise utils.FormalSystemError("Operation prohibited by loop detection algorithm")
    utils.pop_part(right, 'sep', 0)
    return ((left,),), ((debrac(ret),),)


@stoupManager
def rule_left_imp(left: utils.Sentence, right: utils.Sentence, num: int):
    """ A -> B, ... => A    B,... => ...
        ________________________________
        A -> B,... => ...
    """
    try:
        conj = utils.pop_part(left, 'sep', num-1)
    except IndexError:
        return (None, None)
    
    split = utils.strip_around(conj, 'imp', False, PRECEDENCE)
    if split is None or split[0] is None:
        return (None, None)
    split = split[0]
    return ((conj+sep(left)+left,),(debrac(split[1])+sep(left)+left,),), ((debrac(split[0]),),(right,),)


@stoupBlock
def rule_right_imp(left: utils.Sentence, right: utils.Sentence):
    """ ..., A => B
        ______________
        ... => A -> B
    """
    try:
        conj = utils.pop_part(right, 'sep', 0)
    except IndexError:
        return (None, None)
    
    split = utils.strip_around(conj, 'imp', False, PRECEDENCE)
    if split is None or split[0] is None:
        return (None, None)
    split = split[0]
    return ((debrac(split[0])+sep(left)+left,),), ((debrac(split[1]),),)


@stoupBlock
def rule_left_strong(left: utils.Sentence, right: utils.Sentence, num: int):
    """ ..., A, A => ...
        ________________
        ..., A => ...
    """
    try:
        conj = utils.pop_part(left, 'sep', num-1)
    except IndexError:
        return (None, None)
    
    return ((conj+sep()+conj+sep(left)+left,),), ((right,),)


@stoupBlock
def rule_left_weak(left: utils.Sentence, right: utils.Sentence, num: int):
    """ ... => ...
        ______________
        ..., A => ...
    """
    try:
        conj = utils.pop_part(left, 'sep', num-1)
    except IndexError:
        return (None, None)
    
    return ((left,),), ((right,),)


RULES = {
    'left and': utils.Rule(
        symbolic="A&B, ... => ... // A, B, ... => ...",
        docs="Rozkładanie koniunkcji po lewej stronie sekwentu",
        func=rule_left_and,
        reusable=None, # Not needed
        context=[utils.ContextDef(
            variable='partID',
            official='Subsentence number',
            docs='The number of the sequent\'s element',
            type_=int
        )]
    ),
    'left or': utils.Rule(
        symbolic="A v B, ... => ... // A, B, ... => ...",
        docs="Rozkładanie alternatywy po lewej stronie sekwentu",
        func=rule_left_or,
        reusable=None, # Not needed
        context=[utils.ContextDef(
            variable='partID',
            official='Subsentence number',
            docs='The number of the sequent\'s element',
            type_=int
        )]
    ),
    'right and': utils.Rule(
        symbolic="... => A & B // ... => A | ... => B",
        docs="Rozkładanie koniunkcji po prawej stronie sekwentu",
        func=rule_right_and,
        reusable=None, # Not needed
        context=[]
    ),
    'right or': utils.Rule(
        symbolic="... => ... v ... // ... => ...",
        docs="Rozkładanie alternatywy po prawej stronie sekwentu",
        func=rule_right_or,
        reusable=None, # Not needed
        context=[
        utils.ContextDef(
            variable='conn_side',
            official='Side of the or operation',
            docs='l/r/find; `find` option searches for the best possible fit',
            type_=str
        )]
    ),
    'left imp': utils.Rule(
        symbolic="..., A -> B => ... // ..., A => B | ..., B => ...",
        docs="Rozkładanie implikacji po lewej stronie sekwentu",
        func=rule_left_imp,
        reusable=None, # Not needed
        context=[utils.ContextDef(
            variable='partID',
            official='Subsentence number',
            docs='The number of the sequent\'s element',
            type_=int
        )]
    ),
    'right imp': utils.Rule(
        symbolic="... => A -> B // A, ... => B",
        docs="Rozkładanie implikacji po prawej stronie sekwentu",
        func=rule_right_imp,
        reusable=None, # Not needed
        context=[]
    ),
    'left weak': utils.Rule(
        symbolic="A, A, ... => ... // A, ... => ...",
        docs="Reguła osłabiania lewej strony",
        func=rule_left_weak,
        reusable=None, # Not needed
        context=[utils.ContextDef(
            variable='partID',
            official='Subsentence number',
            docs='The number of the sequent\'s element',
            type_=int
        )]
    ),
    'left strong': utils.Rule(
        symbolic="A, ... => ... // A, A, ... => ...",
        docs="Reguła wzmacniania dla lewej strony",
        func=rule_left_strong,
        reusable=None, # Not needed
        context=[utils.ContextDef(
            variable='partID',
            official='Subsentence number',
            docs='The number of the sequent\'s element',
            type_=int
        )]
    ),
}

# __template__


def prepare_for_proving(statement: utils.Sentence) -> utils.Sentence:
    """Przygotowuje zdanie do dowodzenia - czyszczenie, dodawanie elementów"""
    statement = utils.reduce_brackets(statement)
    if 'turnstile_=>' not in statement:
        return ['turnstile_=>']+statement
    else:
        return statement


def check_closure(branch: list[utils.Sentence], used: set[tuple[str]]) -> tp.Union[None, tuple[utils.close.Close, str]]:
    """Sprawdza możliwość zamknięcia gałęzi, zwraca obiekty zamknięcia oraz komunikat do wyświetlenia"""
    left, right = utils.strip_around(branch[-1], "turnstile", False, PRECEDENCE)[0]
    left = [i for i in left if i != "^"]
    seps = sum((i.startswith('sep_') for i in left), 1)

    # Right part verification
    empty = len(right)==1

    # Left part verification
    if not left:
        return None
    for i in range(seps):
        f = utils.pop_part(left[:], 'sep', i)

        # F, ... => ...
        if len(f)==1 and f[0].startswith("falsum_"):
            return utils.close.Falsum, "Falsum found on the left"

        # p, ... => p
        if f==right:
            return utils.close.Axiom, "Sequent on the right corresponds with a sequent on the left"

        # Detect finish
        empty &= not any((any((j.startswith(i) for j in f)) for i in ('and_', 'or_', 'imp_')))

    if empty:
        return utils.close.Emptiness, "Nothing more can be done with this branch, so it was closed."


def check_syntax(tokenized_statement: utils.Sentence) -> tp.Union[str, None]:
    """Sprawdza poprawność zapisu tokenizowanego zdania, zwraca informacje o błędach w formule"""
    return None


def get_rules() -> dict[str, str]:
    """Zwraca reguły rachunku z opisem"""
    return {
        name: "\n".join((rule.symbolic, rule.docs))
        for name, rule in RULES.items()
    }


def get_needed_context(rule_name: str) -> tuple[utils.ContextDef]:
    """Zwraca informacje o wymaganym przez daną regułę kontekście w formie obiektów ContextDef"""
    if (rule := RULES.get(rule_name, None)):
        return tuple(rule.context)
    else:
        return None


def get_used_types() -> tuple[str]:
    return USED_TYPES


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
    rule = RULES[name]

    start = utils.strip_around(branch[-1], "turnstile", False, PRECEDENCE)
    start_left, start_right = start[0]
    
    # Check sequent number
    if context.get('partID', -1) > sum(i.startswith('sep') for i in start_left)+1:
        raise utils.FormalSystemError("Sequent number is too big")

    # Loop detection
    history = None
    if name == "left imp":
        p = utils.pop_part(start_left[:], 'sep', context['partID']-1)
        l, r = utils.strip_around(p, "imp", False, PRECEDENCE)[0]
        if tuple(l) in used:
            raise utils.FormalSystemError("Operation prohibited by loop detection algorithm")
        else:
            history = [[l], [0]]


    elif name == 'left or':
        p = utils.pop_part(start_left[:], 'sep', context['partID']-1)
        l, r = utils.strip_around(p, "or", False, PRECEDENCE)[0]
        if is_sequent(start_left, l) or is_sequent(start_left, r):
            raise utils.FormalSystemError("Operation prohibited by loop detection algorithm")
        else:
            history = [[-1, start_right], [-1, start_right]]


    elif name == 'right imp':
        if (stripped := utils.strip_around(start_right, "imp", False, PRECEDENCE)) is None:
            return None, None
        l, r = stripped[0]
        if is_sequent(start_left, l):
            if tuple(r) not in used:
                history = [[r]]
            else:
                raise utils.FormalSystemError("Operation prohibited by loop detection algorithm")
        else:
            history = [[-1, r]]


    elif name == 'right and':
        l, r = utils.strip_around(start_right, "and", False, PRECEDENCE)[0]
        if tuple(l) in used or tuple(r) in used:
            raise utils.FormalSystemError("Operation prohibited by loop detection algorithm")
        else:
            history = [[l], [r]]

    elif name =='right or':
        context['used'] = used

    # Rule usage
    usage = rule.func(auto, start_left[:], start_right[:], *context.values())
    if not usage:
        return None, None
    left, right = usage


    # Outcome return
    if not (left is None or right is None):
        # History length multiplication
        if not history:
            history = [[0]]*len(left)
        return utils.merge_tupstruct(left, right, "turnstile_=>"), history
    else:
        return None, None

def get_operator_precedence() -> dict[str, int]:
    """Zwraca siłę wiązania danych spójników, im wyższa, tym mocniej wiąże (negacja ma najwyższą przykładowo)"""
    return PRECEDENCE