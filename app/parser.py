from typing import Any, Iterable, Union
from dataclasses import dataclass
from abc import ABC, abstractmethod
import sly

@dataclass
class Rule(object):
    context: dict[str, Any]
    lexem: str
    toktype: str

# def dictSortedValues(d: dict[str, Any]):
#     return [i for _,i in sorted(d.items(), key=lambda x: x[0])]

class Lexicon(object):
    STACK = []

    def __init__(self) -> None:
        super().__init__()
        self.rules = set()

    def __setattr__(self, token: str, lexems: Union[str, Iterable[str]]) -> None:
        if isinstance(lexems, str):
            self.rules.add(Rule(self.STACK.copy(), lexems, token))
        elif isinstance(Iterable):
            for i in lexems:
                self.__setattr__(token, i) 


    def _lexicon_build(self, **kwargs: dict[str, Any]):
        used = {}
        
        # skompiluj listę used na podstawie kwargs i constraints danych reguł

        class _Lex(sly.Lexer):
            tokens = set(used.keys())

        # Dodać do lexiconu rzeczy z used

class RuleConstraint(ABC):

    @abstractmethod
    def __init__(self, tag: Any) -> None:
        super().__init__()
        self.tag = tag


    def __enter__(self) -> None:
        Lexicon.STACK.append((type(self).__name__, self.tag))
        return

    def __exit__(self) -> None:
        Lexicon.STACK.pop()
        return