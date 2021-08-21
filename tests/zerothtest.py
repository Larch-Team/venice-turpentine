import unittest as test
from importlib import import_module
import os
import sys

sys.path.extend(['../app/appdata', '../app/core'])
from sentence import Sentence
from plugins.Formal import analytic_freedom as zol

def join_to_string(sentence) -> str:
    """Writes the sentence as a string, where tokens are written as `<[token type]_[lexem]>`"""
    new = []
    for token in sentence:
        if token in ('(', ')', '{', '}'):
            new.append(token)
        else:
            new.append(f"<{token}>")
    return "".join(new)


class _SessionDummy(object):
    config = {'chosen_plugins':{'Formal':zol}}
    
    def acc(self, arg):
        return zol


def new_notation(func):
    def wrapped(*args):
        arg_list = []
        for sent in args:
            sent_list = sent.replace(
                "(", ">(>").replace(")", ">)>").replace("<", ">").split(">")
            arg_list.append(Sentence([i for i in sent_list if i != ''], _SessionDummy()))
        ret = func(*arg_list)
        if isinstance(ret, list):
            if ret == []:
                return ()
            a = join_to_string(ret)
            return join_to_string(ret)
        elif isinstance(ret, tuple):
            if ret in [((),), None]:
                return ()
            return tuple([tuple([join_to_string(i) for i in j]) for j in ret])
        else:
            return ret
    return wrapped



class Test_true_and(test.TestCase):

    def setUp(self):
        self.rule = new_notation(zol.RULES['true and'].strict)

    def test_basic(self):
        self.assertEqual(self.rule('<sentvar_p><and_^><sentvar_q>'),
                         tuple([tuple(['<sentvar_p>', '<sentvar_q>'])]))

    def test_basicbracket(self):
        self.assertEqual(
            self.rule('(<sentvar_p>)<and_^>(<sentvar_q>)'), tuple([tuple(['<sentvar_p>', '<sentvar_q>'])]))

    def test_double(self):
        self.assertEqual(self.rule('(<sentvar_p><and_^><sentvar_q>)<and_^><sentvar_r>'),
                         tuple([tuple(['<sentvar_p><and_^><sentvar_q>', '<sentvar_r>'])]))

    def test_wrong_rule(self):
        self.assertEqual(self.rule('<sentvar_p><or_or><sentvar_q>'), None)

    def test_brackets(self):
        self.assertEqual(self.rule('(<sentvar_p><or_or><sentvar_r>)<and_^>(<sentvar_q><or_or>(<not_~><sentvar_r>))'),
                         tuple([tuple(['<sentvar_p><or_or><sentvar_r>', '<sentvar_q><or_or>(<not_~><sentvar_r>)'])]))

    def test_more_brackets(self):
        self.assertEqual(self.rule('((<not_~><sentvar_q>)<or_or><sentvar_r>)<and_^>((<sentvar_q>)<or_or>(<not_~>(<sentvar_r>)))'),
                         tuple([tuple(['(<not_~><sentvar_q>)<or_or><sentvar_r>', '(<sentvar_q>)<or_or>(<not_~>(<sentvar_r>))'])]))



class Test_true_or(test.TestCase):

    def setUp(self):
        self.rule = new_notation(zol.RULES['true or'].strict)

    def test_basic(self):
        self.assertEqual(self.rule('<sentvar_p><or_or><sentvar_q>'),
                         (('<sentvar_p>',), ('<sentvar_q>',)))

    def test_basicbracket(self):
        self.assertEqual(self.rule(
            '(<sentvar_p>)<or_or>(<sentvar_q>)'), (('<sentvar_p>',), ('<sentvar_q>',)))

    def test_double(self):
        self.assertEqual(self.rule('(<sentvar_p><or_or><sentvar_q>)<or_or>(<sentvar_r>)'), ((
            '<sentvar_p><or_or><sentvar_q>',), ('<sentvar_r>',)))

    def test_wrong_rule(self):
        self.assertEqual(self.rule('<sentvar_p><and_^><sentvar_q>'), None)

    def test_brackets(self):
        self.assertEqual(self.rule('(<sentvar_p><and_and><sentvar_r>)<or_v>(<sentvar_q><or_or>(<not_~><sentvar_r>))'), ((
            '<sentvar_p><and_and><sentvar_r>',), ('<sentvar_q><or_or>(<not_~><sentvar_r>)',)))

    def test_more_brackets(self):
        self.assertEqual(self.rule('((<not_~><sentvar_q>)<and_and><sentvar_r>)<or_v>((<sentvar_q>)<or_or>(<not_~>(<sentvar_r>)))'), ((
            '(<not_~><sentvar_q>)<and_and><sentvar_r>',), ('(<sentvar_q>)<or_or>(<not_~>(<sentvar_r>))',)))



