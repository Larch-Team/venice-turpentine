import os
import sys
import random
from termcolor import colored
sys.path.extend([os.path.abspath(i) for i in ['../app/appdata', '../app/core']])
from plugins.UserInterface import CLI as c


runner = c.Runner()
rules = runner.session.getrules()
commands = list(c.command_dict.keys())
for x in ['plugin gen','write','exit']:
        commands.remove(x)
args = {'prove' : ['(p -> q) ^ p -> q'],
        'jump': [' left',' right',' <',' >'],
        'use': ['true and', 'false and', 'false or', 'true or', 'false imp', 'true imp', 'double not'],
        'plugin switch': ['UserInterface','Lexicon','Auto','Formal','Output'],
        'plugin list': ['UserInterface','Lexicon','Auto','Formal','Output']}


list_acc = []
list_wrong = []
for com in commands:
        if com in args.keys():
                com_conf = [com,random.choice(args[com])]
                if com == 'plugin switch':
                        com_conf = ' '.join([*com_conf,random.choice(runner('plugin list '+com_conf[-1]).split(sep='\n')[1].split(sep='; '))])
                else:
                        com_conf = ' '.join(com_conf)
                list_acc.append(com_conf)
        else:
                list_acc.append(com)

for com in commands:
        add_arg = random.randint(0,9)
        if add_arg%2:
                list_wrong.append(' '.join([com,random.choice(list(args.values())[random.randint(0,len(args.values())-1)])]))
        else:
                list_wrong.append(com)

acc_permutations = [random.choices(list_acc, k = 20) for _ in range(1000)]
wrong_permutations = [random.choices(list_wrong, k = 20) for _ in range(1000)]

print(colored('POPRAWNE ARGUMENTY\n\n','green'))
for i,list in enumerate(acc_permutations):
        print(colored(f'\tLISTA {i}\n','blue'))
        for com in list:
                print(f'{com}:',end=' ')
                print(f'--[{runner(com)}]--')
print(colored('\n\n ZLE ARGUMENTY\n\n','red'))
for i,list in enumerate(wrong_permutations):
        print(colored(f'\tLISTA {i}\n','blue'))
        for com in list:
                print(f'{com}:',end=' ')
                print(f'--[{runner(com)}]--')
