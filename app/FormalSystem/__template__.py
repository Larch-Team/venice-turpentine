import typing as tp
import FormalSystem as utils

SOCKET = 'FormalSystem'
VERSION = '0.0.1'


def prepare_for_proving(statement: utils.Sentence) -> utils.Sentence:
    pass

def check_contradict(branch: list[utils.Sentence], used: set[tuple[str]]) -> tp.Union[None, tuple[int, str, str]]:
    pass

def check_syntax(tokenized_statement: utils.Sentence) -> tp.Union[str, None]:
    """Should return string description of the problem in syntax"""
    pass

def get_rules() -> dict[str, str]:
    """Returns the names and documentation of the rules"""
    pass

def get_needed_context(rule_name: str) -> tuple[utils.ContextDef]:
    """Returns needed arguments for the given rule"""
    pass

def get_used_types() -> tuple[str]:
    pass

# TODO: Poprawić oznaczenie zwracanego typu
def use_rule(name: str, branch: list[utils.Sentence], used: set[utils.Sentence], context: dict[str, tp.Any], auto: bool) -> tuple[tp.Union[tuple[tuple[utils.Sentence]], None], int]:
    """Uses a rule of the given name on the provided branch.
        Context allows to give the FormalSystem additional arguments. 
        Use `self.access('FormalSystem').get_needed_context(rule)` to check for needed context

    :param name: Rule name
    :type name: str
    :param branch: List of sentences in a branch
    :type branch: list[utils.Sentence]
    :param used: Set of sentences that were already used
    :type used: set[utils.Sentence]
    :param context: Additional arguments
    :type context: dict[str,tp.Any]
    :return: Generated tuple structure with the sentences and sentence ID
    :rtype: tuple[tp.Union[tuple[tuple[utils.Sentence]], None], int]
    """
    pass
