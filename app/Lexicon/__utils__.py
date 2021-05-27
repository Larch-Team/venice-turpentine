from parser import RuleConstraint
from typing import Iterable

# Rule Constraints

class use_language(RuleConstraint):

    def __init__(self, *args: Iterable[str]) -> None:
        super().__init__(args)

class find_new(RuleConstraint):

    def __init__(self) -> None:
        super().__init__('')