class Test_false_and(test.TestCase):

    def setUp(self):
        self.rule = new_notation(zol.RULES['false and'].strict)

    def test_basic(self):
        self.assertEqual(self.rule('<not_~>(<sentvar_p><and_^><sentvar_q>)'), ((
            '<not_~><sentvar_p>',), ('<not_~><sentvar_q>',)))

    def test_basicbracket(self):
        self.assertEqual(self.rule('<not_~>((<sentvar_p>)<and_^>(<sentvar_q>))'), ((
            '<not_~><sentvar_p>',), ('<not_~><sentvar_q>',)))

    def test_double(self):
        self.assertEqual(self.rule('<not_~>((<sentvar_p><and_^><sentvar_q>)<and_^><sentvar_r>)'), ((
            '<not_~>(<sentvar_p><and_^><sentvar_q>)',), ('<not_~><sentvar_r>',)))

    def test_wrong_rule(self):
        self.assertEqual(
            self.rule('<not_~>(<sentvar_p><or_or><sentvar_q>)'), None)

    def test_first_negated(self):
        self.assertEqual(
            self.rule('<not_~><sentvar_p><and_^><sentvar_q>'), None)

    def test_brackets(self):
        self.assertEqual(self.rule('<not_~>((<sentvar_p><or_or><sentvar_r>)<and_^>(<sentvar_q><or_or>(<not_~><sentvar_r>)))'), ((
            '<not_~>(<sentvar_p><or_or><sentvar_r>)',), ('<not_~>(<sentvar_q><or_or>(<not_~><sentvar_r>))',)))

    def test_more_brackets(self):
        self.assertEqual(self.rule('<not_~>(((<not_~><sentvar_q>)<or_or><sentvar_r>)<and_^>((<sentvar_q>)<or_or>(<not_~>(<sentvar_r>))))'), ((
            '<not_~>((<not_~><sentvar_q>)<or_or><sentvar_r>)',), ('<not_~>((<sentvar_q>)<or_or>(<not_~>(<sentvar_r>)))',)))



class Test_false_or(test.TestCase):

    def setUp(self):
        self.rule = new_notation(zol.RULES['false or'].strict)

    def test_basic(self):
        self.assertEqual(self.rule('<not_~>(<sentvar_p><or_or><sentvar_q>)'),
                         tuple([tuple(['<not_~><sentvar_p>', '<not_~><sentvar_q>'])]))

    def test_basicbracket(self):
        self.assertEqual(self.rule('<not_~>((<sentvar_p>)<or_or>(<sentvar_q>))'),
                         tuple([tuple(['<not_~><sentvar_p>', '<not_~><sentvar_q>'])]))

    def test_double(self):
        self.assertEqual(self.rule('<not_~>((<sentvar_p><or_or><sentvar_q>)<or_or>(<sentvar_r>))'),
                         tuple([tuple(['<not_~>(<sentvar_p><or_or><sentvar_q>)', '<not_~><sentvar_r>'])]))

    def test_wrong_rule(self):
        self.assertEqual(
            self.rule('<not_~>(<sentvar_p><and_^><sentvar_q>)'), None)

    def test_first_negated(self):
        self.assertEqual(
            self.rule('<not_~><sentvar_p><or_or><sentvar_q>'), None)

    def test_brackets(self):
        self.assertEqual(self.rule('<not_~>((<sentvar_p><and_and><sentvar_r>)<or_v>(<sentvar_q><or_or>(<not_~><sentvar_r>)))'),
                         tuple([tuple(['<not_~>(<sentvar_p><and_and><sentvar_r>)', '<not_~>(<sentvar_q><or_or>(<not_~><sentvar_r>))'])]))

    def test_more_brackets(self):
        self.assertEqual(self.rule('<not_~>(((<not_~><sentvar_q>)<and_and><sentvar_r>)<or_v>((<sentvar_q>)<or_or>(<not_~>(<sentvar_r>))))'),
                         tuple([tuple(['<not_~>((<not_~><sentvar_q>)<and_and><sentvar_r>)', '<not_~>((<sentvar_q>)<or_or>(<not_~>(<sentvar_r>)))'])]))



