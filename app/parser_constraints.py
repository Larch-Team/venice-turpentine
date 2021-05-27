from parser import RuleConstraint
from typing import Iterable

class UseLanguage(RuleConstraint):

    def __init__(self, *args: Iterable[str]) -> None:
        super().__init__(args)
