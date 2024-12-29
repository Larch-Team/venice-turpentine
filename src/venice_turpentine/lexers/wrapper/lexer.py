import re
from collections import Counter
from dataclasses import dataclass
from typing import Any, Iterable, TypeVar

import ply.lex as plex
from exrex import generate, getone
from ply.lex import LexError

from ...core.formula import Formula
from ...core.token import Token
from ...exceptions import LexiconError

T = TypeVar("T")
V = TypeVar("V")


@dataclass(init=True, repr=False, frozen=True)
class LexerRule:
    constraints: tuple[
        tuple[str, str], ...
    ]  # (constraint, tag) - tag jest używany przez use_language
    type_: str
    lexems: tuple[str, ...]


def join_items(tuples: Iterable[tuple[T, V]]) -> dict[T, tuple[V, ...]]:
    """Grupuje elementy w słownik według klucza"""
    d: dict[T, list[V]] = {}
    for k, v in tuples:
        if k in d:
            d[k].append(v)
        else:
            d[k] = [v]
    return {k: tuple(v) for k, v in d.items()}


def sep_items(tuples: dict[T, V | Iterable[V]]) -> list[tuple[T, V]]:
    """Odwrotność join_items, rozdziela elementy do krotek"""
    d = []
    for k, v in tuples.items():
        if isinstance(v, Iterable):
            d.extend([(k, i) for i in v])
        else:
            d.append((k, v))
    return d


class Lexicon(object):
    """Klasa reprezentująca słownik budowanego leksera"""

    STACK: list[tuple[str, str]] = []
    LITERALS = {"(", ")"}

    def __init__(self) -> None:
        super().__init__()
        self.rules: set[LexerRule] = set()
        self.needs_casing = False

    def __setitem__(self, type_: str, lexems: str | Iterable[str]) -> None:
        if isinstance(lexems, str):
            self.rules.add(LexerRule(tuple(self.STACK), type_, (lexems,)))
            self.needs_casing |= lexems.isupper()
        elif isinstance(lexems, Iterable):
            self.rules.add(LexerRule(tuple(self.STACK), type_, tuple(lexems)))
            self.needs_casing |= any((i.isupper() for i in lexems))

    def compile(self, **constraints) -> "BuiltLexer":
        return BuiltLexer(self, **constraints)


class BuiltLexer(object):

    def __init__(self, lex: Lexicon, **kwargs: dict[str, Any]) -> None:
        super().__init__()
        self.needs_casing = lex.needs_casing
        self.LITERALS = lex.LITERALS
        self.find_new = self._get_find_new(lex)

        filtered_rules = list(self._filter_constraints(lex, kwargs))
        lex_re = [(i, j) for i, j, _ in filtered_rules]
        gen_re = [(i, j) for i, j, for_generation in filtered_rules if for_generation]

        self.lexer_regexes = {
            key: self._regex_from_list(val)
            for key, val in self._join_rules(lex_re).items()
        }
        self.generator_regexes = {
            key: self._regex_from_list(val)
            for key, val in self._join_rules(gen_re).items()
        }

        class _Lex:
            _master_re = re
            literals = lex.LITERALS
            tokens = [i for i in self.lexer_regexes]
            t_ignore = " \t"

            def __init__(self) -> None:
                self.num_count = 0
                self.build()

            def t_error(self, t):
                raise LexiconError(f"{t.value} is not tokenizable")

            def build(self, **kwargs):
                self.lexer = plex.lex(object=self, **kwargs)

            def tokenize(self, s: str):
                self.lexer.input(s)
                while i := self.lexer.token():
                    if i.value in self.literals:
                        yield Token.literal(i.value)
                    else:
                        yield Token(i.type, i.value)

        for type_, lexems in sorted(
            self.lexer_regexes.items(), key=lambda x: len(x[1]), reverse=True
        ):
            setattr(_Lex, f"t_{type_}", lexems)

        self.lexer = _Lex()

    @staticmethod
    def _regex_from_list(lst: Iterable[str]):
        return r"|".join((f"({i})" for i in lst))

    @staticmethod
    def _filter_constraints(
        lex: Lexicon, satisfied: dict[str, Any]
    ) -> Iterable[tuple[str, str, bool]]:
        for rule in lex.rules:
            rewritten_satisfied = sep_items(satisfied)
            if all(
                (
                    i in rewritten_satisfied
                    for i in rule.constraints
                    if i[0] != "find_new"
                )
            ):
                for lexem in rule.lexems:
                    yield rule.type_, lexem, all(
                        (i[0] != "no_generation" for i in rewritten_satisfied)
                    )

    @staticmethod
    def _get_find_new(lex: Lexicon) -> set[str]:
        """Zwraca zbiór wszystkim typów, które określono w kontekście find_new"""
        s = set()
        for rule in lex.rules:
            if any((i[0] == "find_new" for i in rule.constraints)):
                s.add(rule.type_)
        return s

    @staticmethod
    def _join_rules(rules: Iterable[tuple[str, str]]) -> dict[str, list[str]]:
        """
        Łączy duplikaty reguł

        :param rules: pierwotny ciąg reguł
        :type rules: Iterable[tuple[str, tuple[str]]]
        :return: reguły po złączeniu
        :rtype: dict[str, tuple[str]]
        """
        d = join_items(rules)
        return {k: sorted(i, reverse=True) for k, i in d.items()}

    def tokenize(self, formula: str) -> list[Token]:
        """
        Dla danego ciągu znaków generuje listę tokenów

        :param formula: Ciąg znaków do przetworzenia
        :type formula: str
        :raises LexiconError: Nie znaleziono tokenu
        :return: Lista tokenów
        :rtype: list[Token]
        """
        if not self.needs_casing:
            formula = formula.lower()

        try:
            sentence = list(self.lexer.tokenize(formula))
        except LexError as e:
            raise LexiconError from e
        else:
            return sentence

    def generate(self, sentence: Formula, type_: str) -> Token:
        """
        Generuje nowy token dla danego typu

        :param sentence: Zdanie, w którym zostanie użyty
        :type sentence: Formula
        :param type_: Typ tokenu
        :type type_: str
        :return: Token w formie `[typ]_[leksem]`
        :rtype: str
        """
        if type_ not in self.generator_regexes:
            raise LexiconError(f"Type {type_} is not generatable")
        if type_ in self.find_new:
            new_lexems = generate(self.generator_regexes[type_])
            used_lexems = sentence.getLexems()

            try:
                while (new_lex := next(new_lexems)) in used_lexems:
                    pass
            except StopIteration:
                raise LexiconError(f"Need more lexems for the {type_} type") from None
            else:
                return Token(type_, new_lex)

        else:
            counted = Counter(
                (token for t, token in sentence.getItems() if t == type_)
            ).items()
            try:
                new_lex = max(counted, key=lambda x: x[1])[0]
            except ValueError:
                return Token(type_, getone(self.generator_regexes[type_]))
            else:
                return Token(type_, new_lex)
