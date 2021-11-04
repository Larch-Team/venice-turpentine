"""
Konwertuje dowód do kodu TeX dla pakietu forest. Należy go zaimportować przed użyciem.
"""
import plugins.Output.__utils__ as utils

SOCKET = 'Output'
VERSION = '0.2.0'

TEX_DICTIONARY = {
    "falsum"    :   "\\bot",
    "not"       :   "\\neg",
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
    style = r"\forestset{smullyan tableaux/.style={for tree={math content},where n children=1{!1.before computing xy={l=\baselineskip},!1.no edge}{},},}"
    return [style, r'\begin{forest}', 'smullyan tableaux', _write_tree(tree.sentence, tree.children, tree.closer), r'\end{forest}']

def _write_tree(sentence, children, close) -> str:
    if children is not None:
        return "[%s\n%s]" % (get_readable(sentence), "\n".join((_write_tree(i.sentence, i.children, i.closer) for i in children)))

    if close:
        return "[%s [%s]]" % (get_readable(sentence), close.replace('XXX', '\\times').replace(',', '{,}'))
    else:
        return "[%s]" % (get_readable(sentence))
