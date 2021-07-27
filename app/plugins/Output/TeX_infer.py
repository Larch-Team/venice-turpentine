"""
Konwertuje dowód do kodu TeX, który, z pomocą paczki proof.sty dostępnej na stronie http://research.nii.ac.jp/~tatsuta/proof-sty.html, może zostać wyrenderowany do dowodu stylizowanego na rachunek sekwentów.
"""
import typing as tp
import plugins.Output.__utils__ as utils

SOCKET = 'Output'
VERSION = '0.0.1'

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

def get_readable(sentence: utils.Sentence) -> str:
    """Zwraca zdanie w czytelnej formie

    :param sentence: Zdanie do transformacji
    :type sentence: Sentence
    :return: Przepisane zdanie
    :rtype: str
    """
    assert isinstance(sentence, utils.Sentence)
    readable = []
    for lexem in sentence.getReadable():
        if len(lexem) > 1:
            readable.append(f" {lexem} ")
        else:
            readable.append(lexem)
    return "".join(readable).replace("  ", " ")

def write_tree(tree: utils.PrintedTree) -> list[str]:
    """
    Zwraca drzewiastą reprezentację dowodu

    :param tree: Drzewo do konwersji
    :type tree: utils.PrintedTree
    :return: Dowód w liście
    :rtype: list[str]
    """
    return [_write_tree(tree.sentences, tree.children)]


def _translate(s: utils.Sentence):
    readable = [TEX_DICTIONARY.get(t, l) for t, l in s.getItems()]
    return " ".join(readable)


def _write_tree(sentences, children) -> str:
    if len(sentences)>0:
        return _gen_infer(_translate(sentences[0]), _write_tree(sentences[1:], children))
    elif children is not None:
        return " & ".join((_write_tree(i.sentences, i.children) for i in children))
    else:
        return ""

def _gen_infer(s1, s2):
    return "\\infer{%s}{%s}" % (s1, s2)