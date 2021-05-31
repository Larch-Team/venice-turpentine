import typing as tp
import Auto as utils
from collections import namedtuple
from math import inf

SOCKET = 'Auto'
VERSION = '0.0.1'


RULES = ['left and', 'right imp', 'right and', 'left or', 'left imp', 'right or', " "]
RULES_types = {i.split()[1] for i in RULES[:-1]}

PRECEDENCE = {
    'and': 2,
    'or': 2,
    'imp': 1
}

def find_rule(sen: utils.Sentence) -> tp.Union[list[str], None]:
    sen = [i for i in sen if i != "^"]
    side = 'left'
    usable = []
    bracket_lvl = 0
    lowest_precedence = inf
    sep_count = 0
    for i in sen:
        if i.startswith('sep_'):
            lowest_precedence = inf
            sep_count += 1
            assert bracket_lvl == 0, "Wrong brackets"
        elif i.startswith('turnstile_'):
            lowest_precedence = inf
            side = 'right'
            assert bracket_lvl == 0, "Wrong brackets"
        elif i == '(':
            bracket_lvl += 1
        elif i == ')':
            bracket_lvl -= 1
        elif bracket_lvl == 0:
            for j in RULES_types:
                if i.startswith(j+"_") and PRECEDENCE[j]<=lowest_precedence:
                    lowest_precedence = PRECEDENCE[j]
                    if side=='left':
                        usable.append((side, j, sep_count+1))
                    else:
                        usable.append((side, j))
    
    if usable == []:
        return None
    else:
        return usable



# __template__.py

def solve(delegate: callable, branch: list[utils.Sentence]) -> tuple[tp.Union[str, None], tp.Union[tuple[str], None]]:
    found_rules = find_rule(branch[-1])
    
    if found_rules is None:
        return None, None

    found_rules.sort(key=lambda x: RULES.index(" ".join(x[:2])))
    
    out = None
    i = 0
    loops = 0
    while not out and len(found_rules)>i:
        rule = found_rules[i]
        i+=1

        # Context compilation
        context = dict()
        if rule[0]=='left':
            context['partID'] = rule[2]
        elif rule[1]=='or':
            context['conn_side'] = 'find'

        # Execution
        try:
            out = delegate(" ".join(rule[:2]), context, True)
        except Exception as e:
            if str(e) in ("Operation prohibited by loop detection algorithm", "There is a sequent that is prioritized", "Rule can't be performed on prioritized sequents"):
                loops += 1
                out = None
            else:
                raise e

    if out:
        return f"Performed {' '.join((str(i) for i in rule))}", out
    else:
        if loops==len(found_rules):
            return "Branch always loops", None
        return None, None


def compatible() -> tuple[str]:
    return ('int_seqcal_scottish', 'int_seqcal_swiss')