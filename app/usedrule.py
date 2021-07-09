from dataclasses import asdict, dataclass, field
from typing import NewType
from sentence import Sentence

_BranchCentric = NewType('_BranchCentric', object)

@dataclass(init=True, repr=True)
class UsedRule(object):
    layer: int
    branch: str
    rule: str
    _proof: _BranchCentric
    context: dict = field(default_factory=dict)
    decisions: dict = field(default_factory=dict)

    def to_dict(self):
        return asdict(self)

    def get_premisses(self) -> dict[str, Sentence]:
        """Zwraca szystkie zdania, których sentenceID w tej gałęzi został wspomniany w dowodzie"""
        branch, _ = self._proof.nodes.getbranch_sentences()
        context_defs = self._proof.S.acc('FormalSystem').get_needed_context(self.rule)
        sentids = (i.variable for i in context_defs if i.type_ == 'sentenceID')
        return {i: branch[j] for i, j in self.context.items() if i in sentids}
