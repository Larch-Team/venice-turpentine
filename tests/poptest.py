import unittest as test
from importlib import import_module
import os
import sys

sys.path.append('../app')
import pop_engine
import example1

exampleproject_path = os.path.abspath('example_project')


class Test_GenerateFuncDataStructure(test.TestCase):

    def test_addition(self):
        obj = pop_engine.gen_functionDS('', int, int, int)
        self.assertEqual(obj, ('', ((int, int), int)))

    def test_addition_list(self):
        obj = pop_engine.gen_functionDS('', int, *(int, int))
        self.assertEqual(obj, ('', ((int, int), int)))

    def test_NoArgs_None(self):
        obj = pop_engine.gen_functionDS('', None)
        self.assertEqual(obj, ('', ((), None)))

    def test_NoArgs_int(self):
        obj = pop_engine.gen_functionDS('', int)
        self.assertEqual(obj, ('', ((), int)))

    def test_4args_int(self):
        obj = pop_engine.gen_functionDS('', int, str, int, list, tuple)
        self.assertEqual(obj, ('', ((str, int, list, tuple), int)))


class Test_GetFuncFromTemplate(test.TestCase):

    def test_withpy(self):
        funcs = dict((
            pop_engine.gen_functionDS('add', int, int, int),
            pop_engine.gen_functionDS('sub', int, int, int),
            pop_engine.gen_functionDS('a', None)
        ))
        socket = pop_engine.Socket(
            'example_project', exampleproject_path, "0.0.0", 'example2.py')
        self.assertEqual(socket.functions, funcs)

    def test_withoutpy(self):
        funcs = dict((
            pop_engine.gen_functionDS('add', int, int, int),
            pop_engine.gen_functionDS('sub', int, int, int),
            pop_engine.gen_functionDS('a', None)
        ))
        socket = pop_engine.Socket(
            'example_project', exampleproject_path, "0.0.0", 'example2')
        self.assertEqual(socket.functions, funcs)

    def test_wrong_version(self):
        funcs = dict((
            pop_engine.gen_functionDS('add', int, int, int),
            pop_engine.gen_functionDS('sub', int, int, int),
            pop_engine.gen_functionDS('a', None)
        ))
        with self.assertRaises(pop_engine.VersionError):
            socket = pop_engine.Socket(
                'example_project', exampleproject_path, "1.0.0", 'example2.py')

    def test_wrong_folder(self):
        funcs = dict((
            pop_engine.gen_functionDS('add', int, int, int),
            pop_engine.gen_functionDS('sub', int, int, int),
            pop_engine.gen_functionDS('a', None)
        ))
        with self.assertRaises(pop_engine.VersionError):
            socket = pop_engine.Socket(
                'another_test', exampleproject_path, "1.0.0", 'example2.py')

    def test_no_file(self):
        funcs = dict((
            pop_engine.gen_functionDS('add', int, int, int),
            pop_engine.gen_functionDS('sub', int, int, int),
            pop_engine.gen_functionDS('a', None)
        ))
        with self.assertRaises(FileNotFoundError):
            socket = pop_engine.Socket(
                'example_project', exampleproject_path, "0.0.0", 'not_here')


class TestFunctionFit(test.TestCase):

    def setUp(self):
        funcs = dict((
            pop_engine.gen_functionDS('add', int, int, int),
            pop_engine.gen_functionDS('sub', int, int, int),
            pop_engine.gen_functionDS('sub_wrongin', int, int, int),
            pop_engine.gen_functionDS('sub_wrongout', int, int, int),
            pop_engine.gen_functionDS('random', int),
            pop_engine.gen_functionDS('str_int_none', None, str, int)
        ))
        self.socket = pop_engine.Socket(
            'example_project', "<> test <>", "0.0.0", funcs)

    def test_addition(self):
        self.assertTrue(self.socket._functionfit(example1.add))

    def test_str_int_none(self):
        self.assertTrue(self.socket._functionfit(example1.str_int_none))

    def test_no_in(self):
        self.assertTrue(self.socket._functionfit(example1.random))

    def test_not_plugged(self):
        self.assertTrue(self.socket._functionfit(example1.not_plugged))

    def test_sub_wrong_args(self):
        with self.assertRaises(pop_engine.FunctionInterfaceError):
            self.socket._functionfit(example1.sub_wrongin)

    def test_sub_wrong_return(self):
        with self.assertRaises(pop_engine.FunctionInterfaceError):
            self.socket._functionfit(example1.sub_wrongout)


