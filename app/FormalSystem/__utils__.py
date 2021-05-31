from collections import namedtuple
import typing as tp
import close
from tree_helpers import History
from sentence import Sentence

Rule = namedtuple('Rule', ('symbolic', 'docs', 'func', 'context', 'reusable'))

ContextDef = namedtuple(
    'ContextDef', ('variable', 'official', 'docs', 'type_'))


class FormalSystemError(Exception):
    pass


# Rule decorators

def transform_to_sentences(converted, session):
    """Konwertuje struktury krotek z listami stringów do struktur krotek ze zdaniami, inne obiekty pozostawia niezmienione"""
    if isinstance(converted, tuple):
        return tuple(transform_to_sentences(i, session) for i in converted)
    elif isinstance(converted, list): 
        return Sentence(converted, session)
    else:
        return converted  

def Creator(func):
    """Funkcje z tym dekoratorem mogą tworzyć nowe struktury krotek"""
    def wrapper(sentence, *args, **kwargs):
        assert not isinstance(
            sentence, tuple), "Tuple structure already exists"
        if sentence is None:
            return None
        assert isinstance(sentence, Sentence)
        result = func(sentence[:], *args, **kwargs)
        return transform_to_sentences(result, sentence.S)
    return wrapper


def Modifier(func):
    """Funkcje z tym dekoratorem mogą tylko iterować po istniejących strukturach krotek"""
    def wrapper(sentence, *args, **kwargs):
        if isinstance(sentence, tuple):
            calculated = [wrapper(i, *args, **kwargs) for i in sentence]
            if any((i is None for i in calculated)):
                return None
            else:
                return tuple(calculated)
        elif sentence is None:
            return None
        elif isinstance(sentence, Sentence):
            result = func(sentence[:], *args, **kwargs)
            return transform_to_sentences(result, sentence.S)
        else:
            raise TypeError("Modifier is not a sentence nor a tuple")

    return wrapper


# Formating and cleaning

@Modifier
def reduce_brackets(sentence: Sentence) -> Sentence:
    """Minimalizuje nawiasy w zdaniu"""
    return sentence.reduceBrackets()


@Modifier
def quick_bracket_check(reduced: Sentence) -> bool:
    return reduced.count('(') == reduced.count(')')


def cleaned(func):
    """Dekorator automatycznie czyści wynik działania funkcji, aktualnie jest to redukcja nawiasów"""
    def wrapper(*args, **kwargs):
        returned = func(*args, **kwargs)
        returned = reduce_brackets(returned)
        if returned:
            assert quick_bracket_check(returned)
            assert Modifier(isinstance)(returned, Sentence)
        return returned
    return wrapper


# Useful functions for creating rules

# Sentence manipulation

def pop_part(sentence: Sentence, split_type: str, sent_num: int):
    """
    Zwraca n-te podzdanie (podział według obiektów split_type) usuwając je ze zdania
    """
    split_count = 0
    start_split = 0
    for s in sentence:
        if s.startswith(f"{split_type}_"):
            split_count += 1
        if split_count == sent_num:
            break
        start_split += 1

    if len(sentence) <= start_split or split_count<sent_num:
        raise IndexError("sent_num is too big")

    part = []
    if split_count>0:
        sentence.pop(start_split)
    
    while start_split<len(sentence) and not sentence[start_split].startswith(f"{split_type}_"):
        part.append(sentence.pop(start_split))

    if len(sentence)>0 and split_count == 0:
        sentence.pop(start_split)
    return part


# Tuple structure manipulation


def merge_tupstruct(left: tuple[tuple[str]], right: tuple[tuple[str]], glue: str):
    """Łączy struktury krotek w jedną dodając do siebie zdania z `glue` między nimi"""
    if isinstance(left, tuple) and isinstance(right, tuple):
        assert len(left) == len(right), "Tuples not of equal length"
        end = [merge_tupstruct(l, r, glue) for l, r in zip(left, right)]
        return tuple(end)
    elif isinstance(left, Sentence) and isinstance(right, Sentence):
        return left + [glue] + right
    else:
        # Bug reporting
        l_correct = isinstance(left, (Sentence, tuple))
        r_correct = isinstance(right, (Sentence, tuple))
        if l_correct and r_correct:
            raise AssertionError("Tuples not of equal depth")
        else:
            raise AssertionError((l_correct*"left")+(l_correct*r_correct *' and ')+(r_correct*"right") + "tuple is messed up")


def select(tuple_structure: tuple[tuple[Sentence]], selection: tuple[tuple[bool]], func: callable) -> tuple[tuple[Sentence]]:
    """Selektywne wykonywanie funkcji na elementach struktury krotek

    Przykłady:


    tuple_structure :   ((A, B))
    selection       :   ((True, False))
    ___________________________________
    Result          :   ((func(A), B))


    tuple_structure :   ((A, B), (C, D))
    selection       :   ((False, False), (True, False))
    ___________________________________
    Result          :   ((A, B), (func(C), D))


    tuple_structure :   ((A, B), (C, D))
    selection       :   ((False, True), (False, True))
    ___________________________________
    Result          :   ((A, func(B)), (C, func(D)))


    :param tuple_structure: Struktura krotek
    :type tuple_structure: tuple[tuple[Sentence]]
    :param selection: Filtr o kształcie struktury krotek
    :type selection: tuple[tuple[bool]]
    :param func: Funkcja stosowana na elementach, dla których filtr jest prawdziwy
    :type func: callable
    :return: Zmodyfikowana struktura krotek
    :rtype: tuple[tuple[Sentence]]
    """

    # Tests
    if not tuple_structure:
        return None
    assert len(tuple_structure) == len(selection)
    assert all((len(tuple_structure[i]) == len(
        selection[i]) for i in range(len(selection))))

    # Execution
    return _select(tuple_structure, selection, func)