class Test_true_imp(test.TestCase):

    def setUp(self):
        self.rule = new_notation(zol.RULES['true imp'].strict)

    def test_basic(self):
        self.assertEqual(self.rule('<sentvar_p><imp_imp><sentvar_q>'),
                         (('<not_~><sentvar_p>',), ('<sentvar_q>',)))

    def test_basicbracket(self):
        self.assertEqual(self.rule(
            '(<sentvar_p>)<imp_imp>(<sentvar_q>)'), (('<not_~><sentvar_p>',), ('<sentvar_q>',)))

    def test_double(self):
        self.assertEqual(self.rule('(<sentvar_p><imp_imp><sentvar_q>)<imp_imp>(<sentvar_r>)'), ((
            '<not_~>(<sentvar_p><imp_imp><sentvar_q>)',), ('<sentvar_r>',)))

    def test_wrong_rule(self):
        self.assertEqual(self.rule('<sentvar_p><and_^><sentvar_q>'), None)

    def test_brackets(self):
        self.assertEqual(self.rule('(<sentvar_p><and_and><sentvar_r>)<imp_imp>(<sentvar_q><imp_imp>(<not_~><sentvar_r>))'), ((
            '<not_~>(<sentvar_p><and_and><sentvar_r>)',), ('<sentvar_q><imp_imp>(<not_~><sentvar_r>)',)))

    def test_more_brackets(self):
        self.assertEqual(self.rule('((<not_~><sentvar_q>)<and_and><sentvar_r>)<imp_imp>((<sentvar_q>)<imp_imp>(<not_~>(<sentvar_r>)))'), ((
            '<not_~>((<not_~><sentvar_q>)<and_and><sentvar_r>)',), ('(<sentvar_q>)<imp_imp>(<not_~>(<sentvar_r>))',)))



class Test_false_imp(test.TestCase):

    def setUp(self):
        self.rule = new_notation(zol.RULES['false imp'].strict)

    def test_basic(self):
        self.assertEqual(self.rule('<not_~>(<sentvar_p><imp_imp><sentvar_q>)'),
                         tuple([tuple(['<sentvar_p>', '<not_~><sentvar_q>'])]))

    def test_basicbracket(self):
        self.assertEqual(self.rule('<not_~>((<sentvar_p>)<imp_imp>(<sentvar_q>))'),
                         tuple([tuple(['<sentvar_p>', '<not_~><sentvar_q>'])]))

    def test_double(self):
        self.assertEqual(self.rule('<not_~>((<sentvar_p><imp_imp><sentvar_q>)<imp_imp>(<sentvar_r>))'),
                         tuple([tuple(['<sentvar_p><imp_imp><sentvar_q>', '<not_~><sentvar_r>'])]))

    def test_wrong_rule(self):
        self.assertEqual(
            self.rule('<not_~>(<sentvar_p><and_^><sentvar_q>)'), None)

    def test_first_negated(self):
        self.assertEqual(
            self.rule('<not_~><sentvar_p><imp_imp><sentvar_q>'), None)

    def test_brackets(self):
        self.assertEqual(self.rule('<not_~>((<sentvar_p><and_and><sentvar_r>)<imp_imp>(<sentvar_q><imp_imp>(<not_~><sentvar_r>)))'),
                         tuple([tuple(['<sentvar_p><and_and><sentvar_r>', '<not_~>(<sentvar_q><imp_imp>(<not_~><sentvar_r>))'])]))

    def test_more_brackets(self):
        self.assertEqual(self.rule('<not_~>(((<not_~><sentvar_q>)<and_and><sentvar_r>)<imp_imp>((<sentvar_q>)<imp_imp>(<not_~>(<sentvar_r>))))'),
                         tuple([tuple(['(<not_~><sentvar_q>)<and_and><sentvar_r>', '<not_~>((<sentvar_q>)<imp_imp>(<not_~>(<sentvar_r>)))'])]))



