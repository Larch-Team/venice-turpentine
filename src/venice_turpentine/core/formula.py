from __future__ import annotations

from collections import OrderedDict
from functools import cached_property
from typing import Any, Callable, Optional, SupportsIndex, TypeVar, Union, overload

from ..formal_systems import FormalSystem
from .token import Token

T = TypeVar("T")
V = TypeVar("V")
Z = TypeVar("Z")

def apply_on_keys(dictionary: dict[T, Z], op: Callable[[T], V]) -> dict[V, Z]:
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
        precedenceBaked: Optional[dict[int, float]] = None,
    ):
        self.formal_system = formal_system
        # Indeksy spójników oraz siła wiązania - im wyższa wartość, tym mocniej wiąże
        self.precedenceBaked = precedenceBaked or {}
        super().__init__(token_list)

    # MARK: Getters

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

    def isLiteral(self) -> bool:
        main = self.getMainConnective()
        return main is None or (main == 0 and len(self.precedence()) == 1)

    # MARK: Kolejność wykonywania działań

    def calcPrecedenceVal(
        self, connective: str, lvl: int = 0
    ) -> float:
        return lvl + self.formal_system.operator_precedence[connective] / self.formal_system.operator_precedence_scale
    
    def precedence(self) -> dict[int, float]:
        """Oblicza siłę wiązania spójników w zdaniu, zwraca słownik indeksów spójników i ich sił wiązania"""
        if self.precedenceBaked:
            return self.precedenceBaked
        self.precedenceBaked = {}

        lvl = 0
        for i, t in enumerate(self.getTypes()):
            if t == "(":
                lvl += 1
            elif t == ")":
                lvl -= 1
            elif t in self.formal_system.operator_precedence:
                self.precedenceBaked[i] = self.calcPrecedenceVal(
                    t, lvl
                )

        return self.precedenceBaked

    # MARK: Usuwanie nawiasów

    @staticmethod
    def _fixPrecedence_reduceBrackets(precedenceBaked: dict[int, float], removed_brackets_count: int, lowest_unopened_left: int) -> dict[int, float]:
        return apply_on_keys(
                precedenceBaked, lambda x: x - (removed_brackets_count - lowest_unopened_left)
            )

    def reduceBrackets(self) -> Formula:
        """Minimalizuje nawiasy w zdaniu; zakłada poprawność ich rozmieszczenia"""

        if len(self) < 2:
            return self[:]

        reduced = self[:]

        # Deleting brackets
        removed_brackets_count = 0
        while reduced[0] == Token.LEFT_BRACKET() and reduced[-1] == Token.RIGHT_BRACKET():
            reduced = reduced[1:-1]
            removed_brackets_count += 1

        # Poszukuje
        # Wprowadzone aby obsługiwać przypadki typu "((A))or((A))"
        opened_left = 0
        opened_right = 0
        lowest_unopened_left = 0
        for i in reduced:
            if i == Token.LEFT_BRACKET():
                opened_left += 1
            elif i == Token.RIGHT_BRACKET():
                opened_right += 1
            else:
                continue
            unopened_left =  opened_right - opened_left
            lowest_unopened_left = max(lowest_unopened_left, unopened_left)

        unclosed_right = opened_left - opened_right + lowest_unopened_left
        return Formula(
            lowest_unopened_left * [Token.LEFT_BRACKET()] + reduced + unclosed_right * [Token.RIGHT_BRACKET()],
            self.formal_system, self._fixPrecedence_reduceBrackets(self.precedenceBaked, removed_brackets_count, lowest_unopened_left)
        )

    # MARK: Operacje na zdaniu

    def getMainConnective(self) -> int | None:
        """
        Zwraca indeks głównego spójnika w zdaniu. None jeśli zdanie jest literałem.
        W przypadku równych sił wiązania zwraca indeks najbardziej na prawo, z wyjątkiem jednoargumentowych spójników
        """
        if not self.precedence():
            return None
        
        min_prec = min(self.precedence().values())
        min_prec_indexes = [i for i, j in self.precedence().items() if j == min_prec]
        
        # Spójniki jednoargumentowe jako jedyne działają "od prawej"
        if all(self[i].type_ in self.formal_system.unary_operators for i in min_prec_indexes):
            return min(min_prec_indexes)
        else:
            return max(min_prec_indexes)

    def splitByIndex(self, index: int) -> tuple[Formula | None, Formula | None]:
        """Dzieli zdanie na dwa na podstawie podanego indeksu. Zwraca lewą i prawą część"""
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

    # Not finished

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
        Redukuje negacje obejmujące całość zdania
        """
        conn, new = self.getComponents()
        if not conn or not conn.startswith("not"):
            return self.reduceBrackets()
        else:
            return new[1].getNonNegated()

    # MARK: Overwriting list methods

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
        return f'Formula[{" ".join(self.getLexems())}]'

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
