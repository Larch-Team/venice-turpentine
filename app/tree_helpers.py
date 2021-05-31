from typing import Any, Union, NewType, Iterable
from sentence import Sentence
def _f():
    pass

function = type(_f)

class History(set):
    """Zbiór reprezentujący historię"""
    
    OPS = {
        'pass':     0,
        'clear':    -1
    }

    def __init__(self, iterable: Iterable[Any] = {}) -> None:
        """Zbiór reprezentujący historię"""
        super().__init__(iterable)

    def add_sentence(self, element: Sentence) -> None:
        """Dodaje zdanie `element` do zbioru, o ile już w nim nie jest. Konkretniej dodaje wartość hash zdania."""
        if isinstance(element, list):
            return super().add(hash(element))
        else:
            raise TypeError("History can only store sentences")

    def __call__(self, *coms: tuple[Union[list, Sentence, int, callable]]) -> None:
        """ Używane do manipulacji historią

            Możliwe argumenty:
                - `Sentence`    - dodaje formułę do historii 
                - `callable`    - wykonuje operacje `callable(history)` na obiekcie historii, a wynik nadpisuje jako nową historię; traktuj ją jako `set`
                - `int`         - wykonuje jedną z predefiniowanych operacji:
                    -  0 - operacja pusta
                    - -1 - czyszczenie historii

            :raises TypeError: Typ nie jest obsługiwany 
        """
        for num, command in enumerate(coms):
            if isinstance(command, Sentence):
                self.add_sentence(command)
            elif isinstance(command, list):
                self.add_sentence(Sentence(command))
            elif isinstance(command, function):
                self = History(command(self))
            elif isinstance(command, int):
                if command == -1:  # Clear set
                    self.clear()
                elif command == 0: # Pass
                    pass
            else:
                raise TypeError(f"Historia nie przyjmuje typu {type(command).__name__} (komenda {num+1}.)")

    def __contains__(self, item: Sentence) -> bool:
        return super().__contains__(hash(item))

    def copy(self):
        return History(super().copy())