class Test_double_neg(test.TestCase):

    def setUp(self):
        self.rule = new_notation(zol.RULES['double not'].strict)

    def test_basic(self):
        self.assertEqual(self.rule(
            '<not_~><not_~>(<sentvar_p><or_or><sentvar_q>)'), (('<sentvar_p><or_or><sentvar_q>',),))

    def test_wrong_amount1(self):
        self.assertEqual(
            self.rule('<not_~>(<sentvar_p><and_^><sentvar_q>)'), None)

    def test_wrong_amount0(self):
        self.assertEqual(self.rule('<sentvar_p><and_^><sentvar_q>'), None)

    def test_long(self):
        self.assertEqual(self.rule('<not_~><not_~>(((<not_~><sentvar_q>)<and_and><sentvar_r>)<or_v>((<sentvar_q>)<or_or>(<not_~>(<sentvar_r>))))'),
                         (('((<not_~><sentvar_q>)<and_and><sentvar_r>)<or_v>((<sentvar_q>)<or_or>(<not_~>(<sentvar_r>)))',),))

    def test_middlebracket(self):
        self.assertEqual(self.rule(
            '<not_~>(<not_~>(<sentvar_p><or_or><sentvar_q>))'), (('<sentvar_p><or_or><sentvar_q>',),))

    def test_nobracket(self):
        self.assertEqual(
            self.rule('<not_~><not_~><sentvar_p>'), (('<sentvar_p>',),))


class Test_bracket_reduction(test.TestCase):

    def setUp(self):
        self.func = new_notation(zol.utils.reduce_brackets)

    def test_nobrackets(self):
        self.assertEqual(self.func(
            '<sentvar_p><and_^><sentvar_q>'), '<sentvar_p><and_^><sentvar_q>')

    def test_simple(self):
        self.assertEqual(self.func(
            '(<sentvar_p><and_^><sentvar_q>)'), '<sentvar_p><and_^><sentvar_q>')

    def test_left_not_reductable(self):
        self.assertEqual(self.func(
            '<not_~>(<sentvar_p><and_^><sentvar_q>)'), '<not_~>(<sentvar_p><and_^><sentvar_q>)')

    def test_right_not_reductable(self):
        self.assertEqual(self.func('(<sentvar_p><and_^><sentvar_q>)<and_^><sentvar_q>'),
                         '(<sentvar_p><and_^><sentvar_q>)<and_^><sentvar_q>')

    def test_complex_reductable(self):
        self.assertEqual(self.func('((<not_~>((<sentvar_p><and_^><sentvar_q>)<and_^><sentvar_r>)))'),
                         '<not_~>((<sentvar_p><and_^><sentvar_q>)<and_^><sentvar_r>)')

    def test_complex(self):
        self.assertEqual(self.func('<not_~>((<sentvar_p><and_^><sentvar_q>)<and_^><sentvar_r>)'),
                         '<not_~>((<sentvar_p><and_^><sentvar_q>)<and_^><sentvar_r>)')

    def test_double_and(self):
        self.assertEqual(self.func('(<sentvar_p><and_^><sentvar_q>)<and_^>(<sentvar_p><and_^><sentvar_q>)'),
                         '(<sentvar_p><and_^><sentvar_q>)<and_^>(<sentvar_p><and_^><sentvar_q>)')

    def test_double_and_reductable(self):
        self.assertEqual(self.func('((((<sentvar_p><and_^><sentvar_q>)<and_^>(<sentvar_p><and_^><sentvar_q>))))'),
                         '(<sentvar_p><and_^><sentvar_q>)<and_^>(<sentvar_p><and_^><sentvar_q>)')

    def test_long_complex_reductable(self):
        self.assertEqual(self.func('((<not_~>(<not_~>(((<not_~><sentvar_q>)<and_and><sentvar_r>)<or_v>((<sentvar_q>))<or_or>(<not_~>(<sentvar_r>))))))'),
                         '<not_~>(<not_~>(((<not_~><sentvar_q>)<and_and><sentvar_r>)<or_v>((<sentvar_q>))<or_or>(<not_~>(<sentvar_r>))))')

    def test_long_complex(self):
        self.assertEqual(self.func('<not_~>(<not_~>(((<not_~><sentvar_q>)<and_and><sentvar_r>)<or_v>((<sentvar_q>))<or_or>(<not_~>(<sentvar_r>))))'),
                         '<not_~>(<not_~>(((<not_~><sentvar_q>)<and_and><sentvar_r>)<or_v>((<sentvar_q>))<or_or>(<not_~>(<sentvar_r>))))')



if __name__ == "__main__":
    test.main()
