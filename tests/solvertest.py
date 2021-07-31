import sys
import time

sys.path.append('../app')
from plugins.UserInterface import CLI as c

with open('tautologies_20_5-1.txt') as t:
    TAUTOLOGIES = t.readlines()

runner = c.Runner()

start = time.time()
for num, formula in enumerate(TAUTOLOGIES):
    if num % 50 == 0:
        print(f'Postęp: {num}/{len(TAUTOLOGIES)}')
    runner(f'prove {formula}')
    wynik = runner('solve')
    if wynik == 'Nie udało się zakończyć dowodu':
        print(num, "- brak rozwiązania -" , formula)
    elif 'Formuła jest tautologią' not in wynik:
        print(num, "- błędne rozwiązanie -" , formula)
    runner(f'leave')
print(round((time.time()-start)/len(TAUTOLOGIES), 4), 'sekund na dowód')