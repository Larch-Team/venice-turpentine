from __future__ import annotations

import json
import random
import typing as tp
from collections import OrderedDict, namedtuple
from math import inf as INFINITY

from anytree import NodeMixin, util

from close import *
from history import *

Sentence = tp.NewType("Sentence", list[str])
PrintedProofNode = namedtuple('PrintedProofNode', ('sentence', 'children', 'closer'))

SentenceTupleStructure = tp.NewType('SentenceTupleStructure', tuple[tuple[Sentence]])
HistoryTupleStructure = tp.NewType('HistoryTupleStructure', tuple[tuple[tp.Union[Sentence, int, tp.Callable]]])

def getcolors():
    """
    Zwraca słownik kolorów wraz z ich kodami RGB
    """
    with open('colors.json') as f:
        c = json.load(f)
    return c

class ProofNodeError(Exception):
    def __init__(self, msg: str, *args, **kwargs):
        super().__init__(msg, *args, **kwargs)


class ProofBase(object):
    """Klasa macierzysta dla ProofNode implementująca wszystkie czysto dowodowe elementy"""


    def __init__(self, sentence: Sentence, branch: str, layer: int = 0, history: History = None) -> None:
        """Używaj ProofNode"""
        super().__init__()
        self.sentence = sentence
        self.branch = branch
        self.closed = None
        self.history = History() if history is None else history.copy()
        self.editable = True
        self.layer = layer

    def close(self, close: Close = None, text: str = None, success: bool = None) -> None:
        """Zamyka gałąź używając obiektu `Close`, lub tekstu do wyświetlania użytkownikowi oraz informacje, czy można uznać to zamknięcie za sukces (dla przykładu: sprzeczność w tabeli analitycznej jest sukcesem, próba zapobiegnięcia pętli już nie)"""
        assert self.is_leaf, "Można zamykać tylko liście"
        if close:
            self.closed = close
        else:
            assert isinstance(text, str) and isinstance(success, bool)
            self.closed = Close(success, text)
        self.editable = False


    def gethistory(self) -> History:
        """
        Zwraca hashowane wartości zdań znajdujących się w historii (w formie `History` - podklasy zbioru). Hashowaną wartość można uzyskać z `hash(Sentence)`.
        """
        return self.history.copy()


    def History(self, *commands: tuple[tp.Union[Sentence, int, Callable]]) -> None:
        """ Używane do manipulacji historią

            Możliwe argumenty:
                - `Sentence`    - dodaje formułę do historii 
                - `Callable`    - wykonuje operacje `callable(history)` na obiekcie historii, a wynik nadpisuje jako nową historię; traktuj ją jako `set`
                - `int`         - wykonuje jedną z predefiniowanych operacji:
                    - 0 - operacja pusta
                    - 1 - reset historii

            :raises TypeError: Typ nie jest obsługiwany 
        """
        self.history(*commands)



