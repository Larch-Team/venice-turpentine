from math import inf
import random
from typing import Any, Callable, Iterable, NewType, Union

from anytree.iterators.preorderiter import PreOrderIter

from close import Close
from exceptions import EngineError, FormalError, UserMistake
from history import History
from pop_engine import Module
from sentence import Sentence
from tree import ProofNode, SentenceTupleStructure
from usedrule import UsedRule
from colors import get_branch_name

_Proof = NewType('_Proof', object)

class Proof(object):

    def __init__(self, sentence: Sentence, config: dict = None) -> None:
        super().__init__()
        self.S = sentence.S # Session
        self.config = config or self.S.get_config()
        self.sentence = sentence
        self.nodes = ProofNode(sentence, next(get_branch_name(self.config['accessibility'], [])))
        self.metadata = dict(
            usedrules = [],
            decision_points = [],
            used_solver = False
        )

    # Tree methods

    def append(self, sentences: Iterable[tuple[Sentence]], branch: str) -> int:
        leaf = self.nodes.getleaf(branch)
        return leaf.append(sentences, self.config['accessibility'])


    # Proof manipulation

    def deal_closure(self, branch_name: str, FormalSystem: Module = None) -> tuple[Close, str]:
        """Wywołuje proces sprawdzenia zamykalności gałęzi oraz (jeśli można) zamyka ją; Zwraca informacje o zamknięciu"""
        FormalSystem = FormalSystem or self.S.acc('Formal')
        return self.deal_closure_func(FormalSystem.check_closure, branch_name)

    def deal_closure_func(self, func: Callable[[list[Sentence], History], Union[None, tuple[Close, str]]], branch_name: str) -> tuple[Close, str]:
        """Wywołuje proces sprawdzenia zamykalności gałęzi oraz (jeśli można) zamyka ją; Zwraca informacje o zamknięciu"""
        try:
            branch, _ = self.nodes.getleaf(branch_name).getbranch_sentences()
        except ValueError as e:
            if e.message == 'not enough values to unpack (expected 2, got 1)':
                raise EngineError(
                    "Proof too short to check for contradictions")
            else:
                raise e
        used = self.nodes.getleaf(branch_name).gethistory()
        
        # Branch checking
        out = func(branch, used)

        if out:
            closure, info = out
            self.nodes.getleaf(branch_name).close(closure)
            return closure, f"{branch_name}: {info}"
        else:
            return None, None

    def use_rule(self, branch_name: str, rule: str, context: dict[str, Any], decisions: dict = None) -> None:
        """
        Wykorzystuje regułę dowodzenia systemu FormalSystem na określonej gałęzi z określonym kontekstem.

        :param FormalSystem: Socket FormalSystem, używany do przywołania use_rule
        :type FormalSystem: Socket
        :param branch: nazwa gałęzi do zastosowania reguły
        :type branch: str
        :param rule: Nazwa reguły
        :type rule: str
        :param context: Kontekst zastosowania reguły
        :type context: dict[str, Any]
        :param decisions: Zbiór podjętych decyzji, defaults to None
        :type decisions: dict, optional
        :raises EngineError: [description]
        :return: Lista nowych gałęzi
        :rtype: tuple[str]
        """
        FormalSystem = self.S.acc('Formal')

        # Statement and used retrieving
        old = self.nodes.getleaf(branch_name)
        branch = old.getbranch_sentences()[0][:]
        used = old.gethistory()

        # Rule execution
        try:
            out, used_extention, decisions = FormalSystem.use_rule(rule, branch, used, context, decisions)
        except FormalError as e:
            raise EngineError(str(e))

        # Adding to used rules and returning
        if out is None:
            return

        layer = old.append(out, self.config['accessibility'])
        children = old.children
        self.nodes.insert_history(used_extention, children)

        self.metadata['usedrules'].append(UsedRule(layer, branch_name, rule, self, context, decisions))
        
        
    def preview(self, branch_name: str, rule: str, context: dict[str, Any], decisions: dict = None) -> SentenceTupleStructure:
        FormalSystem = self.S.acc('Formal')

        # Statement and used retrieving
        old = self.nodes.getleaf(branch_name)
        branch = old.getbranch_sentences()[0][:]
        used = old.gethistory()

        # Rule execution
        try:
            out, _ = FormalSystem.use_rule(rule, branch, used, context, decisions)
        except FormalError as e:
            return ()
        return out


    def perform_usedrule(self, usedrule: UsedRule):
        """Wykonuje na dowodzie regułę na podstawie obiektu UsedRules"""
        self.use_rule(
            branch_name=usedrule.branch,
            rule=usedrule.rule,
            context=usedrule.context,
            decisions=usedrule.decisions
        )
        
    
    def get_histories(self) -> dict[str, History]:
        """Zwraca historie wszystkich gałęzi"""
        leaves = self.nodes.leaves
        return {leaf.branch:leaf.gethistory() for leaf in leaves}       
    
    
    def get_last_modified_branches(self) -> list[str]:
        """Zwraca gałęzie zmodyfikowane w ostatnim ruchu"""
        if not self.metadata['usedrules']:
            assert len(self.nodes.getbranchnames()) == 1
            return self.nodes.getbranchnames()
        max_layer = self.metadata['usedrules'][-1].layer
        return [i.branch for i in self.nodes.leaves if i.layer==max_layer]
    
    
    def copy(self) -> _Proof:
        """Kopiuje dowód"""
        p = Proof(self.sentence.copy(), self.config.copy())
        for used in self.metadata['usedrules']:
            p.perform_usedrule(used)
        for i in self.nodes.getleaves():
            if i.closed:
                p.nodes.getleaf(i.branch).close(i.closed)
        return p
    
    
    def _group_by_layers(self) -> list[tuple[UsedRule, list[Sentence]]]:
        """Grupuje zdania na podstawie reguł użytych do ich utworzenia"""
        d = {i.layer:[] for i in self.metadata['usedrules']}
        for node in PreOrderIter(self.nodes):
            if node.layer == 0:
                continue
            d[node.layer].append(node.sentence)
        return [(i,d[i.layer]) for i in self.metadata['usedrules']]
    
    def check(self) -> list[UserMistake]:
        """Sprawdza poprawność dowodu"""
        # if not self.metadata['usedrules']:
        #     raise EngineError("Nie wykonano żadnej operacji")
        
        checker = self.S.acc('Formal').checker
        
        problems = []
        for used, sentences in self._group_by_layers():
            for i in sentences:
                if (info := checker(used, i)) and info not in problems:
                    problems.append(info)
        return problems
    
    def solve(self) -> tuple[UsedRule]:
        """Dokańcza dowód, jest to wrapper przywołujący `Session.solve`"""
        self.S.solve(proof=self)
        return self.metadata['usedrules']


