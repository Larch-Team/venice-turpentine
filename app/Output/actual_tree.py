"""
Plugin printujący drzewo z pomocą modułu anytree. Drzewo wbrew pewnym logicznym intuicjom rozrasta się w poziomie.

Autorzy:
    Michał Gajdziszewski - autor skryptu wzorcowego
    Jakub Dakowski (@PogromcaPapai) - autor implementacji
"""
import Output as utils
from anytree import Node, RenderTree

SOCKET = 'Output'
VERSION = '0.0.1'


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
    Zwraca drzewiastą reprezentację drzewa
    """
    strs = []
    for pre, fill, node in RenderTree(get_nodes(tree.sentences, lexem_parser, tree.children)[0]):
        strs.append(f"{pre}{node.name}".rstrip('\n'))
    return strs


def get_nodes(sentences: list[str], lexem_parser: callable, children: list[utils.PrintedTree]) -> list[Node]: 
    """Zwraca listę dzieci do dania do drzewa.
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