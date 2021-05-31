import typing as tp

lexicon = None


class CompilerError(Exception):
    pass


class MultipleTypesError(CompilerError):

    def __init__(self, multiple, *args, **kwargs):
        lists = [" - ".join((i[0], ", ".join(i[1]))) for i in multiple.items()]
        msg = "\n".join(("Multiple types found for:", *lists))
        super().__init__(msg, *args, **kwargs)


Sentence = tp.NewType("Sentence", list[str])

NON_CONVERTIBLE = ("(", ")")
