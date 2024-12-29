from abc import ABC, abstractmethod


class FormalSystem(ABC):

    @abstractmethod
    def get_operator_precedence(self) -> dict[str, int]:
        pass
