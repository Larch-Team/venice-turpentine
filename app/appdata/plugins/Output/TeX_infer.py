"""
Konwertuje dowód do kodu TeX, który, z pomocą paczki proof.sty dostępnej na stronie http://research.nii.ac.jp/~tatsuta/proof-sty.html, może zostać wyrenderowany do dowodu stylizowanego na rachunek sekwentów.
"""
import typing as tp
import plugins.Output.__utils__ as utils

SOCKET = 'Output'
VERSION = '0.2.0'

TEX_DICTIONARY = {
    "falsum"    :   "\\bot",
    "turnstile" :   "\\Rightarrow",
    "imp"       :   "\\rightarrow",
    "and"       :   "\\land",
    "or"        :   "\\lor",
    "sep"       :   ",",
    "^"         :   "\\ast",
    "("         :   "(",
    ")"         :   ")",
}

def convert_token(token: str) -> str:
    """Returns a readable version of a token

    :param sentence: Transcribed sentence
    :type sentence: Sentence
    :return: Transcribed string
    :rtype: str
    """
    return TEX_DICTIONARY.get(token.split('_')[0], token.split('_')[-1])

def get_readable(sentence: utils.Sentence) -> str:
    """Zwraca zdanie w czytelnej formie

    :param sentence: Zdanie do transformacji
    :type sentence: Sentence
    :return: Przepisane zdanie
    :rtype: str
    """
    return " ".join(convert_token(i) for i in sentence)

def write_tree(tree: utils.PrintedProofNode) -> list[str]:
    """
    Zwraca drzewiastą reprezentację dowodu

    :param tree: Drzewo do konwersji
    :type tree: utils.PrintedProofNode
    """
    return [_write_tree(tree.sentence, tree.children)]

def _gen_infer(s1, s2):
    return "\\infer{%s}{%s}" % (s1, s2)

def _write_tree(sentence, children) -> str:
    if children is None:
        return _gen_infer(get_readable(sentence), "")
    else:
        return _gen_infer(get_readable(sentence), " & ".join((_write_tree(i.sentence, i.children) for i in children)))
