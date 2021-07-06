from collections import namedtuple
from typing import Any, Callable, Iterable, NewType

from anytree.node.nodemixin import NodeMixin

from sentence import Sentence

SentenceTupleStructure = NewType('SentenceTupleStructure', tuple[tuple[Sentence]])
_Rule = NewType('_Rule', NodeMixin)
ContextDef = namedtuple(
    'ContextDef', ('variable', 'official', 'docs', 'type_'))


class RuleBase(object):
    def __init__(self, name: str, symbolic: str, docs: str, context: Iterable[ContextDef]) -> None:
        super().__init__()
        self.name = name
        self.symbolic = symbolic
        self.__doc__ = docs
        self.context = context
        self.naive = None
        self.strict = None
        
    def setNaive(self, func: Callable[[list[Sentence], dict[str, Any]], SentenceTupleStructure]):
        self.naive = func
    
    def setStrict(self, func: Callable[[Sentence], SentenceTupleStructure]):
        self.strict = func
        
class Rule(RuleBase, NodeMixin):

    def __init__(self, name: str, symbolic: str, docs: str, context: Iterable[ContextDef], parent: _Rule = None, children: Iterable[_Rule] = []) -> None:
        super().__init__(name, symbolic, docs, context)
        self.parent = parent
        self.children = children