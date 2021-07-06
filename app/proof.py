import random
from typing import Any, Iterable, Union
from close import Close
from pop_engine import Socket
from sentence import Sentence
from tree import ProofNode
from exceptions import EngineError, FormalError
from usedrule import UsedRule

class Proof(object):

    def __init__(self, sentence: Sentence, name_seed: int = None) -> None:
        super().__init__()
        self.S = sentence.S # Session
        self.config = self.S.get_config()
        self.nodes = ProofNode(sentence, 'Green')
        self.metadata = dict(
            usedrules = [],
            decision_points = []
        )
        self.name_seed = name_seed or random.random()*10**7
        self.namegen = random.Random(self.name_seed)

    # Tree methods

    def append(self, sentences: Iterable[tuple[Sentence]], branch: str) -> int:
        leaf = self.nodes.getleaf(branch)
        leaf.append(sentences, self.namegen)


    # Proof manipulation

    def deal_closure(self, FormalSystem: Socket, branch_name: str) -> tuple[Close, str]:
        """Wywołuje proces sprawdzenia zamykalności gałęzi oraz (jeśli można) zamyka ją; Zwraca informacje o podjętych akcjach"""
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
        out = FormalSystem.check_closure(branch, used)

        if out:
            closure, info = out
            self.nodes.getleaf(branch_name).close(closure)
            return closure, f"{branch_name}: {info}"
        else:
            return None, None


    def use_rule(self, FormalSystem: Socket, branch: str, rule: str, context: dict[str, Any], decisions: dict = None) -> tuple[str]:
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

        # Statement and used retrieving
        old = self.nodes.getleaf(branch)
        branch = old.getbranch_sentences()[0][:]
        used = old.gethistory()

        # Rule execution
        try:
            out, used_extention, decisions = FormalSystem.use_rule(rule, branch, used, context, decisions)
        except FormalError as e:
            raise EngineError(str(e))

        # Adding to used rules and returning
        if out is None:
            return None

        layer = old.append(out, self.namegen)
        children = old.children
        assert len(children) == len(used_extention), "Liczba gałęzi i list komend powinna być taka sama"
        for j, s in zip(children, used_extention):
            j.History(*s)
            for k in j.descendants:
                k.History(*s)

        self.metadata['usedrules'].append(UsedRule(layer, self.branch, rule, self, context, decisions))
        return tuple(i.branch for i in children)


class BranchCentric(Proof):

    def __init__(self, sentence: Sentence, config: dict, name_seed: int = None) -> None:
        super().__init__(sentence, config, name_seed=name_seed)
        self.branch = 'Green'

    def append(self, sentences: Iterable[tuple[Sentence]]) -> int:
        return super().append(sentences, self.branch)

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
            changed = self.nodes.getleaf(new.capitalize())
            if not changed:
                raise EngineError(
                    f"Branch '{new.lower()}' doesn't exist in this proof")
            else:
                self.branch = changed.branch
    
    def next(self):
        """Przeskakuje do następnej otwartej gałęzi"""
        nodes = self.nodes.getopen()
        if nodes:
            self.branch = next(nodes).branch
            return f"Branch changed to {nodes.branch}"
        else:
            raise EngineError("All branches are closed")

    def use_rule(self, FormalSystem: Socket, rule: str, context: dict[str, Any], decisions: dict):
        return super().use_rule(FormalSystem, self.branch, rule, context, decisions=decisions)