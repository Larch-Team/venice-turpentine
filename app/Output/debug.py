"""
Plugin printujący drzewo z pomocą modułu anytree. Drzewo wbrew pewnym logicznym intuicjom rozrasta się w poziomie.
Printuje zdania z informacją o typie.

Autorzy:
    Michał Gajdziszewski - autor skryptu wzorcowego
    Jakub Dakowski (@PogromcaPapai) - autor implementacji
"""
import typing as tp
import Output.__utils__ as utils
from anytree import Node

SOCKET = 'Output'
VERSION = '0.0.1'


def get_readable(sentence: utils.Sentence, lexem_parser: callable) -> str:
    """Konwertuje tokeny do formy <typ_leksem>

    :param sentence: Zdanie do transformacji
    :type sentence: Sentence
    :param lexem_parser: nieużywany parametr
    :type lexem_parser: callable
    :return: Przekonwertowane zdanie
    :rtype: str
    """
    assert isinstance(sentence, utils.Sentence)
    return "<"+"> <".join(sentence)+">"

def write_tree(tree: utils.PrintedTree, lexem_parser: callable) -> list[str]:
    """
    Zwraca drzewiastą reprezentację dowodu

    :param tree: Drzewo do konwersji
    :type tree: utils.PrintedTree
    :param lexem_parser: funkcja jednoargumentowa konwertująca tokeny na leksemy
    :type lexem_parser: callable
    :return: Dowód w liście
    :rtype: list[str]
    """
    return [
        f"{pre}{node.name}".rstrip('\n')
        for pre, _, node in RenderTree(
            get_nodes(tree.sentences, lexem_parser, tree.children)[0]
        )
    ]


def get_nodes(sentences: list[str], lexem_parser: callable, children: list[utils.PrintedTree]) -> list[Node]: 
    """Zwraca listę dzieci do dodania do drzewa.
    Jeżeli istnieją jeszcze zdania w sentences, to mają one pierwszeństwo. W innym przypadku wyliczane są dzieci.

    :param sentences: PrintedTree.sentences
    :type sentences: list[str]
    :param lexem_parser: Transformuje tokeny w leksemy
    :type lexem_parser: callable
    :param children: PrintedTree.children
    :type children: list[PrintedTree]
    :return: Lista dzieci do dodania do węzła
    :rtype: list[Node]
    """
    if sentences:
        return [Node(get_readable(sentences[0], lexem_parser), children=get_nodes(sentences[1:], lexem_parser, children))]
    elif children:
        return sum((get_nodes(child.sentences, lexem_parser, child.children) for child in children), [])
    else:
        return []