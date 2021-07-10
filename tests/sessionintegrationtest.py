import sys
import random

sys.path.append('../app')
from UserInterface import CLI as c

#jeszcze tu wroce to takie prototypowe zabawy
runner = c.Runner()
rules = runner.session.getrules()
commands = list(c.command_dict.keys())
args = {'jump': [' left',' right',' <',' >'],
        'write': ['file'],
        'use': ['true and', 'false and', 'false or', 'true or', 'false imp', 'true imp', 'double not'],
        'plugin switch': ['UserInterface','Lexicon','Auto','FormalSystem','Output'], #jeszcze name
        'plugin list': ['UserInterface','Lexicon','Auto','FormalSystem','Output']}

lists_acc = [[random.choice(commands) for _ in range(20)] for _ in range(50)]
lists_wrong = []

# for key in commands.keys(): print(key)
# print(rules.keys())
# print(lists[1])

for com_list in lists:
    for com in com_list:
        runner(com)