import example1
import unittest as test
from importlib import import_module
import os
import sys

sys.path.append('../app/')
from UserInterface import cmd

class TestParser(test.TestCase):

    def setUp(self):
        self.dict = {
            'addition negative': {'comm': example1.sub, 'args': [int, int], 'add_docs': ''},
            'addition': {'comm': example1.add, 'args': [int, int], 'add_docs': ''},
            'str_int': {'comm': example1.str_int_none, 'args': [str, int], 'add_docs': ''},
            'random': {'comm': example1.random, 'args': [], 'add_docs': ''}
        }

    def test_proper(self):
        parsed = cmd.parser('addition 1 2', _dict=self.dict)
        self.assertEqual(tuple(parsed[0].values()), (example1.add, [1, 2]))

    def test_no_args(self):
        parsed = cmd.parser('random', _dict=self.dict)
        self.assertEqual(tuple(parsed[0].values()), (example1.random, []))

    def test_long(self):
        parsed = cmd.parser('addition negative 1 2', _dict=self.dict)
        self.assertEqual(tuple(parsed[0].values()), (example1.sub, [1, 2]))

    def test_wrong_args(self):
        with self.assertRaises(TypeError):
            cmd.parser('addition 1 test', _dict=self.dict)

    def test_too_many_args(self):
        with self.assertRaises(cmd.ParsingError):
            cmd.parser('random 1', _dict=self.dict)

    def test_more_args_needed(self):
        with self.assertRaises(cmd.ParsingError):
            cmd.parser('addition 1', _dict=self.dict)

    def test_func_notfound(self):
        with self.assertRaises(cmd.ParsingError):
            cmd.parser('doesntexist 1', _dict=self.dict)


if __name__ == "__main__":
    test.main()
