import unittest as test
from importlib import import_module
import os
import sys
import anytree
sys.path.append('../app')
from UserInterface import CLI as c

runner = c.Runner()
rules = runner.session.getrules()
for key in runner.session.getrules().keys(): print(rules[key])