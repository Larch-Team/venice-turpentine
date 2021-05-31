import typing as tp
import Output as utils

SOCKET = 'Output'
VERSION = '0.0.1'


def get_readable(sentence: utils.Sentence, lexem_parser: callable) -> str:
    """Returns a readable version of the sentence

    :param sentence: Transcribed sentence
    :type sentence: Sentence
    :param lexem_parser: Transforms tokens into lexems to use (get_lexem for example)
    :type lexem_parser: callable
    :return: Transcribed string
    :rtype: str
    """
    pass

def write_tree(tree: utils.PrintedTree, lexem_parser: callable) -> list[str]:
    """
    Returns a tree/table representation of the whole proof
    """
    pass