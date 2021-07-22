import importlib
import importlib.util
import inspect
import logging
import os
import sys
import shutil
import typing as tp
from collections import OrderedDict

Module = type(tp)

logger = logging.getLogger('pop')


def gen_functionDS(func_name: str, returns: tp.Any, *args: tp.Any) -> tuple[str, tuple[tuple[tp.Any], tp.Any]]:
    return (func_name, (args, returns))


####
# Socket Interface
####


class Socket(object):

    # Cache-related functions
    cache = OrderedDict()

    @classmethod
    def clear_cache(cls, amount: int = 0):
        """Clears the plugin cache. Will delete the supplied amount of the oldest plugins if provided with a number"""
        logger.warning("Starting cache clearing")
        if amount > 0:
            for _ in range(amount):
                name = cls.cache.popitem(False)[0]
                logger.info(
                    f"Deleting {name[1]} (from socket {name[0]}) from cache")
        else:
            cls.cache = OrderedDict()

    # Magic

    def __init__(self, socket_name: str, abs_path: str, version: str, template: tp.Union[str, dict[str, tuple[tuple[tp.Any], tp.Any]]], plugged: str = ""):
        """Allows the user to smoothly interchange plugins by providing the interface call functions

        Args:
            socket_name (str): Name given to the socket, will be used to identify plugins
            abs_path (str): Absolute path to the directory with plugins; use `<> test <>` for testing
            version (str): Version of the socket, will be checked with sockets. Supported format: "x.x.z". 
                Changes on "z level" will be omitted in version checking
            template (str OR dict[str, tuple[tuple[tp.Any], tp.Any]]): Used as a reference in interface verification. 
                When supplied with file name system will use it to generate templates. `gen_functionDS` generates the primitive version.
            plugged (str, optional): Name of a plugin which will be connected. Defaults to "".
        """
        # Plugin's directory
        if abs_path != "<> test <>":
            assert os.path.isabs(abs_path), "Path not absolute"
            if not os.path.exists(abs_path):
                os.mkdir(abs_path)
        self.dir = abs_path

        # Version checking
        self.version = [int(i) for i in version.split('.')]
        assert len(self.version) == 3, "Wrong version format"

        self.name = socket_name
        self.read_template(template)

        # Plugging
        if not plugged:
            self.plugin = None
        else:
            self.plug(plugged)

    def __call__(self) -> Module:
        """Use this to get access to the plugin

        Raises:
            PluginError: Raised if nothing is plugged in

        Returns:
            Module: Plugged module
        """
        if self.plugin:
            return self.plugin
        else:
            raise PluginError(f"{self.name} lacks a plugin")

    # Get functions

    def get_plugin_name(self):
        return self.__call__().__name__

    def isplugged(self):
        return bool(self.plug)

    # Plugin manipulation

    def generate_template(self, plugin_name: str) -> None:
        """Creates a file called `plugin_name` from the socket's template

        :param plugin_name: Name of the new plugin
        :type plugin_name: str
        :raises FileExistsError: File called `plugin_name` already exists
        :raises FileNotFoundError: Template not found
        """
        if plugin_name.endswith(".py"):
            plugin_name = plugin_name[:-3]
        if self.template:
            try:
                shutil.copyfile(f"{self.dir}/{self.template}.py",
                                f"{self.dir}/{plugin_name}.py")
            except shutil.SameFileError:
                raise FileExistsError(
                    f"{plugin_name} already exists in {self.name}'s directory")
        else:
            raise FileNotFoundError(
                f"There is no template available for {self.name}'s plugins")

    def find_plugins(self) -> list[str]:
        """
        Returns:
            list[str]: List of all plugins in the socket's directory
        """
        return [
            file[:-3]
            for file in os.listdir(self.dir)
            if file.endswith(".py")
            and file
            not in {f"{self.template}.py", "__utils__.py", "__init__.py"}
        ]

    def unplug(self) -> None:
        """Unplugs the current plugin, not recommended"""
        logger.warning(
            f"{self.get_plugin_name()} disconnected from {self.name}")
        self.plug = None

    def plug(self, plugin_name: str) -> None:
        """Connects the plugin to the socket

        Args:
            plugin_name (str): Name of the plugin

        Raises:
            FileNotFoundError: Raised if module with this name does not exist
            PluginError: Wrong socket
            VersionError: Wrong plugin version
            FunctionInterfaceError: Socket doesn't allow this function interface
            LackOfFunctionsError: Module lacks a function needed to connect to the socket
        """
        # Retrieval
        assert self.dir != "<> test <>"
        if plugin_name.endswith(".py"):
            plugin_name = plugin_name[:-3]
        if plugin_name not in self.find_plugins():
            logger.error(f"{plugin_name} doesn't exist in {self.dir}")
            raise FileNotFoundError(
                f"{plugin_name} doesn't exist in {self.dir}")
        logger.info(f"Importing {plugin_name}")
        plug_obj = self._import(plugin_name)

        # Verification
        self.check_name(
            plug_obj, f"{plugin_name} is meant to be plugged into {plug_obj.SOCKET}, not {self.name}")
        self.check_version(
            plug_obj, f'Wrong version - Socket: {".".join((str(i) for i in self.version))}; Plugin: {plug_obj.VERSION}')
        self.fits(plug_obj)

        # Connecting to the system
        self.plugin = plug_obj
        logger.warning(f"{plugin_name} connected to {self.name}")

    def _import(self, plugin_name: str) -> Module:
        """Imports a module named `plugin_name` from `self.dir`; USE PLUG INSTEAD"""
        module = self.cache.get((self.name, plugin_name), None)
        if module:
            self.cache.move_to_end((self.name, plugin_name))
        else:
            module = self._only_import(plugin_name)
        return module

    def _only_import(self, plugin_name):
        sys.path.insert(0, self.dir)
        spec = importlib.util.spec_from_file_location(
            plugin_name, f"{self.dir}/{plugin_name}.py")
        result = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(result)
        sys.path.pop(0)
        if plugin_name != self.template:
            self.cache[(self.name, plugin_name)] = result
        return result

    # Verification

    def check_name(self, plugin: Module, message: str) -> None:
        """Verifies socket name of the plugin

        :param plugin: Plugin to test
        :type plugin: Module
        :param message: Message to show in the exception
        :type message: str
        :raises PluginError: Wrong plugin name
        """
        assert 'SOCKET' in dir(plugin), "No socket name in the plugin"
        if plugin.SOCKET != self.name:
            raise PluginError(message)
        logger.debug(f"Checked socket")
        return True

    def check_version(self, plugin: Module, message: str) -> None:
        """Verifies plugin versions. Supported format: "x.x.z", changes on "z level" will be omitted in version checking

        :param plugin: Checked plugin
        :type plugin: Module
        :param message: Message to add if an exception is raised
        :type message: str
        :raises VersionError: Wrong plugin version
        """
        assert 'VERSION' in dir(plugin), "No plugin version in the plugin"
        plugin_ver = [int(i) for i in plugin.VERSION.split(".")]
        if len(plugin_ver) != 3:
            logger.error(
                f"Wrong version format in the plugin: {str(plugin.VERSION)}")
            raise PluginError(
                f"Wrong version format used in the plugin: {str(plugin.VERSION)}")
        if plugin_ver[:-1] != self.version[:-1]:
            raise VersionError(message)

        logger.debug(f"Checked version")
        return True

    def fits(self, plugin: Module) -> bool:
        """Function checks if module is connectable to the socket

        Args:
            plugin (Module)

        Raises:
            FunctionInterfaceError: Socket doesn't allow this function interface
            LackOfFunctionsError: Module lacks a function needed to connect to the socket
        """
        set_names = set(self.func_names)
        set_plugin = set(dir(plugin))
        if not set_names.issubset(set_plugin):
            raise LackOfFunctionsError(
                self, plugin.__name__, set_names-set_plugin)
        members = dict(inspect.getmembers(plugin, callable))
        for i in set_names:
            self._functionfit(members[i])
        return True

    def _functionfit(self, func: tp.Callable) -> bool:
        """Checks compatibility of the function's interface

        Raises:
            FunctionInterfaceError: Socket doesn't allow this function interface - wrong type of arguments/returned value.
        """
        if self.functions.get(func.__name__, None) is None:
            return True
        sig = inspect.signature(func)
        args = tuple(sig.parameters[j].annotation for j in sig.parameters.keys())
        proper = self.functions[func.__name__]

        # Argument checking
        if args != proper[0]:
            raise FunctionInterfaceError(True, self, func, args)

        # Return checking
        elif sig.return_annotation != proper[1]:
            raise FunctionInterfaceError(
                False, self, func, sig.return_annotation)
        else:
            logger.debug(f"{func.__name__} compatible")
            return True
            
    def read_template(self, template: tp.Union[str, dict[str, tuple[tuple[tp.Any], tp.Any]]]):
        """
        Reads/Retrieves a template and modifies the shape of the socket according to the objects given in the template
        """
        if isinstance(template, str):
            if template.endswith(".py"):
                template = template[:-3]
            if not os.path.isfile(f"{self.dir}/{template}.py"):
                raise FileNotFoundError(
                    f"{template}.py doesn't exist in {self.dir}")
            self.template = template
            self.functions = self._get_functions_from_template(template)
        else:
            self.template = None
            self.functions = template
        self.func_names = self.functions.keys()

    def _get_functions_from_template(self, template_file_name: str) -> dict[str, tuple[tuple[tp.Any], tp.Any]]:
        """Generates information about function annotations of a template 

        :param template_file_name: Name of the template file
        :type template_file_name: str
        :return: {function name:((*argument types), return type)}
        :rtype: dict[str, tuple[tuple[tp.Any], tp.Any]]
        """

        # Verification
        template = self._import(template_file_name)
        self.check_version(
            template, f"Version of {template.__name__} not compatible with {self.name}")
        self.check_name(
            template, f"{template.__name__} can be a socket of {template.SOCKET}, not {self.name}")

        # Template reading
        funcs = {}
        for i in inspect.getmembers(template, callable):
            if i[0].endswith('Error'):
                continue
            sig = inspect.signature(i[1])
            args = tuple(sig.parameters[j].annotation for j in sig.parameters.keys())
            funcs[i[0]] = (args, inspect.signature(i[1]).return_annotation)
        return funcs


