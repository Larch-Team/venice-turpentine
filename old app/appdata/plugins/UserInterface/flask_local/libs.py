
from typing import Any, Iterator
from string import Template

from sentence import Sentence
from tree import ProofNode, SentenceTupleStructure


def JSONResponse(type_: str, content: Any = None):
    return {'type': type_, 'content': content} if content is not None else {'type': type_}


def symbol_HTML(rule: str, symbolic: str, tID: int, sID: int, tooltip: str):
    symbolic = symbolic.replace(";", "<br>").replace("|", "</div> <div>")
    premiss, result = symbolic.split(" / ")
    return f'''<button type="button" onclick="use_rule('{rule}', {tID}, {sID})" title="{tooltip}">
    <div class="symbolic"><div>{premiss}</div></div>
    <hr>
    <div class="symbolic"><div>{result}</div></div></button>'''


Tag = Template('<button type="button" class="$branch tree-btn" id="btn$sID$tID$branch" onclick="getRules($tID, $sID, \'$branch\')">$symbol</button>')


def _clickable(sentence: Sentence, sentenceID: int, branches: list[str], add) -> Iterator[str]:
    for tID, symbol in enumerate(sentence.getReadableList()):
        yield Tag.substitute(tID=tID, sID=sentenceID, branch=" ".join(branches)+add, symbol=symbol)


def get_clickable(sentence: Sentence, sentenceID: int, branch: str, add=''):
    return " ".join(_clickable(sentence, sentenceID, branch, add))


def getused(node: ProofNode):
    return {f' used-{i.branch.lower()}' for i in node.leaves if node.sentence in i.history}


def get_tree_clickable(node: ProofNode):
    if node.children:
        table = [
            get_clickable(
                node.sentence,
                len(node.ancestors),
                {i.branch.lower() for i in node.leaves},
                add="".join(getused(node))
            ),
            '<div class="symbolic2">',
        ]
        for child in node.children:
            table.append(
                ''.join(['<div>', get_tree_clickable(child), '</div>']))
        table.append('</div>')
    else:
        table = [get_clickable(node.sentence, len(node.ancestors), {
                               node.branch}, add=f' leaf-{node.branch} leaf')]
    return "".join(table)


def get_tree_contra(node: ProofNode):
    if node.children:
        table = [" ".join(node.sentence.getReadableList()),
                 '<div class="symbolic2">']
        for child in node.children:
            table.append(''.join(['<div>', get_tree_contra(child), '</div>']))
        table.append('</div>')
    elif node.closed:
        if node.closed.success:
            table = ['<button type="button" onclick="getBranch(\'', node.branch, '\');">',
                 " ".join(node.sentence.getReadableList()),
                 '</button>',
                 '<br><div class="branch_close">&#10060;</div>']
        else:
            table = ['<button type="button" onclick="getBranch(\'', node.branch, '\');">',
                 " ".join(node.sentence.getReadableList()),
                 '</button>',
                 '<br><div class="branch_close">&#11093;</div>']
    else:
        table = ['<button type="button" onclick="getBranch(\'', node.branch, '\');">',
                 " ".join(node.sentence.getReadableList()),
                 '</button>']
    return "".join(table)


def get_preview(render: SentenceTupleStructure):
    max_len = max(len(i) for i in render)
    render = (i+("")*(max_len(len(i))) for i in render)
    table = []
    for row in zip(*render):
        table += ['<tr>', *["<td>"+i.getReadable()+"</td>" for i in row], '</tr>']
    return f"<table> {''.join(table)} </table>"
