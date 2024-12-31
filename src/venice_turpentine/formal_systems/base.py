from abc import ABC, abstractmethod


class FormalSystem(ABC):

    @property
    @abstractmethod
    def operator_precedence(self) -> dict[str, int]:
        pass

    @property
    @abstractmethod
    def unary_operators(self) -> list[str]:
        pass

    @property
    def operator_precedence_scale(self) -> int:
        return max(self.operator_precedence.values()) + 1