class TestSocketFit(test.TestCase):

    def test_good_import(self):
        funcs = dict((
            pop_engine.gen_functionDS('add', int, int, int),
            pop_engine.gen_functionDS('sub', int, int, int),
            pop_engine.gen_functionDS('random', int),
            pop_engine.gen_functionDS('str_int_none', None, str, int)
        ))
        self.socket = pop_engine.Socket(
            'example_project', "<> test <>", "0.0.0", funcs)
        self.assertTrue(self.socket.fits(example1))

    def test_wrong_arg(self):
        funcs = dict((
            pop_engine.gen_functionDS('add', int, int, int),
            pop_engine.gen_functionDS('sub', int, int, int),
            pop_engine.gen_functionDS('sub_wrongin', int, int, int),
            pop_engine.gen_functionDS('random', int),
            pop_engine.gen_functionDS('str_int_none', None, str, int)
        ))
        self.socket = pop_engine.Socket(
            'example_project', "<> test <>", "0.0.0", funcs)
        with self.assertRaises(pop_engine.FunctionInterfaceError):
            self.socket.fits(example1)

    def test_wrong_return(self):
        funcs = dict((
            pop_engine.gen_functionDS('add', int, int, int),
            pop_engine.gen_functionDS('sub', int, int, int),
            pop_engine.gen_functionDS('sub_wrongout', int, int, int),
            pop_engine.gen_functionDS('random', int),
            pop_engine.gen_functionDS('str_int_none', None, str, int)
        ))
        self.socket = pop_engine.Socket(
            'example_project', "<> test <>", "0.0.0", funcs)
        with self.assertRaises(pop_engine.FunctionInterfaceError):
            self.socket.fits(example1)

    def test_lack_function(self):
        funcs = dict((
            pop_engine.gen_functionDS('add', int, int, int),
            pop_engine.gen_functionDS('sub', int, int, int),
            pop_engine.gen_functionDS('addstring', str, str, str),
            pop_engine.gen_functionDS('sub_wrongout', int, int, int),
            pop_engine.gen_functionDS('random', int),
            pop_engine.gen_functionDS('str_int_none', None, str, int)
        ))
        self.socket = pop_engine.Socket(
            'example_project', "<> test <>", "0.0.0", funcs)
        with self.assertRaises(pop_engine.LackOfFunctionsError):
            self.socket.fits(example1)

    def test_changed_names(self):
        funcs = dict((
            pop_engine.gen_functionDS('ger', int, int, int),
            pop_engine.gen_functionDS('fe', int, int, int),
        ))
        self.socket = pop_engine.Socket(
            'example_project', "<> test <>", "0.0.0", funcs)
        with self.assertRaises(pop_engine.LackOfFunctionsError):
            self.socket.fits(example1)


class TestMisc(test.TestCase):

    def test_find_plugin(self):
        funcs = dict((
            pop_engine.gen_functionDS('add', int, int, int),
            pop_engine.gen_functionDS('sub', int, int, int)
        ))
        self.socket = pop_engine.Socket(
            'example_project', exampleproject_path, "0.0.0", funcs)
        tested = self.socket.find_plugins()
        self.assertSetEqual(set(tested), {
                            'example2', 'example2_', 'example_compatible', 'example_wrong_ver_for'})

    def test_create_plugin(self):
        funcs = dict((
            pop_engine.gen_functionDS('add', int, int, int),
            pop_engine.gen_functionDS('sub', int, int, int),
            pop_engine.gen_functionDS('a', None)
        ))
        socket = pop_engine.Socket(
            'example_project', exampleproject_path, "0.0.0", 'example2.py')
        socket.generate_template('test_plugin')
        tested = os.path.isfile(f"{exampleproject_path}/test_plugin.py")
        os.remove(f"{exampleproject_path}/test_plugin.py")
        self.assertTrue(tested)

    def test_create_plugin_already_exists(self):
        funcs = dict((
            pop_engine.gen_functionDS('add', int, int, int),
            pop_engine.gen_functionDS('sub', int, int, int),
            pop_engine.gen_functionDS('a', None)
        ))
        socket = pop_engine.Socket(
            'example_project', exampleproject_path, "0.0.0", 'example2.py')
        with self.assertRaises(FileExistsError):
            socket.generate_template('example2.py')


