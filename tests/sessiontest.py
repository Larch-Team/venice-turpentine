import unittest as test
from importlib import import_module
import os
import sys
import anytree
from pprint import pprint
sys.path.append('../app')
from UserInterface import CLI as c

with open('tautologies_20_5-1.txt') as t:
    TAUTOLOGIES = [f"~({i[:-1]})" for i in t.readlines()]

runner = c.Runner()
rules = runner.session.getrules()
# for key in runner.session.getrules().keys(): print(rules[key])

def collect_branch(runner, name):
    runner(f'jump {name}')
    a = runner.session._get_node().getbranch_sentences()[0]
    return runner.session._get_node().getbranch_sentences()[0]

for num, formula in enumerate(TAUTOLOGIES):
    runner(f'prove {formula}')
    last_branches = None
    branches = {tuple(collect_branch(runner, name)) for name in runner.session.getbranches()}
    turn = 0
    print(f'{num=}, {formula=}')
    while branches != last_branches and not runner.session.proof_finished()[0]:
        turn += 1
        print(f'\t{turn=}')
        for branch_name in runner.session.getbranches():
            print(f'\t\t{branch_name=}')
            for i, f in enumerate(collect_branch(runner, branch_name)):
                jumpout = False
                print(f'\t\t\t{i+1=}')
                for rule in rules:
                    out = runner(f'use {rule} {i+1}')
                    # print(out)
                    if out not in ("Rule couldn't be used", 'This sentence was already used in a non-reusable rule'):
                        oneline = "/".join(out.split('\n'))
                        print(f'\t\t\t\t{rule=} {oneline}')
                        jumpout = True
                        break
                if jumpout:
                    break
        last_branches = branches.copy()
        branches = {tuple(collect_branch(runner, name)) for name in runner.session.getbranches()}
    print(runner.session.proof_finished())
    if not sum(runner.session.proof_finished())==2:
        for i in branches:
            print()
            for j in i:
                print(str(j))
        break

    runner(f'leave')