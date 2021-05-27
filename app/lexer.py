from abc import ABC, abstractmethod
from collections import namedtuple, Counter
from re import escape as resc, compile
from typing import Any, Iterable, Union, NewType
from sentence import Sentence
from exrex import generate, getone
import re

import ply.lex as plex
from ply.lex import LexError

token_type = NewType('Token', str)

LexerRule = namedtuple('LexerRule', ('constraints', 'type_', 'lexems'))

class LrchLexerError(Exception):
    pass


def join_items(tuples):
    d = {}
    for k, v in tuples:
        if k in d:
            d[k].extend(v)
        else:
            d[k] = list(v)
    return {k:tuple(v) for k,v in d.items()}

def sep_items(tuples):
    d = []
    for k, v in tuples.items():
        if isinstance(v, (tuple, list)):
            d.extend([(k,i) for i in v])
        else:
            d.append((k,v))
    return tuple(d)

class Lexicon(object):
    STACK = []
    LITERALS = {'(', ')'}

    def __init__(self) -> None:
        super().__init__()
        self.rules = set()
        self.needs_casing = False

    def __setitem__(self, type_: str, lexems: Union[str, Iterable[str]]) -> None:
        if isinstance(lexems, str):
            self.rules.add(LexerRule(tuple(self.STACK), type_, (lexems,)))
            self.needs_casing |= lexems.isupper()
        elif isinstance(lexems, (list, tuple, set)):
            self.rules.add(LexerRule(tuple(self.STACK), type_, lexems))
            self.needs_casing |= any((i.isupper() for i in lexems))


class BuiltLexer(object):

    def __init__(self, lex: Lexicon, **kwargs: dict[str, Any]) -> None:
        super().__init__()
        self.needs_casing = lex.needs_casing
        self.LITERALS = lex.LITERALS

        self.find_new = self._get_find_new(lex)
        used = self._join_rules(self._filter_constraints(lex, kwargs))
        self.regexes = {key:self._regex_from_list(val) for key, val in used.items()}

        class _Lex:
            _master_re = re
            literals = lex.LITERALS
            tokens = [i.upper() for i in self.regexes]
            t_ignore = ' \t'

            def __init__(self) -> None:
                self.num_count = 0
                self.build()

            def t_error(self, t):
                raise LrchLexerError(f'{t} is not tokenizable')

            def build(self, **kwargs):
                self.lexer = plex.lex(object=self,**kwargs)

            def tokenize(self, s: str):
                self.lexer.input(s)    
                while (i := self.lexer.token()):
                    if i.value in self.literals:
                        yield i.value
                    else:
                        yield f"{i.type}_{i.value}"

        for type_, lexems in sorted(self.regexes.items(), key=lambda x: len(x[1]), reverse=True):
            setattr(_Lex, f"t_{type_.upper()}", lexems)

        self.lexer = _Lex()

    @staticmethod
    def _regex_from_list(lst: list[str]):
        return r"|".join((f"({i})" for i in lst))

    @staticmethod
    def _filter_constraints(lex: Lexicon, satisfied: dict[str, Any]) -> Iterable[tuple[str, tuple[str]]]:
        for def_constr, type_, lexems in lex.rules:
            rewritten_satisfied = sep_items(satisfied)
            if all((i in rewritten_satisfied for i in def_constr if i[0] != 'find_new')):
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
        d = join_items(rules)
        return {k:sorted(i, reverse=True) for k,i in d.items()}

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
        
        try:
            sentence = list(self.lexer.tokenize(formula))
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


    def __exit__(self, *args) -> None:
        Lexicon.STACK.pop()
        return
