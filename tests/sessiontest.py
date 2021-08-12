import sys

from multiprocessing import Pool
sys.path.extend(['../app/appdata', '../app/core'])
from plugins.UserInterface import CLI as c

# TODO: dostosować do reguł naiwnych
raise NotImplementedError()

with open('tautologies_20_5-1.txt') as t:
    TAUTOLOGIES = [f"~({i[:-1]})" for i in t.readlines()]

runner = c.Runner()
rules = runner.session.getrules()
# for key in runner.session.getrules().keys(): print(rules[key])

def collect_branch(runner, name):
    runner(f'jump {name}')
    return runner.session._get_node().getbranch_sentences()[0]

def prove_formula(counter):
    num=counter[0]
    formula=counter[1]
    runner(f'prove {formula}')
    last_branches = None
    branches = {tuple(collect_branch(runner, name)) for name in runner.session.getbranches()}
    turn = 0
    while branches != last_branches and not runner.session.proof_finished()[0]:
        turn += 1
        #print(f'\t{turn=}')
        for branch_name in runner.session.getbranches():
            #print(f'\t\t{branch_name=}')
            for i, f in enumerate(collect_branch(runner, branch_name)):
                jumpout = False
                #print(f'\t\t\t{i+1=}')
                for rule in rules:
                    out = runner(f'use {rule} {i+1}')
                    # print(out)
                    if out not in ("Rule couldn't be used", 'This sentence was already used in a non-reusable rule'):
                        oneline = "/".join(out.split('\n'))
                        #print(f'\t\t\t\t{rule=} {oneline}')
                        jumpout = True
                        break
                if jumpout:
                    break
        last_branches = branches.copy()
        branches = {tuple(collect_branch(runner, name)) for name in runner.session.getbranches()}
    print(f'{num=}, {formula=}', '\n',runner.session.proof_finished())
    if not sum(runner.session.proof_finished())==2:
        for i in branches:
            print()
            for j in i:
                print(str(j))
        return

if __name__ == '__main__':
    counter_list = list(enumerate(TAUTOLOGIES))
    pool=Pool()
    pool.map(prove_formula, counter_list)
    runner(f'leave')