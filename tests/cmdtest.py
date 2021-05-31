import example1
import unittest as test
from importlib import import_module
import os
import sys

sys.path.append('../app')
from UserInterface import CLI as cmd

class TestParser(test.TestCase):

    def setUp(self):
        self.comms = {
            'addition negative': {'comm': example1.sub, 'args': [int, int]},
            'addition': {'comm': example1.add, 'args': [int, int]},
            'str_int': {'comm': example1.str_int_none, 'args': [str, int]},
            'random': {'comm': example1.random, 'args': []}
        }

    def test_proper(self):
        parsed = cmd.parser('addition 1 2', self.comms)
        self.assertEqual(tuple(parsed[0]._asdict().values()), (example1.add, [1, 2], None))

    def test_no_args(self):
        parsed = cmd.parser('random', self.comms) 
        self.assertEqual(tuple(parsed[0]._asdict().values()), (example1.random, [], None))

    def test_long(self):
        parsed = cmd.parser('addition negative 1 2', self.comms)
        self.assertEqual(tuple(parsed[0]._asdict().values()), (example1.sub, [1, 2], None))

    def test_wrong_args(self):
        with self.assertRaises(TypeError):
            cmd.parser('addition 1 test', self.comms)

    def test_too_many_args(self):
        with self.assertRaises(cmd.ParsingError):
            cmd.parser('random 1', self.comms)

    def test_more_args_needed(self):
        with self.assertRaises(cmd.ParsingError):
            cmd.parser('addition 1', self.comms)

    def test_func_notfound(self):
        with self.assertRaises(cmd.ParsingError):
            cmd.parser('doesntexist 1', self.comms)


if __name__ == "__main__":
    test.main()
