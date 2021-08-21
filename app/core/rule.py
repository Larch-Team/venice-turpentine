from collections import namedtuple
from inspect import signature
from typing import Callable, Iterable, NewType, Type

from anytree.node.nodemixin import NodeMixin

from sentence import Sentence

SentenceTupleStructure = NewType('SentenceTupleStructure', tuple[tuple[Sentence]])
_Rule = NewType('_Rule', NodeMixin)
ContextDef = namedtuple(
    'ContextDef', ('variable', 'official', 'docs', 'type_'))

def ParameterContext(parent: Type, type_: str, variable: str = '', official: str = '', docs: str = ''):
    """
    Używane do definiowania elementów kontekstu reguł - dodatkowych przesłanek pochodzących od użytkownika

    :param parent: Typ, z którego przesłanka będzie dziedziczyć type hinting
    :type type_: Type
    :param type_: Nazwa typu
    :type type_: str
    :param variable: Nazwa klucza, pod jakim element będzie przechowywany, nie może być powtarzalny
    :type variable: str
    :param name_official: Nazwa wyświetlalna dla użytkownika, defaults to ''
    :type name_official: str, optional
    :param docs: Dokumentacja, defaults to ''
    :type docs: str, optional
    """
    context_type = NewType(type_, parent)

    if variable == '':
        variable = type_
    if official == '':
        official = variable
        
    context_type.variable = variable
    context_type.official = official
    context_type.__doc__ = docs
    return context_type


SentenceID = ParameterContext(int, 'sentenceID', official='Sentence Number', docs='The number of the sentence in this branch')
TokenID = ParameterContext(int, 'tokenID', official='Token Number', docs='The number of the symbol in the sentence')

class RuleBase(object):
    def __init__(self, name: str, symbolic: str, docs: str, reusable: bool, context: Iterable[ContextDef] = None) -> None:
        super().__init__()
        self.name = name
        self.symbolic = symbolic
        self.__doc__ = docs
        self.context = context
        self.reusable = reusable
        self.naive = None
        self.strict = None
        
    def setNaive(self, func: Callable[..., SentenceTupleStructure]):
        self.naive = func
        
        if not self.context:
            self.context = []
            params = signature(func).parameters
            for i in params.values():
                if hasattr(i.annotation, 'official'):
                    self.context.append(ContextDef(
                        variable = i.annotation.variable,
                        official = i.annotation.official,
                        docs = i.annotation.__doc__,
                        type_ = i.annotation.__name__
                    ))
                elif i.annotation == list[Sentence]:
                    continue                
                else:
                    self.context = None
                    break
                
        return func
    
    def setStrict(self, func: Callable[[Sentence], SentenceTupleStructure]):
        self.strict = func
        return func
        
class Rule(RuleBase, NodeMixin):

    def __init__(self, name: str, symbolic: str, docs: str, reusable: bool, context: Iterable[ContextDef] = None, parent: _Rule = None, children: Iterable[_Rule] = []) -> None:
        super().__init__(name, symbolic, docs, reusable, context)
        self.parent = parent
        self.children = children or []
