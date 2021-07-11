import sys

sys.path.append('../app')
from UserInterface import CLI as c

with open('tautologies_20_5-1.txt') as t:
    TAUTOLOGIES = t.readlines()

runner = c.Runner()

for num, formula in enumerate(TAUTOLOGIES):
    runner(f'prove {formula}')
    if runner('solve') == 'Nie udało się zakończyć dowodu':
        print(num, "-" , formula)
    runner(f'leave')