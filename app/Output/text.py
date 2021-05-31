"""
WRITE_TREE DOES NOT WORK PROPERLY

"""
import typing as tp
import Output as utils

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
    Returns a tree/table representation of the whole proof
    """
    return _write_tree(tree, lexem_parser)[0]
    
def _write_tree(tree: utils.PrintedTree, lexem_parser: callable) -> tuple[list[str], int]:
    """A technical function used to generate a table representation of the whole proof. USE `write_tree` INSTEAD.

    :param tree: Tree to print
    :type tree: utils.PrintedTree
    :param width: [description]
    :type width: int
    :param lexem_parser: an object able to transcribe tokens into lexems
    :type lexem_parser: callable
    :return: List of lines to print, width
    :rtype: list[str], int
    """
    DELIMITER = '  \u2016  '
    delilen = len(DELIMITER)

    # Get width of current node's sentences
    parsed = [get_readable(s, lexem_parser) for s in tree.sentences]
    width = max((len(s) for s in parsed))

    # _write_tree for all the children
    if tree.children:
        children = []
        widths = []
        
        # Getting children
        for i in tree.children:
            s, w = _write_tree(i, lexem_parser)
            children.append(s)
            widths.append(w)
        
        # Children length correction
        sen_am = max((len(s) for s in children))
        children = [i+['']*(sen_am - len(i)) for i in children]

        # Children formating
        if sum(widths)+delilen*len(widths)-delilen >= width:
            width = delilen*len(widths)-delilen
        else:
            symb_to_use = width-delilen*len(widths)-delilen
            children = [utils.align(*col) for col in zip(children, widths)]
        append = [DELIMITER.join(i) for i in zip(*children)]

    else:
        if len(tree.closer)>width:
            width = len(tree.closer)
            append = [tree.closer]
        else:
            append = [tree.closer+" "*(width - len(tree.closer))]
    
    # Align the sentences
    sentences = utils.align(parsed, width)

    return sentences+append, width