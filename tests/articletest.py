import unittest
import sys

sys.path.append('../app')
from article import Article

class ArticleTest(unittest.TestCase):

    def setUp(self):
        self.article = Article('article.html')

    def test_oneline(self):
        t = '<h1 id="oneline">Oneline</h1>'
        self.assertEqual(self.article['oneline'], t)
        
    def test_manyline(self):
        t = '<p id="manyline">\n        Manyline\n    </p>'
        self.assertEqual(self.article['manyline'], t)
    
    def test_startend(self):
        t = '<a href="" id="startend" />'
        self.assertEqual(self.article['startend'], t)
        
    def test_wrapped(self):
        t = '<h1 id="wrapped">Wrapped</h1>'
        self.assertEqual(self.article['wrapped'], t)
        
    def test_wrapper(self):
        t = '<div id="wrapper">\n        <h1 id="wrapped">Wrapped</h1>\n    </div>'
        self.assertEqual(self.article['wrapper'], t)


if __name__ == "__main__":
    unittest.main()