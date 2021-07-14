import sys
import random

sys.path.append('../app')
from UserInterface import CLI as c

#jeszcze tu wroce to takie prototypowe zabawy
runner = c.Runner()
rules = runner.session.getrules()
commands = list(c.command_dict.keys())
for x in ['prove','plugin gen','write','exit']:
        commands.remove(x)
args = {'jump': [' left',' right',' <',' >'],
        'write': ['file'],
        'use': ['true and', 'false and', 'false or', 'true or', 'false imp', 'true imp', 'double not'],
        'plugin switch': ['UserInterface','Lexicon','Auto','FormalSystem','Output'], #jeszcze name
        'plugin list': ['UserInterface','Lexicon','Auto','FormalSystem','Output']}

lists_acc = []
lists_wrong = []
for _ in range(50):
        com_list = []
        for _ in range(19):
                com = random.choice(commands)
                if com in args.keys():
                        com_conf = [com,random.choice(args[com])]
                        if com == 'plugin switch':
                                com_conf = ' '.join([com_conf[0],com_conf[1],random.choice(runner('plugin list '+com_conf[-1]).split(sep='\n')[1].split(sep='; '))])
                        else:
                                com_conf = ' '.join(com_conf)
                else:
                        com_list.append(com_conf)
        com_list.append('exit')
        lists_acc.append(com_list)
 

for list in lists_acc: print(list)

# p = runner('plugin list FormalSystem')
# p = p.split(sep='\n')[1].split(sep = '; ')
# print(p)