class ProofNode(ProofBase, NodeMixin):
    """Reprezentacja pojedynczego zdania w drzewie"""

    def __init__(self, sentence: Sentence, branch_name: str, layer: int = 0, history: History = None, parent: ProofNode = None, children: tp.Iterable[ProofNode] = []):
        """Reprezentacja pojedynczego zdania w drzewie

        :param sentence: Opisywane zdanie
        :type sentence: Sentence
        :param branch_name: Nazwa gałęzi
        :type branch_name: str
        :param layer: numer warstwy, można go utożsamiać z numerem ruchu w dowodzie, pozwala na wycofywanie ruchów w przyszłości
        :type layer: int, defaults to 0
        :param history: obiekt historii, przechowuje informacjęo użytych formułach, defaults to None
        :type history: History, optional
        :param parent: poprzednik węzłu w drzewie, defaults to None
        :type parent: ProofNode, optional
        :param children: następniki węzłu w drzewie, defaults to []
        :type children: tp.Iterable[ProofNode], optional
        """
        super().__init__(sentence=sentence, branch=branch_name, layer=layer, history=history)
        self.parent = parent or None
        self.children = children


    def __repr__(self) -> str:
        return f"{self.branch}:{len(self.ancestors)}{' (closed)' if self.closed else ''} - {self.sentence.getReadable()}"


    def gen_name(self, namegen: random.Random, am=2) -> tuple[str]:
        """Zwraca `am` nazw dla gałęzi z czego jedną jest nazwa aktualnej"""
        branch_names = self.getbranchnames()
        possible = [i for i in getcolors() if not i in branch_names]
        if len(possible)<am-1:
            if len(self.leaves) == 1000:
                raise ProofNodeError("No names exist")
            return self.branch, *[str(namegen.randint(0, 1000)) for i in range(am-1)]
        return self.branch, *namegen.choices(possible, k=am-1)
    
    
    # Static
    
    @staticmethod
    def insert_history(used_extention: HistoryTupleStructure, children: Iterable[ProofNode]):
        assert len(children) == len(used_extention), "Liczba gałęzi i list komend dla historii powinna być taka sama"
        for j, s in zip(children, used_extention):
            j.History(*s)
            for k in j.descendants:
                k.History(*s)


    # Nawigacja


    def getbranchnames(self):
        """Zwraca nazwy wszystkich gałęzi w dowodzie"""
        return [i.branch for i in self.getleaves()]


    def getbranch_nodes(self) -> tuple[list[ProofNode], Close]:
        """Zwraca gałąź dowodu w formie węzłów z informacjami o jej zamknięciu"""
        assert self.is_leaf, "Gałąź nie jest kompletna, gdyż węzeł nie jest liściem"
        return [i for i in self.path], self.closed


    def getbranch_sentences(self) -> tuple[list[Sentence], Close]:
        """Zwraca gałąź dowodu z informacjami o jej zamknięciu"""
        assert self.is_leaf, "Gałąź nie jest kompletna, gdyż węzeł nie jest liściem"
        return [i.sentence for i in self.path], self.closed


    def gettree(self) -> PrintedProofNode:
        """Rekurencyjnie opracowuje PrintedProofNode - jest to namedtuple wykorzystywana podczas printowania drzewa"""
        if not self.is_leaf:
            children = (i.gettree() for i in self.children)
            closer = ''
        else:
            children = None
            closer = str(self.closed) if self.closed else None
        return PrintedProofNode(sentence=self.sentence, children=children, closer=closer)


    def notused(self) -> list[ProofNode]:
        return [i for i in self.getbranch_nodes()[0] if i.sentence not in self.history]
    

    def getleaves(self, *names: tp.Iterable[str]) -> list[ProofNode]:
        """Zwraca wszystkie liście *całego drzewa*, bądź tylko liście o wybranych nazwach (jeśli zostaną podane w `names`)

        :names: Iterable[str]
        :rtype: list[ProofNode]
        """
        if names:
            return [i for i in self.root.leaves if i.branch in names]
        else:
            return self.root.leaves

    def getleaf(self, name: str) -> ProofNode:
        branches = self.getleaves(name)
        if branches:
            return branches[0]
        else:
            return None

    def getopen(self) -> list[ProofNode]:
        """Zwraca listę *otwartych* liści całego drzewa"""
        return [i for i in self.getleaves() if not i.closed]


    def getneighbour(self, left_right: str) -> ProofNode:
        """Zwraca prawego, lub lewego sąsiada danego węzła. 
        Równie dobrze można używać `anytree.util.rightsibling(self)` oraz `anytree.util.leftsibling(self)`

        :param left_right: 'L/Left' lub 'R/Right'
        :type left_right: str
        :raises ProofNodeError: Podano niepoprawny kierunek
        :return: Sąsiad
        :rtype: ProofNode
        """
        if not self.parent:
            return None
        if left_right.upper() in ('R', 'RIGHT'):
            return util.rightsibling(self)
        elif left_right.upper() in ('L', 'LEFT'):
            return util.leftsibling(self)
        else:
            raise ProofNodeError(f"'{left_right}' is not a valid direction")


    def is_closed(self) -> bool:
        """Sprawdza, czy wszystkie gałęzie zamknięto"""
        return all((i.closed for i in self.leaves))


    def is_successful(self) -> bool:
        """Sprawdza, czy wszystkie liście zamknięto *ze względu na sukces*"""
        return all((i.closed is not None and i.closed.success == 1 for i in self.getleaves()))


    # Modyfikacja

    def append(self, sentences: SentenceTupleStructure, namegen: random.Random) -> int:
        """Dodaje zdania do drzewa, zwraca warstwę"""
        names = self.gen_name(namegen, am=len(sentences))
        layer = max((i.layer for i in self.getleaves()))+1
        for i, branch in enumerate(sentences):
            par = self
            for sen in branch:
                par = ProofNode(sen, names[i], layer, self.history, parent=par)
        return layer


    def pop(self, layer: int):
        """
        Usuwa z dowodu wszystkie węzły o danej, lub wyższej warstwie

        :param layer: Warstwa (najwyższą można uzyskać przez sprawdzenie wartości w stosie użytych reguł)
        :type layer: int
        """
        self.root._pop(layer)

    def _pop(self, layer: int):
        """
        Usuwa z dowodu wszystkie węzły o danej, lub wyższej warstwie

        :param layer: Warstwa (najwyższą można uzyskać przez sprawdzenie wartości w stosie użytych reguł)
        :type layer: int
        """
        self.children = [i for i in self.children if i.layer<layer]
        for i in self.children:
            i._pop(layer)