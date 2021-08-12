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
    for lexem in sentence.getLexems():
        if len(lexem) > 1:
            readable.append(f" {lexem} ")
        else:
            readable.append(lexem)
    return "".join(readable).replace("  ", " ")

def write_tree(tree: utils.PrintedProofNode) -> list[str]:
    """
    Zwraca drzewiastą reprezentację dowodu

    :param tree: Drzewo do konwersji
    :type tree: utils.PrintedProofNode
    """
    return [_write_tree(tree.sentence, tree.children)]


def _translate(s: utils.Sentence):
    readable = [TEX_DICTIONARY.get(t, l) for t, l in s.getItems()]
    return " ".join(readable)

def _gen_infer(s1, s2):
    return "\\infer{%s}{%s}" % (s1, s2)

def _write_tree(sentence, children) -> str:
    if children is None:
        return _gen_infer(_translate(sentence), "")
    else:
        return _gen_infer(_translate(sentence), " & ".join((_write_tree(i.sentences, i.children) for i in children)))
