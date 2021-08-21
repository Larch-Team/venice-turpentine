from lexer import RuleConstraint, Lexicon
from misc import get_plugin_path

# Rule Constraints

class use_language(RuleConstraint):

    def __init__(self, arg: str) -> None:
        super().__init__(arg)

class find_new(RuleConstraint):

    def __init__(self) -> None:
        super().__init__('')

class no_generation(RuleConstraint):

    def __init__(self) -> None:
        super().__init__('')