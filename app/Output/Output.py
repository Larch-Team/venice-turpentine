import typing as tp
from collections import namedtuple

Sentence = tp.NewType("Sentence", list[str])
PrintedTree = namedtuple('PrintedTree', ('sentences', 'children', 'closer'))

def align(strings: list[str], length: int = None) -> list[str]:
    """Generates additional spaces at the end of string which makes them all have the same length
    
    TODO: NEEDS TO BE VERIFIED!!!
    """
    if not length:
        length = max((len(i) for i in strings))
    return ["".join((i, " "*(length-len(i)))) for i in strings]