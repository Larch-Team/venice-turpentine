from typing import Any, Iterable, Union
from dataclasses import dataclass
from abc import ABC, abstractmethod
from collections import namedtuple
import sly

LITERALS = {'(', ')'}

LexerRule = namedtuple('LexerRule', ('constraints', 'token', 'lexems'))

class LrchLexerError(Exception):
    pass


class Lexicon(object):
    STACK = []

    def __init__(self) -> None:
        super().__init__()
        self.rules = set()
        self.is_lowercase = False

    def __setitem__(self, token: str, lexems: Union[str, Iterable[str]]) -> None:
        if isinstance(lexems, str):
            self.rules.add(LexerRule(self.STACK.copy(), token, [lexems]))
            self.needs_casing |= lexems.isupper()
        elif isinstance(Iterable):
            self.rules.add(LexerRule(self.STACK.copy(), token, lexems))
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

        used = self._join_rules(self._filter_constraints(lex, kwargs))
        used = ((key, r"|".join((f"({i})" for i in val)))
                for key, val in used.items())
        for token, lexems in sorted(used, key=lambda x: len(x[1]), reverse=True):
            setattr(_Lex, token, lexems)
            _Lex.tokens.add(token)

        self.lexer = _Lex()

    @staticmethod
    def _filter_constraints(lex: Lexicon, const: dict[str, Any]) -> Iterable[tuple[str, tuple[str]]]:
        for constraints, token, lexems in lex.rules:
            if all((i in const.items() for i in constraints if i[0] != 'findnew')):
                yield token, lexems

    @staticmethod
    def _join_rules(rules: Iterable[tuple[str, tuple[str]]]) -> dict[str, tuple[str]]:
        d = {}
        for token, lexems in rules:
            if token in d:
                d[token].extend(lexems)
            else:
                d[token] = lexems
        return d

    def tokenize(self, formula: str):
        if not self.needs_casing:
            formula = formula.lower()
        
        sentence = []
        for i in self.lexer.tokenize(formula):
            if i.value in LITERALS:
                sentence.append(i.value)
            else:
                sentence.append(f"{}")


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