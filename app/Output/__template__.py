"""
Tutaj umieść dokumentację swojego pluginu
"""
import typing as tp
import Output.__utils__ as utils

SOCKET = 'Output'
VERSION = '0.0.1'


def get_readable(sentence: utils.Sentence) -> str:
    """Returns a readable version of the sentence

    :param sentence: Transcribed sentence
    :type sentence: Sentence
    :return: Transcribed string
    :rtype: str
    """
    pass

def write_tree(tree: utils.PrintedTree) -> list[str]:
    """
    Returns a tree/table representation of the whole proof
    """
    pass