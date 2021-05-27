from abc import ABC, abstractmethod
from collections import namedtuple, Counter
from re import escape as resc, compile
from typing import Any, Iterable, Union, NewType
from sentence import Sentence
from exrex import generate, getone

import sly
from sly.lex import LexError

LITERALS = {'(', ')'}

token_type = NewType('Token', str)

LexerRule = namedtuple('LexerRule', ('constraints', 'type_', 'lexems'))

class LrchLexerError(Exception):
    pass


class Lexicon(object):
    STACK = []

    def __init__(self) -> None:
        super().__init__()
        self.rules = set()
        self.is_lowercase = False

    def __setitem__(self, type_: str, lexems: Union[str, Iterable[str]]) -> None:
        if isinstance(lexems, str):
            self.rules.add(LexerRule(self.STACK.copy(), type_, [lexems]))
            self.needs_casing |= lexems.isupper()
        elif isinstance(Iterable):
            self.rules.add(LexerRule(self.STACK.copy(), type_, lexems))
            self.needs_casing |= any((i.isupper() for i in lexems))


class BuiltLexer(object):

    def __init__(self, lex: Lexicon, **kwargs: dict[str, Any]) -> None:
        super().__init__()
        self.needs_casing = lex.needs_casing

        class _Lex(sly.Lexer):
            literals = LITERALS
            tokens = set()

            def error(self, t):
                raise LrchLexerError(f'{t} is not tokenizable')

        self.find_new = self._get_find_new(lex)
        used = self._join_rules(self._filter_constraints(lex, kwargs))
        self.regexes = {key:self._regex_from_list(val) for key, val in used.items()}

        for type_, lexems in sorted(self.regexes.items(), key=lambda x: len(x[1]), reverse=True):
            setattr(_Lex, type_, lexems)
            _Lex.tokens.add(type_)

        self.lexer = _Lex()

    @staticmethod
    def _regex_from_list(lst: list[str]):
        return r"|".join((f"({resc(i)})" for i in lst))

    @staticmethod
    def _filter_constraints(lex: Lexicon, const: dict[str, Any]) -> Iterable[tuple[str, tuple[str]]]:
        for constraints, type_, lexems in lex.rules:
            if all((i in const.items() for i in constraints if i[0] != 'find_new')):
                yield type_, lexems

    @staticmethod
    def _get_find_new(lex: Lexicon) -> set[str]:
        """Zwraca zbiór wszystkim typów, które określono w kontekście find_new"""
        # Co jeśli:
        # with find_new():
        #   lex['a'] = 'b'
        # lex['a'] = 'hgh'
        return {type_ for constraints, type_, _ in lex.rules if any((i[0] == 'find_new' for i in constraints))}

    @staticmethod
    def _join_rules(rules: Iterable[tuple[str, tuple[str]]]) -> dict[str, tuple[str]]:
        """
        Łączy duplikaty reguł

        :param rules: pierwotny ciąg reguł
        :type rules: Iterable[tuple[str, tuple[str]]]
        :return: reguły po złączeniu
        :rtype: dict[str, tuple[str]]
        """
        d = {}
        for type_, lexems in rules:
            if type_ in d:
                d[type_].extend(lexems)
            else:
                d[type_] = lexems
        return d

    def tokenize(self, formula: str) -> list[token_type]:
        """
        Dla danego ciągu znaków generuje listę tokenów

        :param formula: Ciąg znaków do przetworzenia
        :type formula: str
        :raises LrchLexerError: Nie znaleziono tokenu
        :return: Lista tokenów w formie `[typ]_[leksem]`
        :rtype: list[str]
        """
        if not self.needs_casing:
            formula = formula.lower()
        
        sentence = []
        try:
            for i in self.lexer.tokenize(formula):
                if i.value in LITERALS:
                    sentence.append(i.value)
                else:
                    sentence.append(f"{i.type}_{i.value}")
        except LexError as e:
            raise LrchLexerError(e)
        else:
            return sentence

    def generate(self, sentence: Sentence, type_: str) -> token_type:
        """
        Generuje nowy token dla danego typu

        :param sentence: Zdanie, w którym zostanie użyty
        :type sentence: Sentence
        :param type_: Typ tokenu
        :type type_: str
        :return: Token w formie `[typ]_[leksem]`
        :rtype: str
        """
        assert type_ in self.regexes, "Type doesn't exist in this Lexicon"
        if type_ in self.find_new:
            new_lexems = generate(self.regexes[type_])
            used_lexems = sentence.getLexems()

            try:
                while (new_lex := next(new_lexems)) not in used_lexems: pass
            except StopIteration:
                return None
            else:
                return f"{type_}_{new_lex}"

        else:
            counted = Counter((l for t, l in sentence.getItems() if l == type_)).items()
            try:
                new_lex = max(counted, key=lambda x: x[1])[0]
            except ValueError:
                return getone(self.regexes[type_])
            else:
                return f"{type_}_{new_lex}"          


class RuleConstraint(ABC):

    @abstractmethod
    def __init__(self, tag: Any) -> None:
        super().__init__()
        self.tag=tag


    def __enter__(self) -> None:
        Lexicon.STACK.append((type(self).__name__, self.tag))
        return


    def __exit__(self) -> None:
        Lexicon.STACK.pop()
        return
