import typing as tp
from collections import namedtuple
import close
from sentence import Sentence
from misc import get_plugin_path

PrintedTree = namedtuple('PrintedTree', ('sentences', 'children', 'closer'))