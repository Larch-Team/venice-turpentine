from .base import FormalSystem

class DebugFormalSystem(FormalSystem):

    @property
    def operator_precedence(self) -> dict[str, int]:
        return {
            "neg": 3,
            "unary": 3,
            "and": 2,
            "or": 2,
            "imp": 1,
        }

    @property
    def unary_operators(self) -> list[str]:
        return ["neg", "unary"]
