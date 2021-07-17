import sys
import random

sys.path.append('../app')
from UserInterface import CLI as c

#jeszcze tu wroce
runner = c.Runner()
rules = runner.session.getrules()
commands = list(c.command_dict.keys())
for x in ['prove','plugin gen','write','exit']:
        commands.remove(x)
args = {'jump': [' left',' right',' <',' >'],
        'use': ['true and', 'false and', 'false or', 'true or', 'false imp', 'true imp', 'double not'],
        'plugin switch': ['UserInterface','Lexicon','Auto','FormalSystem','Output'],
        'plugin list': ['UserInterface','Lexicon','Auto','FormalSystem','Output']}

lists_acc = []
lists_wrong = []
for _ in range(50):
        com_list_a = ['prove (p -> q) ^ p -> q']
        com_list_w = ['prove (p -> q) ^ p -> q']
        for _ in range(18):
                com_a = random.choice(commands)
                com_w = random.choice(commands)
                add_arg = random.randint(0,9)
                if add_arg%2:
                        com_list_w.append(' '.join([com_w,random.choice(list(args.values())[random.randint(0,len(args.values())-1)])]))
                else:
                        com_list_w.append(com_w)
                if com_a in args.keys():
                        com_conf = [com_a,random.choice(args[com_a])]
                        if com_a == 'plugin switch':
                                com_conf = ' '.join([*com_conf,random.choice(runner('plugin list '+com_conf[-1]).split(sep='\n')[1].split(sep='; '))])
                        else:
                                com_conf = ' '.join(com_conf)
                        com_list_a.append(com_conf)
                else:
                        com_list_a.append(com_a)
        com_list_a.append('exit')
        com_list_w.append('exit')
        lists_acc.append(com_list_a)
        lists_wrong.append(com_list_w)
 
print('POPRAWNE ARGUMENTY\n\n')
for i,list in enumerate(lists_acc):
        print(f'LISTA {i}\n')
        for com in list:
                print(f'{com}:',end=' ')
                print(f'--[{runner(com)}]--')
print('\n\n ZLE ARGUMENTY\n\n')
for i,list in enumerate(lists_wrong):
        print(f'LISTA {i}\n')
        for com in list:
                print(f'{com}:',end=' ')
                print(f'--[{runner(com)}]--')

# print(random.choice(list(args.values())[random.randint(0,len(args.values())-1)]))
# p = runner('plugin list FormalSystem')
# p = p.split(sep='\n')[1].split(sep = '; ')
# print(p)