class TestPlugging(test.TestCase):

    def test_good_import(self):
        funcs = dict((
            pop_engine.gen_functionDS('add', int, int, int),
            pop_engine.gen_functionDS('sub', int, int, int),
        ))
        self.socket = pop_engine.Socket(
            'example_project', exampleproject_path, "0.0.0", funcs)
        self.socket.plug("example2")
        self.assertTrue(self.socket().__name__ == 'example2')

    def test_partial_compatibility(self):
        funcs = dict((
            pop_engine.gen_functionDS('add', int, int, int),
            pop_engine.gen_functionDS('sub', int, int, int),
        ))
        self.socket = pop_engine.Socket(
            'example_project', exampleproject_path, "0.0.0", funcs)
        self.socket.plug("example_compatible")
        self.assertTrue(self.socket().__name__ == 'example_compatible')

    def test_plugin_change(self):
        funcs = dict((
            pop_engine.gen_functionDS('add', int, int, int),
            pop_engine.gen_functionDS('sub', int, int, int),
        ))
        self.socket = pop_engine.Socket(
            'example_project', exampleproject_path, "0.0.0", funcs)
        self.socket.plug("example2")
        self.socket.plug("example2_")
        self.assertTrue(self.socket().__name__ == "example2_")

    def test_plugin_doesnt_exist(self):
        funcs = dict((
            pop_engine.gen_functionDS('add', int, int, int),
            pop_engine.gen_functionDS('sub', int, int, int),
        ))
        self.socket = pop_engine.Socket(
            'example_project', exampleproject_path, "0.0.0", funcs)
        with self.assertRaises(FileNotFoundError):
            self.socket.plug("does_not_exist")

    def test_function_doesnt_exist(self):
        funcs = dict((
            pop_engine.gen_functionDS('add', int, int, int),
            pop_engine.gen_functionDS('sub', int, int, int),
            pop_engine.gen_functionDS('does_not_exist', None)
        ))
        self.socket = pop_engine.Socket(
            'example_project', exampleproject_path, "0.0.0", funcs)
        with self.assertRaises(pop_engine.LackOfFunctionsError):
            self.socket.plug("example2")

    def test_wrong_interface(self):
        funcs = dict((
            pop_engine.gen_functionDS('add', int, int, int),
            pop_engine.gen_functionDS('sub', int, int, str)
        ))
        self.socket = pop_engine.Socket(
            'example_project', exampleproject_path, "0.0.0", funcs)
        with self.assertRaises(pop_engine.FunctionInterfaceError):
            self.socket.plug("example2")

    def test_wrong_version(self):
        funcs = dict((
            pop_engine.gen_functionDS('add', int, int, int),
            pop_engine.gen_functionDS('sub', int, int, int)
        ))
        self.socket = pop_engine.Socket(
            'example_project', exampleproject_path, "1.0.0", funcs)
        with self.assertRaises(pop_engine.VersionError):
            self.socket.plug("example2")

    def test_wrong_version_format(self):
        funcs = dict((
            pop_engine.gen_functionDS('add', int, int, int),
            pop_engine.gen_functionDS('sub', int, int, int)
        ))
        self.socket = pop_engine.Socket(
            'example_project', exampleproject_path, "0.0.0", funcs)
        with self.assertRaises(SyntaxError):
            self.socket.plug("example_wrong_ver_for")

    def test_wrong_folder(self):
        funcs = dict((
            pop_engine.gen_functionDS('add', int, int, int),
            pop_engine.gen_functionDS('sub', int, int, int)
        ))
        self.socket = pop_engine.Socket(
            'another_test', exampleproject_path, "0.0.0", funcs)
        with self.assertRaises(pop_engine.PluginError):
            self.socket.plug("example2")


if __name__ == "__main__":
    test.main()
