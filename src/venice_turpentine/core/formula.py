from __future__ import annotations

from collections import OrderedDict
from typing import Callable, Optional, SupportsIndex, TypeVar, Union, overload

from ..formal_systems import FormalSystem
from .token import Token

T = TypeVar("T")


def apply_on_keys(dictionary: dict, op: Callable) -> dict:
    return {op(i): j for i, j in dictionary.items()}


def slice_dict_by_key(
    dictionary: dict[int, T], key: int
) -> tuple[dict[int, T], dict[int, T]]:
    return (
        {i: j for i, j in dictionary.items() if i < key},  # left
        {i - key - 1: j for i, j in dictionary.items() if i > key},  # right
    )


class Formula(list[Token]):

    def __init__(
        self,
        token_list: list[Token],
        formal_system: FormalSystem,
        precedenceBaked: Optional[dict[str, float]] = None,
    ):
        self.formal_system = formal_system
        self.precedenceBaked = precedenceBaked or {}
        super().__init__(token_list)

    def getTypes(self) -> list[str]:
        """Zwraca listę kolejno występujących typów w zdaniu"""
        return [i.type_ for i in self]

    def getLexems(self) -> list[str]:
        """Zwraca ze zdania leksemy użyte przez użytkownika"""
        return [i.lexem for i in self]

    def getItems(self) -> list[tuple[str, str]]:
        """Zwraca listę kolejno występujących par typów i leksemów"""
        items = []
        for i in self:
            items.append((i.type_, i.lexem))
        return items

    def getUnique(self) -> list[str]:
        """Zwraca zapis unikalny dla tego zdania; odporne na różnice w formacie zapisu"""
        ret = []
        for token in self:
            if token.type_ in (
                "indvar",
                "constant",
                "predicate",
                "function",
                "sentvar",
            ):
                ret.append(token.type_)
            else:
                ret.append(token.lexem)
        return ret

    def getPrecedence(self) -> dict[str, int]:
        return self.formal_system.get_operator_precedence()

    # Manipulacja zdaniem

    def reduceBrackets(self) -> Formula:
        """Minimalizuje nawiasy w zdaniu; zakłada poprawność ich rozmieszczenia"""
        # TODO: Redukcja nawiasów w *całości* zdania

        if len(self) < 2:
            return self[:]

        reduced = self[:]

        # Deleting brackets
        while reduced[0] == "(" and reduced[-1] == ")":
            reduced = reduced[1:-1]

        diff = (len(self) - len(reduced)) / 2

        # Fill missing brackets
        opened_left = 0
        opened_right = 0
        min_left = 0
        for i in reduced:
            if i == "(":
                opened_left += 1
            elif i == ")":
                opened_right += 1
            else:
                continue
            delta_left = opened_left - opened_right
            min_left = min(min_left, delta_left)

        if self.precedenceBaked:
            new_baked = apply_on_keys(
                self.precedenceBaked, lambda x: x - (diff + min_left)
            )
        else:
            new_baked = {}

        right = opened_left - opened_right - min_left
        return Formula(
            -min_left * ["("] + reduced + right * [")"], self.formal_system, new_baked
        )

    @staticmethod
    def static_calcPrecedenceVal(
        connective: str, precedence: dict[str, int], lvl: int = 0, prec_div: int = None
    ) -> float:
        if prec_div is not None:
            return lvl + precedence[connective] / prec_div
        else:
            return lvl + precedence[connective] / max(precedence.values()) + 1

    def getLowest(
        self, dictionary: dict[int, float], precedence: dict[str, int] = None
    ):
        if not dictionary:
            return None
        if precedence is None:
            precedence = self.getPrecedence()
        min_prec = min(dictionary.values())
        min_prec_indexes = (i for i, j in dictionary.items() if j == min_prec)
        max_prec = max(precedence.values())
        if min_prec == max_prec / (max_prec + 1):
            return min(min_prec_indexes)
        else:
            return max(min_prec_indexes)

    def calcPrecedenceVal(
        self, connective: str, lvl: int = 0, prec_div: int = None
    ) -> float:
        precedence = self.getPrecedence()
        return self.static_calcPrecedenceVal(connective, precedence, lvl, prec_div)

    def readPrecedence(self, precedence: dict[str, int] = None) -> dict[int, float]:
        """
        Oblicza, bądź zwraca informacje o sile spójników w danym zdaniu. *Powinno być przywołane przed dowolnym użyciem precedenceBaked*
        W testach używać można argument opcjonalny, aby nie odwoływać się do

        :param precedence: Siła wiązania spójników (podane same typy) - im wyższa wartość, tym mocniej wiąże, optional
        :type precedence: dict[str, int]
        :return: Indeksy spójników oraz siła wiązania - im wyższa wartość, tym mocniej wiąże
        :rtype: dict[str, float]
        """
        if precedence is None:
            if self.precedenceBaked:
                return self.precedenceBaked
            precedence = self.getPrecedence()

        self.precedenceBaked = OrderedDict()

        lvl = 0
        prec_div = max(precedence.values()) + 1
        for i, t in enumerate(self.getTypes()):
            if t == "(":
                lvl += 1
            elif t == ")":
                lvl -= 1
            elif t in precedence:
                self.precedenceBaked[i] = self.static_calcPrecedenceVal(
                    t, precedence, lvl, prec_div
                )

        return self.precedenceBaked

    def splitByIndex(self, index: int):
        """
        Dzieli zdanie na dwa na podstawie podanego indeksu.
        """
        p_left, p_right = slice_dict_by_key(self.precedenceBaked, index)
        left = (
            Formula(self[:index], self.formal_system, p_left)
            .reduceBrackets()
            .reduceBrackets()
            if self[:index]
            else None
        )
        right = (
            Formula(self[index + 1 :], self.formal_system, p_right)
            .reduceBrackets()
            .reduceBrackets()
            if self[index + 1 :]
            else None
        )
        return left, right

    def getMainConnective(self, precedence: dict[str, int] = None) -> Union[int, None]:
        prec = self.readPrecedence(precedence)

        if len(prec) == 0:
            return None
        return self.getLowest(prec, precedence)

    def getComponents(
        self, precedence: dict[str, int] = None
    ) -> tuple[Optional[str], Optional[tuple[Formula, Formula]]]:
        """
        Na podstawie kolejności wykonywania działań wyznacza najwyżej położony spójnik oraz dzieli zdanie na dwa części.
        Zwraca None gdy nie udało się znaleźć spójnika

        :param precedence: Siła wiązania spójników (podane same typy) - im wyższa wartość, tym mocniej wiąże, optional
        :type precedence: dict[str, int]
        :return: Główny spójnik oraz powstałe zdania; None jeśli dane zdanie nie istnieje
        :rtype: tuple[Optional[str], Optional[tuple[Formula, Formula]]]
        """
        sentence = self.reduceBrackets()
        con_index = self.getMainConnective(precedence)
        if con_index is None:
            return None, None
        return sentence[con_index], sentence.splitByIndex(con_index)

    def getNonNegated(self) -> Formula:
        """
        Zwracane zdanie jest konceptualnie podobne do literału, ale rozszerzone na całe zdanie. W skrócie redukowane są wszystkie negacje obejmujące całe zdanie
        """
        conn, new = self.getComponents()
        if not conn or not conn.startswith("not"):
            return self.reduceBrackets()
        else:
            return new[1].getNonNegated()

    def isLiteral(self) -> bool:
        main = self.getMainConnective()
        return main is None or (main == 0 and len(self.readPrecedence()) == 1)

    # Overwriting list methods

    def __hash__(self):
        return hash(" ".join(self.getUnique()))

    def __eq__(self, o) -> bool:
        if isinstance(o, Formula):
            return self.getUnique() == o.getUnique()
        else:
            return list(self) == o

    def __add__(self, x: Union[Formula, list[str]]) -> Formula:
        return Formula(super().__add__(x), self.formal_system)

    def __mul__(self, n: int) -> Formula:
        return Formula(super().__mul__(n), self.formal_system)

    def copy(self) -> Formula:
        return Formula(super().copy(), self.formal_system, self.precedenceBaked)

    def __repr__(self) -> str:
        return " ".join(self)

    def __rmul__(self, n: int) -> Formula:
        return Formula(super().__rmul__(n), self.formal_system)

    def __str__(self) -> str:
        return self.getReadable()

    @overload
    def __getitem__(self, key: SupportsIndex) -> Token: ...
    @overload
    def __getitem__(self, key: slice) -> Formula: ...
    def __getitem__(self, key):
        if isinstance(key, slice):
            return Formula(super().__getitem__(key), self.formal_system)
        elif isinstance(key, int):
            return super().__getitem__(key)
