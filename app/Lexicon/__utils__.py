import typing as tp
from sentence import Sentence

lexicon = None


class CompilerError(Exception):
    pass


class MultipleTypesError(CompilerError):

    def __init__(self, multiple, *args, **kwargs):
        lists = [" - ".join((i[0], ", ".join(i[1]))) for i in multiple.items()]
        msg = "\n".join(("Multiple types found for:", *lists))
        super().__init__(msg, *args, **kwargs)


NON_CONVERTIBLE = ("(", ")")