def _select(filtered, selection, func: callable) -> tuple[tuple[Sentence]]:
    """Recursion used in `select`; DO NOT USE"""
    after = []

    for s, use in zip(filtered, selection):
        if isinstance(use, bool):
            if use:
                after.append(func(s))
            else:
                after.append(s)
        else:
            after.append(_select(s, use, func))
    return tuple(after)


# Creators


@Creator
def empty_creator(sentence: Sentence):
    """Zwraca zdanie w strukturze krotek reprezentującą jedno rozgałęzienie z jednym zdaniem"""
    return ((sentence,),)


@cleaned
@Creator
def strip_around(sentence: Sentence, border_type: str, split: bool, precedence: dict[str, int]) -> tuple[tuple[Sentence]]:
    """Dzieli zdanie wokół głównego spójnika, jeśli spójnikiem jest `border_type`

    :param sentence: zdanie do podziału
    :type sentence: Sentence
    :param border_type: typ spójnika, wokół którego dzielone będzie zdanie
    :type border_type: str
    :param split: Czy tworzyć nowe gałęzie?
    :type split: bool
    :param precedence: Kolejność wykonywania działań
    :type precedence: dict[str, int]
    :return: Struktura krotek
    :rtype: tuple[tuple[Sentence]]
    """
    if not sentence:
        return None

    middle, subsents = sentence.getMainConnective(precedence)
    if middle is None or middle.split('_')[0] != border_type:
        return None
    
    left, right = subsents
    if split:
        return ((left,), (right,))
    else:
        return ((left, right),)


# Modifiers


@cleaned
@Modifier
def reduce_prefix(sentence: Sentence, prefix_type: str, precedence: dict[str, int]) -> Sentence:
    """Usuwa prefiksy ze zdań

    :param sentence: zdanie do modyfikacji
    :type sentence: Sentence
    :param prefix_type: typ prefiksu do usunięcia
    :type prefix_type: str
    :param precedence: Kolejność wykonywania działań
    :type precedence: dict[str, int]
    :return: Nowe zdanie
    :rtype: Sentence
    """
    if not sentence:
        return None

    middle, subsents = sentence.getMainConnective(precedence)
    if middle is None or middle.split('_')[0] != prefix_type:
        return None
    
    _, right = subsents
    return right


@Modifier
def add_prefix(sentence: Sentence, prefix: str, lexem: str) -> Sentence:
    """Dodaje prefiks do zdania

    :param sentence: Zdanie do modyfikacji
    :type sentence: Sentence
    :param prefix: Typ prefiksu (`x` w `x_y`)
    :type prefix: str
    :param lexem: Leksem prefiksu  (`y` in `x_y`)
    :type lexem: str
    :return: Zmieniony prefiks
    :rtype: Sentence
    """
    if len(sentence) == 1:
        return Sentence([f"{prefix}_{lexem}", *sentence], sentence.S)
    new_record = {0:sentence.calcPrecedenceVal(prefix)}
    return Sentence([f"{prefix}_{lexem}", '(', *sentence, ')'], sentence.S, {i+2:j+1 for i,j in sentence.precedenceBaked.values()} | new_record)


@Modifier
def on_part(sentence: Sentence, split_type: str, sent_num: int, func: callable):
    """Wykonuje funkcję na pewnej części zdania (części oddzielone są `split_type`)
    Ex.:
              onpart(s, sep*, 1, f)
    x0;x1;x3 ----------------------> x0;f(x1);x2

    *w pluginie basic sep jest typem ;

    :param sentence: Zdanie
    :type sentence: Sentence
    :param split_type: Typ dzielący od siebie części zdania
    :type split_type: str
    :param sent_num: Numer podzdania do zastosowania funkcji
    :type sent_num: int
    :param func: Używana funkcja
    :type func: callable
    """

    split_count = 0
    for start_split, s in enumerate(sentence):
        if s.startswith(f"{split_type}_"):
            split_count += 1
        if split_count == sent_num:
            break

    if len(sentence) <= start_split or split_count<sent_num:
        return None

    end_split = start_split+1
    while end_split<len(sentence) and not sentence[end_split].startswith(f"{split_type}_"):
        end_split += 1

    if len(sentence)-1 <= end_split:
        out = func(sentence[start_split+(split_count!=0):])
    else:
        out = func(sentence[start_split+(split_count!=0):end_split])

    if isinstance(out, Sentence):
        return sentence[:start_split+(split_count!=0)] + out + sentence[end_split:]
    elif isinstance(out, tuple):
        l = []
        for branch in out:
            assert isinstance(branch, tuple)
            l.append(
                tuple(
                    sentence[: start_split + (split_count != 0)]
                    + i
                    + sentence[end_split:]
                    for i in branch
                )
            )

        return tuple(l)
    else:
        return None