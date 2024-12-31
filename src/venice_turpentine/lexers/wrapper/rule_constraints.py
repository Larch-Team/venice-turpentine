from abc import ABC, abstractmethod
from typing import Any

from .lexer import Lexicon


class RuleConstraint(ABC):

    @abstractmethod
    def __init__(self, tag: Any) -> None:
        super().__init__()
        self.tag = tag

    def __enter__(self) -> None:
        Lexicon.STACK.append((type(self).__name__, self.tag))
        return

    def __exit__(self, *args) -> None:
        Lexicon.STACK.pop()
        return


class use_language(RuleConstraint):

    def __init__(self, arg: str) -> None:
        super().__init__(arg)


class find_new(RuleConstraint):

    def __init__(self) -> None:
        super().__init__("")


class no_generation(RuleConstraint):

    def __init__(self) -> None:
        super().__init__("")
