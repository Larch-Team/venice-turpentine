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
        self.assertEqual(basic.tokenize("p and q", ['and']), ["and_and"])
        self.assertEqual(basic.tokenize("p imp q", ['imp']), ["imp_imp"])
        self.assertEqual(basic.tokenize('not p',['not']),['not_not'])

    def test_symbol(self):
        self.assertEqual(basic.tokenize("p v q", ['or']), ["or_v"])
        self.assertEqual(basic.tokenize("p | q", ['or']), ["or_|"])
        self.assertEqual(basic.tokenize("p ^ q", ['and']), ["and_^"])
        self.assertEqual(basic.tokenize("p & q", ['and']), ["and_&"])
        self.assertEqual(basic.tokenize("p -> q", ['imp']), ["imp_->"])
        self.assertEqual(basic.tokenize('~ p',['not']),['not_~'])

    def test_full_word(self):
        self.assertEqual(basic.tokenize("p or q", ['or', 'sentvar']), ["sentvar_p", "or_or", "sentvar_q"])
        self.assertEqual(basic.tokenize("p and q", ['and', 'sentvar']), ["sentvar_p", "and_and", "sentvar_q"])
        self.assertEqual(basic.tokenize("p imp q", ['imp', 'sentvar']), ["sentvar_p", "imp_imp", "sentvar_q"])
        self.assertEqual(basic.tokenize('not p',['not','sentvar']),['not_not','sentvar_p'])

    def test_full_symbol(self):
        self.assertEqual(basic.tokenize("p v q", ['or', 'sentvar']), ["sentvar_p", "or_v", "sentvar_q"])
        self.assertEqual(basic.tokenize("p | q", ['or', 'sentvar']), ["sentvar_p", "or_|", "sentvar_q"])
        self.assertEqual(basic.tokenize("p ^ q", ['and', 'sentvar']), ["sentvar_p", "and_^", "sentvar_q"])
        self.assertEqual(basic.tokenize("p & q", ['and', 'sentvar']), ["sentvar_p", "and_&", "sentvar_q"])
        self.assertEqual(basic.tokenize("p -> q", ['imp', 'sentvar']), ["sentvar_p", "imp_->", "sentvar_q"])
        self.assertEqual(basic.tokenize('~ p',['not','sentvar']),['not_~','sentvar_p'])

    def test_bracket(self):
        self.assertEqual(basic.tokenize("(p v q)", ['or', 'sentvar']), ["(", "sentvar_p", "or_v", "sentvar_q", ")"])
        self.assertEqual(basic.tokenize("(p | q)", ['or', 'sentvar']), ['(',"sentvar_p", "or_|", "sentvar_q",')'])
        self.assertEqual(basic.tokenize("(p ^ q)", ['and', 'sentvar']), ['(',"sentvar_p", "and_^", "sentvar_q",')'])
        self.assertEqual(basic.tokenize("(p & q)", ['and', 'sentvar']), ['(',"sentvar_p", "and_&", "sentvar_q",')'])
        self.assertEqual(basic.tokenize("(p -> q)", ['imp', 'sentvar']), ['(',"sentvar_p", "imp_->", "sentvar_q",')'])
        self.assertEqual(basic.tokenize('(~ p)',['not','sentvar']),['(','not_~','sentvar_p',')'])

if __name__ == "__main__":
    test.main()