class BranchCentric(Proof):

    def __init__(self, sentence: Sentence, config: dict) -> None:
        super().__init__(sentence, config)
        self.branch = self.nodes.branch

    def append(self, sentences: Iterable[tuple[Sentence]], branch: str = None) -> int:
        branch = branch or self.branch
        return super().append(sentences, branch)

    def get_node(self):
        return self.nodes.getleaf(self.branch)

    def jump(self, new: str) -> None:
        """Skacze do gałęzi o nazwie new, albo na prawego/lewego sąsiadu, jeżeli podamy "left/right"

        :param new: Target branch
        :type new: str
        """
        if new.capitalize()==self.branch:
            return

        if (new_up := new.upper()) in ('LEFT', 'RIGHT'):
            changed = self.get_node().getneighbour(new_up)
            if changed is None:
                raise EngineError(f"There is no branch on the {new.lower()}")
            else:
                self.branch = changed.branch
        else:
            changed = self.nodes.getleaf(new)
            if not changed:
                raise EngineError(
                    f"Branch '{new}' doesn't exist in this proof")
            else:
                self.branch = changed.branch
    
    def next(self):
        """Przeskakuje do następnej otwartej gałęzi"""
        nodes = self.nodes.getopen()
        if nodes:
            self.branch = nodes[0].branch
            return f"Branch changed to {nodes[0].branch}"
        else:
            raise EngineError("All branches are closed")

    def use_rule(self, rule: str, context: dict[str, Any], decisions: dict):
        return super().use_rule(self.branch, rule, context, decisions=decisions)
