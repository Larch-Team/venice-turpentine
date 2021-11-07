"""
Tutaj umieść dokumentację swojego pluginu
"""
import typing as tp
import plugins.Output.__utils__ as utils

SOCKET = 'Output'
VERSION = '0.2.0'

def convert_token(token: str) -> str:
    """Returns a readable version of a token

    :param sentence: Transcribed sentence
    :type sentence: Sentence
    :return: Transcribed string
    :rtype: str
    """
    pass

def get_readable(sentence: utils.Sentence) -> str:
    """Returns a readable version of the sentence

    :param sentence: Transcribed sentence
    :type sentence: Sentence
    :return: Transcribed string
    :rtype: str
    """
    pass

def write_tree(tree: utils.PrintedProofNode) -> list[str]:
    """
    Returns a tree/table representation of the whole proof
    """
    pass