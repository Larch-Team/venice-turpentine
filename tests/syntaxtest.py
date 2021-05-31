import unittest as test
from importlib import import_module
import os
import sys

sys.path.append('../app/Lexicon')
import basic

basic.TESTING = True

class TestTokenize(test.TestCase):
    # TODO: Rozbudować

    def test_word(self):
        self.assertEqual(basic.tokenize("p or q", ['or']), ["or_or"])

    def test_symbol(self):
        self.assertEqual(basic.tokenize("p v q", ['or']), ["or_v"])

    def test_full(self):
        self.assertEqual(basic.tokenize("p v q", ['or', 'sentvar']), ["sentvar_p", "or_v", "sentvar_q"])

    def test_bracket(self):
        self.assertEqual(basic.tokenize("(p v q)", ['or', 'sentvar']), ["(", "sentvar_p", "or_v", "sentvar_q", ")"])


if __name__ == "__main__":
    test.main()
