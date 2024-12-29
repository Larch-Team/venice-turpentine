from dataclasses import dataclass


@dataclass(init=True, repr=False, frozen=True)
class Token:
    """Instancja elementu alfabetu formalnego"""

    type_: str
    lexem: str
    is_literal: bool = False

    def __str__(self):
        return self.lexem

    def __repr__(self):
        return f"{self.type_.upper()}({self.lexem})"

    @classmethod
    def literal(cls, s: str):
        return cls(s, s, is_literal=True)
