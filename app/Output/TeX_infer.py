"""
Konwertuje dowód do kodu TeX, który, z pomocą paczki proof.sty dostępnej na stronie http://research.nii.ac.jp/~tatsuta/proof-sty.html, może zostać wyrenderowany do dowodu stylizowanego na rachunek sekwentów.
"""
import typing as tp
import Output.__utils__ as utils

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

def get_readable(sentence: utils.Sentence, lexem_parser: callable) -> str:
    """Zwraca zdanie w czytelnej formie

    :param sentence: Zdanie do transformacji
    :type sentence: Sentence
    :param lexem_parser: Funkcja jednoargumentowa konwertująca tokeny na leksemy
    :type lexem_parser: callable
    :return: Przepisane zdanie
    :rtype: str
    """
    assert isinstance(sentence, utils.Sentence)
    readable = []
    for lexem in (lexem_parser(i) for i in sentence):
        if len(lexem) > 1:
            readable.append(f" {lexem} ")
        else:
            readable.append(lexem)
    return "".join(readable).replace("  ", " ")

def write_tree(tree: utils.PrintedTree, lexem_parser: callable) -> list[str]:
    """
    Zwraca drzewiastą reprezentację dowodu

    :param tree: Drzewo do konwersji
    :type tree: utils.PrintedTree
    :param lexem_parser: Funkcja jednoargumentowa konwertująca tokeny na leksemy
    :type lexem_parser: callable
    :return: Dowód w liście
    :rtype: list[str]
    """
    return [_write_tree(tree.sentences, tree.children, lexem_parser)]


def _translate(s: utils.Sentence, lexem_parser: callable):
    readable = []
    for i in s:
        for typ in TEX_DICTIONARY.keys():
            if i.startswith(typ):
                readable.append(TEX_DICTIONARY[typ])
                break
        else:
            readable.append(lexem_parser(i))
    return " ".join(readable)


def _write_tree(sentences, children, lexem_parser: callable) -> str:
    if len(sentences)>0:
        return _gen_infer(_translate(sentences[0], lexem_parser), _write_tree(sentences[1:], children, lexem_parser))
    elif children is not None:
        return " & ".join((_write_tree(i.sentences, i.children, lexem_parser) for i in children))
    else:
        return ""

def _gen_infer(s1, s2):
    return "\\infer{%s}{%s}" % (s1, s2)