
from typing import Any, Iterator
from string import Template

from sentence import Sentence
from tree import ProofNode, SentenceTupleStructure

def JSONResponse(type_: str, content: Any = None):
    return {'type':type_, 'content': content} if content is not None else {'type':type_}

def symbol_HTML(rule: str, symbolic: str, branch: str, tID: int, sID: int, tooltip: str):
    symbolic = symbolic.replace(";", "<br>").replace("|", "</div> <div>")
    premiss, result = symbolic.split(" / ")
    return f'''<button type="button" onclick="use_rule('{rule}', '{branch}', {tID}, {sID})" title="{tooltip}">
    <div class="symbolic"><div>{premiss}</div></div>
    <hr>
    <div class="symbolic"><div>{result}</div></div></button>'''
    

# TODO: uzupełnić tag
Tag = Template('<button type="button" onclick="getRules(\'$branch\', $tID, $sID)">$symbol</button>')

def _clickable(sentence: Sentence, sentenceID: int, branch: str) -> Iterator[str]:
    for tID, symbol in enumerate(sentence.getReadableList()):
        yield Tag.substitute(tID=tID, sID=sentenceID, branch=branch, symbol=symbol)

def get_clickable(sentence: Sentence, sentenceID: int, branch: str):
    return " ".join(_clickable(sentence, sentenceID, branch))

def get_tree(node: ProofNode):
    table = [get_clickable(node.sentence, len(node.ancestors), node.branch)]
    if node.children:
        table.append('<div class="symbolic2">') # symbolic to zły wybór, ale ma potencjał!!!!
        for child in node.children:
            table.append(''.join(['<div>', get_tree(child), '</div>']))
        table.append('</div>')
    return "".join(table)

def get_preview(render: SentenceTupleStructure):
    max_len = max(len(i) for i in render)
    render = (i+("")*(max_len(len(i))) for i in render)
    table = []
    for row in zip(*render):
        table += ['<tr>', *["<td>"+i.getReadable()+"</td>" for i in row], '</tr>']
    return f"<table> {''.join(table)} </table>"
