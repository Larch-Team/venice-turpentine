from typing import Any, Callable, Iterable
from rule import Rule, SentenceTupleStructure
from sentence import Sentence
from proof import Proof
import plugins.Formal.__utils__ as utils
from analytic_signed.signed import *
from tree import ProofNode
from usedrule import UsedRule

def find_rule(sentence: Sentence) -> str:
    """
    Rozpoznaje jaka reguła powinna zostać użyta na formule
    """
    sentence = convert_from_signed(sentence)
    main, other = sentence.getComponents()
    if main is None:
        return None
    elif main.startswith('not_'):
        negated = 'false'
        second, _ = other[1].getComponents()
    else:
        negated = 'true'
        second = main

    if second is None:
        return None
    elif second.startswith('not_'):
        return 'double not'
    else:
        return f"{negated} {second.split('_')[0]}"


def append_by_rules(containers: dict[str, list[utils.SignedSentence]], nodes: Iterable[ProofNode]) -> dict[str, list[utils.SignedSentence]]:
    """
    Uzupełnia kontenery wygenerowane przez group_by_rules o dodatkowe elementy

    :param containers: kontenery wygenerowane przez group_by_rules
    :type containers: dict[str, list[utils.SignedSentence]]
    :param nodes: Węzły, o które mają zostać uzupełnione kontenery
    :type nodes: tp.Iterable[ProofNode]
    :return: Uzupełnione kontenery
    :rtype: dict[str, list[utils.SignedSentence]]
    """
    for node in nodes:
        num = node.depth

        if not node.closed and (rule := find_rule(node.sentence)) is not None:
            containers[rule].append(
                utils.SignedSentence(convert_from_signed(node.sentence), node.branch, num))
    return containers


def multiply_for_branches(containers: dict[str, list[utils.SignedSentence]], target: str, branches: Iterable[str]) -> dict[str, list[utils.SignedSentence]]:
    """
    Generuje dodatkowe reprezentacje zdań w innych gałęziach

    :param containers: kontenery wygenerowane przez group_by_rules
    :type containers: dict[str, list[utils.SignedSentence]]
    :param target: Gałąź, która ma być używana jako wzorzec
    :type target: str
    :param branches: Gałęzie, dla których należy wygenerować zdania
    :type branches: tp.Iterable[str]
    :return: Uzupełnione kontenery
    :rtype: dict[str, list[utils.SignedSentence]]
    """
    to_copy = {key: [i for i in val if i.branch == target]
               for key, val in containers.items()}

    for key, value in containers.items():
        value.extend(
            change_branch_container(
                to_copy[key], [i for i in branches if i != target]
            )
        )

    return containers


def change_branch_container(container: list[utils.SignedSentence], branches: Iterable[str]) -> list[utils.SignedSentence]:
    return [utils.SignedSentence(i.sentence, j, i.id) for i in container for j in branches]

def strict_filler(func: Callable[..., SentenceTupleStructure]) -> Callable[..., tuple[ProofNode]]:
    """
    Dekorator uzupełniający funkcję wykonującą regułę dowodzenia strict o otoczkę techniczną

    :param func: Funkcja wykonująca operacje, pierwszym argumentem powinno być Rule, a drugim Sentence
    :type func: tp.Callable[..., SentenceTupleStructure]
    :return: Nowa funkcja z dodatkowym argumentem Proof na początku
    :rtype: tp.Callable[..., tuple[ProofNode]]
    """
    def wrapper(proof: Proof, rule: Rule, sentence: utils.SignedSentence, *args, **kwargs):
        old = proof.nodes.getleaf(sentence.branch)

        # Rule usage
        fin = func(rule, sentence, *args, **kwargs)
        assert fin is not None, "Reguła nie zwróciła nic"

        layer = proof.append(fin, sentence.branch)
        ProofNode.insert_history(
            len(fin)*([[0]] if rule.reusable else [[convert_to_signed(sentence.sentence)]]), old.children)

        if rule.name.startswith('false'):
            _, (_, a) = sentence.sentence.getComponents()
            tid = a.getMainConnective() +2
        else:
            tid = sentence.sentence.getMainConnective()
        context = {
            'sentenceID': sentence.id,
            'tokenID': tid
        }

        proof.metadata['usedrules'].append(
            UsedRule(layer, sentence.branch, rule.name, proof, context=context, auto=True))
        return old.descendants
    return wrapper

@strict_filler
def use_strict(rule: Rule, sentence: utils.SignedSentence) -> SentenceTupleStructure:
    """Funkcja ma de facto inne parametry ze względu na działanie dekoratora - pierwszym jest Proof. Funkcja wykonuje regułę dowodzenia w formie strict na zdaniu"""
    return rule.strict(sentence.sentence)


def _pop_default(l: list, index: int = -1, default: Any = None) -> Any:
    try:
        return l.pop(index)
    except IndexError:
        return default


def propagate_rule(proof: Proof, rule: Rule, containers: dict[str, list[utils.SignedSentence]], check_closure: Callable) -> dict[str, list[utils.SignedSentence]]:
    """
    Przypominająca operację konsekwencji funkcja, która stosuje daną regułę, dopóki da się ją zastosować na formułach w dowodzie.
    Zwraca kontenery z nierozwiązanymi zdaniami
    """
    if not containers[rule.name]:
        return containers
    closed = []
    while (sentence := _pop_default(containers[rule.name])):
        if sentence.branch in closed:
            continue
        new = use_strict(proof, rule, sentence)
        for node in new:
            if proof.deal_closure_func(check_closure, node.branch)[0]:
                closed.append(node.branch)

        modified_branches = {i.branch for i in new}
        if len(modified_branches) > 1:
            containers = multiply_for_branches(
                containers, node.parent.branch, modified_branches)
        containers = append_by_rules(containers, new)
    return {i: [k for k in j if k.branch not in closed] for i, j in containers.items()}


def _solver(proof: Proof, rule: Rule, containers: dict[str, list[utils.SignedSentence]], check_closure: Callable) -> bool:
    """ 
    Rekurencyjna funkcja solvera, zwraca informację, czy dowód udało się ukończyć (powinna być zawsze True)
    Używać solver zamiast tej.
    """
    start_used = proof.metadata['usedrules'][:]
    start_layer = start_used[-1].layer if start_used else 0

    while any(len(containers[i.name]) > 0 for i in rule.path):
        for past_rule in rule.path:
            containers = propagate_rule(proof, past_rule, containers, check_closure)
        if proof.nodes.is_closed():
            return True

    for child in rule.children:
        if _solver(proof, child, containers, check_closure):
            return True

    proof.metadata['usedrules'] = start_used
    proof.nodes.pop(start_layer+1)
    return False