class DummySocket(Socket):
    """
    A socket that that doesn't load the plugin. Use to avoid circular references
    """

    def __call__(self):
        raise NotImplementedError("It's a dummy")

    def fits(self, plugin):
        raise NotImplementedError("It's a dummy")

    def get_plugin_name(self) -> str:
        return self.plug

    def plug(self, plugin_name: str) -> None:
        self.plugin = plugin_name
        logger.warning(f"{plugin_name} connected to {self.name} (dummy)")

####
# Exceptions
####


class PluginError(Exception):
    """Mother of exceptions used to deal with plugin problems"""

    def __init__(self, msg):
        logger.error(msg)
        super().__init__(msg)


class LackOfFunctionsError(PluginError):
    """Raised if module lacks important functions"""

    def __init__(self, socket: Socket, module_name: str, functions: list[str]):
        info = f"{module_name} can't be connected to {socket.name}, because it lacks {len(functions)} function{'s'*(len(functions)>1)}"
        self.lacking = [
            f"{i}: {', '.join(str(socket.functions[i][0]))} -> {str(socket.functions[i][1])}" for i in functions]
        super().__init__(info)


class FunctionInterfaceError(PluginError):
    """Raised if function has a bad interface"""

    def __init__(self, argument_problem: bool, socket: Socket, func: tp.Callable, what_is: tp.Any):
        if argument_problem:
            info = f"{func.__name__} can't be connected to {socket.name}; " + \
                f"Arguments are: {str(what_is)}, should be: {str(socket.functions[func.__name__][0])}"
        else:
            info = f"{func.__name__} can't be connected to {socket.name}; " + \
                f"Return is: {str(what_is)}, should be: {str(socket.functions[func.__name__][1])}"
        super().__init__(info)


class VersionError(PluginError):
    """Raised if plugin has an incompatible version"""
    pass
