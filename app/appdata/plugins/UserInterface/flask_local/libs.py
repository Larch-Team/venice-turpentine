
from typing import Any, Iterator
from string import Template

from sentence import Sentence

def JSONResponse(type_: str, content: Any = None):
    return {'type':type_, 'content': content} if content is not None else {'type':type_}


# TODO: uzupełnić tag
Tag = Template('<a href= $tID $sID $branch >$symbol</a>')

def _clickable(sentence: Sentence, sentenceID: int, branch: str) -> Iterator[str]:
    for tID, symbol in enumerate(sentence.getReadableList()):
        yield Tag.substitute(tID=tID, sID=sentenceID, branch=branch, symbol=symbol)

def get_clickable(sentence: Sentence, sentenceID: int, branch: str):
    return " ".join(_clickable(sentence, sentenceID, branch))