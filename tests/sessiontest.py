import unittest as test
from importlib import import_module
import os
import sys
import anytree
sys.path.append('../app')
from UserInterface import CLI as c

with open('tautologies_20_5-1.txt') as t:
    TAUTOLOGIES = [f"~({i})".removesuffix('\n') for i in t.readlines()]

runner = c.Runner()
rules = runner.session.getrules()
# for key in runner.session.getrules().keys(): print(rules[key])

def collect_branch(runner, name):
    runner(f'jump {name}')
    a = runner.session._get_node().getbranch_sentences()[0]
    return runner.session._get_node().getbranch_sentences()[0]

for formula in TAUTOLOGIES[:1]:
    runner(f'prove {formula}')
    last_branches = None
    branches = {tuple(collect_branch(runner, name)) for name in runner.session.getbranches()}
    turn = 0
    print(f'{formula=}')
    while branches != last_branches and not runner.session.proof_finished()[0]:
        turn += 1
        print(f'\t{turn=}')
        for branch_name in runner.session.getbranches():
            print(f'\t\t{branch_name=}')
            for i, f in enumerate(collect_branch(runner, branch_name)):
                print(f'\t\t\t{i+1=}')
                jumpout = False
                if f in runner.session._get_node().history:
                    continue
                for rule in rules:
                    out = runner(f'use {rule} {i+1}')
                    # print(out)
                    if out != "Rule couldn't be used":
                        oneline = "/".join(out.split('\n'))
                        print(f'\t\t\t\t{rule=} {oneline}')
                        jumpout = True
                        break
                if jumpout:
                    break
        last_branches = branches.copy()
        branches = {tuple(collect_branch(runner, name)) for name in runner.session.getbranches()}
    if runner.session.proof_finished()[0]:
        print('proof ended')
    else:
        print('iterating ended')
    runner(f'leave')