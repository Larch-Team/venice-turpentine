from dataclasses import dataclass
import logging
from typing import Any, Callable, Union


logger = logging.getLogger('engine')

# engine

class EngineError(Exception):
    def __init__(self, msg: str, *args, **kwargs):
        logger.error(msg)
        super().__init__(msg, *args, **kwargs)

class LrchLexerError(Exception):
    pass

class SentenceError(Exception):
    pass

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
            info = (
                f"{func.__name__} can't be connected to {socket.name}; "
                + f'Arguments are: {what_is}, should be: {socket.functions[func.__name__][0]}'
            )

        else:
            info = (
                f"{func.__name__} can't be connected to {socket.name}; "
                + f'Return is: {what_is}, should be: {socket.functions[func.__name__][1]}'
            )

        super().__init__(info)


class VersionError(PluginError):
    """Raised if plugin has an incompatible version"""
    pass

# Formal

class FormalError(Exception):
    pass


@dataclass(init=True, repr=True, frozen=True)
class UserMistake:
    name: str
    default: str
    additional: Union[dict[str, Any], None] = None
    
    def __eq__(self, o: object) -> bool:
        if isinstance(o, UserMistake):
            return self.name == o.name and self.additional == o.additional
        else:
            return False
    
    def __str__(self) -> str:
        return self.default
    
class RaisedUserMistake(UserMistake, Exception):
    pass

class FileManagerError(Exception):
    pass