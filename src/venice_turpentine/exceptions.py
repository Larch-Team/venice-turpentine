from dataclasses import dataclass
from typing import Any, Union

from loguru import logger

# engine


class EngineError(Exception):
    def __init__(self, msg: str, *args, **kwargs):
        logger.error(msg)
        super().__init__(msg, *args, **kwargs)


class LexiconError(Exception):
    pass


class FormulaError(Exception):
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
