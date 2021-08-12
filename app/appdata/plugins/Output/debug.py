"""
Plugin printujący drzewo z pomocą modułu anytree. Drzewo wbrew pewnym logicznym intuicjom rozrasta się w poziomie.
Printuje zdania z informacją o typie.

Autorzy:
    Michał Gajdziszewski - autor skryptu wzorcowego
    Jakub Dakowski (@PogromcaPapai) - autor implementacji
"""
import plugins.Output.__utils__ as utils
from anytree import RenderTree, Node

SOCKET = 'Output'
VERSION = '0.0.1'


def get_readable(sentence: utils.Sentence) -> str:
    """Konwertuje tokeny do formy <typ_leksem>

    :param sentence: Zdanie do transformacji
    :type sentence: Sentence
    :return: Przekonwertowane zdanie
    :rtype: str
    """
    assert isinstance(sentence, utils.Sentence)
    return "<"+"> <".join(sentence)+">"

def write_tree(tree: utils.PrintedProofNode) -> list[str]:
    """
    Zwraca drzewiastą reprezentację dowodu

    :param tree: Drzewo do konwersji
    :type tree: utils.PrintedProofNode
    :return: Dowód w liście
    :rtype: list[str]
    """
    return [
        f"{pre}{node.name}".rstrip('\n')
        for pre, _, node in RenderTree(
            get_nodes(tree.sentence, tree.children)[0]
        )
    ]


def get_nodes(sentence: list[str], children: list[utils.PrintedProofNode]) -> list[Node]: 
    """Zwraca listę dzieci do dodania do drzewa.
    Jeżeli istnieją jeszcze zdania w sentence, to mają one pierwszeństwo. W innym przypadku wyliczane są dzieci.

    :param sentence: PrintedProofNode.sentence
    :type sentence: list[str]
    :param children: PrintedProofNode.children
    :type children: list[PrintedTree]
    :return: Lista dzieci do dodania do węzła
    :rtype: list[Node]
    """
    ch = sum((get_nodes(child.sentence, child.children) for child in children), []) if children else []
    return [Node(get_readable(sentence), children=ch)]