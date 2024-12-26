import os
import unittest
import sys

sys.path.extend([os.path.abspath(i) for i in ['../app/appdata', '../app/core']])
from sentence import Sentence

class TestgetComponents(unittest.TestCase):

    def setUp(self):
        self.precedence = {
            'and':3,
            'or':3,
            'imp':2,
            'not':4
        }

    def test_simple(self):
        sentence = Sentence(['sentvar_p', 'or_or', 'sentvar_q'], None)
        result = (
            'or_or',
            (
                ['sentvar_p'],
                ['sentvar_q']
            )
        )
        self.assertEqual(sentence.getComponents(self.precedence), result)

if __name__ == "__main__":
    unittest.main()