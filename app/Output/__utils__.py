import typing as tp
from collections import namedtuple
import close
from sentence import Sentence

PrintedTree = namedtuple('PrintedTree', ('sentences', 'children', 'closer'))