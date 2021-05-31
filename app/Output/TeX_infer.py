import typing as tp
import Output as utils

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
    """Returns a readable version of the sentence

    :param sentence: Transcribed sentence
    :type sentence: Sentence
    :param lexem_parser: Transforms tokens into lexems to use (get_lexem for example)
    :type lexem_parser: callable
    :return: Transcribed string
    :rtype: str
    """
    assert isinstance(sentence, list)
    readable = []
    for lexem in (lexem_parser(i) for i in sentence):
        if len(lexem) > 1:
            readable.append(f" {lexem} ")
        else:
            readable.append(lexem)
    return "".join(readable).replace("  ", " ")

def write_tree(tree: utils.PrintedTree, lexem_parser: callable) -> list[str]:
    """
    Returns a tree/table representation of the whole proof
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
        return "\\infer{%s}{%s}" % (_translate(sentences[0], lexem_parser), 
            _write_tree(sentences[1:], children, lexem_parser))
    elif children is not None:
        return " & ".join((_write_tree(i.sentences, i.children, lexem_parser) for i in children))
    else:
        return ""