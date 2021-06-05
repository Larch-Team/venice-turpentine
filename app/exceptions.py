import logging
from typing import Any, Callable


logger = logging.getLogger('engine')

# engine

class EngineError(Exception):
    def __init__(self, msg: str, *args, **kwargs):
        logger.error(msg)
        super().__init__(msg, *args, **kwargs)


# pop_engine

class PluginError(Exception):
    """Mother of exceptions used to deal with plugin problems"""

    def __init__(self, msg):
        logger.error(msg)
        super().__init__(msg)


class LackOfFunctionsError(PluginError):
    """Raised if module lacks important functions"""

    def __init__(self, socket, module_name: str, functions: list[str]):
        info = f"{module_name} can't be connected to {socket.name}, because it lacks {len(functions)} function{'s'*(len(functions)>1)}"
        self.lacking = [
            f"{i}: {', '.join(str(socket.functions[i][0]))} -> {str(socket.functions[i][1])}" for i in functions]
        super().__init__(info)


class FunctionInterfaceError(PluginError):
    """Raised if function has a bad interface"""

    def __init__(self, argument_problem: bool, socket, func: Callable, what_is: Any):
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

# FormalUser

class FormalUserError(Exception):
    pass