import unittest
import sys

sys.path.append('../app')
from sentence import Sentence

class TestgetMainConnective(unittest.TestCase):

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
        self.assertEqual(sentence.getMainConnective(self.precedence), result)

if __name__ == "__main__":
    unittest.main()