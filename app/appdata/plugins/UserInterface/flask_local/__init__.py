"""
Tutaj umieść dokumentację swojego pluginu
"""
import enum
from typing import Any
from close import Contradiction
from manager import FileManager
import plugins.UserInterface.__utils__ as utils
from flask import Flask, render_template, request
import webbrowser
from engine import Session, contextdef_translate
from exceptions import EngineError
from collections import namedtuple
from flask_local.libs import JSONResponse, get_clickable, symbol_HTML, get_tree_clickable, get_preview
from plugins.UserInterface.flask_local.libs import get_tree_contra
from proof import Proof

SOCKET = 'UserInterface'
VERSION = '0.0.1'


app = Flask('flask_local', static_url_path='/static')
session = Session('main', 'config.json')
# TODO: dodać po skończeniu setup update


@app.route('/', methods=['GET'])
def index():
    session.reset_proof()
    return render_template('index.html')


@app.route('/run', methods=['GET'])
def larch():
    return render_template('larch.html', hint_start="<div>"+"</div><div>".join(session.start_help())+"</div>")

# API


@app.route('/API/new_proof', methods=['POST'])
def do_new_proof():
    sentence = request.data.decode()
    if session.proof:
        return JSONResponse(type_='error', content="A proof would be deleted")
    try:
        text = session.new_proof(sentence)
    except EngineError as e:
        print(str(e))
        return JSONResponse(type_='error', content=str(e))
    else:
        if text:
            print("error")
            return JSONResponse(type_='error', content="\n".join(text))
        else:
            print("New proof")
            return JSONResponse('success')


@app.route('/API/use_rule', methods=['POST'])
def do_use_rule():
    rule = request.json['rule']
    branch_name = request.json['branch']
    context = request.json['context']

    # Check context
    context_info = session.context_info(rule)
    prepared = {}
    if context_info is None:
        return JSONResponse(type_='error', content="No such rule")
    for variable, official, _, type_ in context_info:
        if variable not in context:
            return JSONResponse(type_='error', content=f"{official} is not provided to the rule")

        vartype = contextdef_translate(type_)
        try:
            new = vartype(context[variable])
        except ValueError:
            return JSONResponse(type_='error', content=f"{official} is of a wrong type")

        prepared[variable] = new

    # Run use_rule
    try:
        session.jump(branch_name)
        text = session.use_rule(rule, prepared)
    except EngineError as e:
        print(str(e))
        return JSONResponse(type_='error', content=str(e))
    else:
        if text:
            print("error")
            return JSONResponse(type_='error', content="\n".join(text))
        else:
            print(f"rule used {rule=} {branch_name=}")
            return JSONResponse('success')


@app.route('/API/hint/wanted', methods=['GET'])
def do_hint() -> str:
    """Gives you a hint"""
    try:
        hints = session.hint()
    except EngineError as e:
        return JSONResponse(type_='error', content=str(e))
    if hints is not None:
        return JSONResponse(type_='success', content=hints)
    else:
        return JSONResponse(type_='error', content="Podpowiedzi nie ma, trzymaj się tam")


@app.route('/API/worktree', methods=['GET'])
def do_get_worktree():
    if not session.proof:
        return "no proof"

    try:
        return get_tree_clickable(session.proof.nodes)
    except EngineError as e:
        return f'<code>{e}</code>'
    
@app.route('/API/contratree', methods=['GET'])
def do_get_contratree():
    if not session.proof:
        return "no proof"

    try:
        return get_tree_contra(session.proof.nodes)
    except EngineError as e:
        return f'<code>{e}</code>'


@app.route('/API/branch', methods=['GET'])
def do_get_branch():
    branch = request.args.get('branch', default=None, type=str)
    if not session.proof:
        return "no proof"

    try:
        session.jump(branch)
        return " ".join(
            f'<button class="branch-btn" id="btn{i}" onclick="forCheckBranch(\'{branch}\', {i});">{sen}</button>'
            for i, sen in enumerate(session.getbranch_strings()[0])
        )

    except EngineError as e:
        return f'<code>{e}</code>'


@app.route('/API/preview', methods=['POST'])
def do_preview():
    rule = request.json['rule']
    branch_name = request.json['branch']
    context = request.json['context']
    ret = session.proof.preview(branch_name, rule, context)
    return get_preview(ret)


@app.route('/API/rules', methods=['GET'])
def do_get_rules():
    tokenID = request.args.get('tokenID', default=None, type=int)
    sentenceID = request.args.get('sentenceID', default=None, type=int)
    branch = request.args.get('branch', default=None, type=str)

    docs = session.getrules()
    if session.sockets['Formal'].plugin_name == 'analytic_freedom' and session.proof is not None and branch is not None and sentenceID is not None and tokenID is not None:
        b, _ = session.proof.nodes.getleaf(branch).getbranch_sentences()
        token = b[sentenceID].getTypes()[tokenID]
        docs = {i: j for i, j in docs.items() if i.endswith(token)}

    rules = session.getrulessymbol()
    return "".join(symbol_HTML(key, rules[key], branch, tokenID, sentenceID, docs[key]) for key in docs)


@app.route('/API/undo', methods=['POST'])
def do_undo() -> str:
    """Undos last action"""
    try:
        rules = session.undo(1)
        return JSONResponse(type_='success')
    except EngineError as e:
        return JSONResponse(type_='error', content=str(e))


@app.route('/API/contra', methods=['POST'])
def do_contra() -> str:
    """Check contradiction"""
    branch_name = request.json['branch']
    sID1 = request.json['sentenceID1']
    sID2 = request.json['sentenceID2']
    try:
        branch, closed = session.proof.nodes.getleaf(
            branch_name).getbranch_sentences()
        if closed:
            return JSONResponse(type_='error', content="Branch already closed")
        elif (branch[sID1].getNonNegated() == branch[sID2].getNonNegated() and
              (len(branch[sID1].reduceBrackets()) - len(branch[sID2].reduceBrackets())) % 2 == 1):
            session.proof.nodes.getleaf(branch_name).close(Contradiction(sentenceID1 = sID1+1, sentenceID2 = sID2+1))
            return JSONResponse(type_='success')
        else:
            return JSONResponse(type_='error', content="Branch couldn't be closed")
    except EngineError as e:
        return JSONResponse(type_='error', content=str(e))


@app.route('/API/finish', methods=['POST'])
def do_finish() -> str:  # sourcery skip: merge-else-if-into-elif
    try:
        is_tautology = request.json['tautology']
        problems = session.check()
        
        # Check proof
        if problems:
            return JSONResponse(type_='success', content='wrong rule')

        test_proof = session.proof.copy()
        closed_branches = [i.branch for i in session.proof.nodes.getopen()]
        
        # Check branch closure
        for i in test_proof.nodes.getopen():
            test_proof.deal_closure(i.branch)
            if i.closed and i.closed.success and i.branch not in closed_branches:
                return JSONResponse(type_='success', content='not all closed')

        # Check decision
        test_proof.solve()
        if is_tautology:
            if session.proof.nodes.is_successful():
                # Zaznaczono tautologię i poprawny dowód to wykazuje
                return JSONResponse(type_='success', content='correct')
            elif test_proof.nodes.is_successful():
                # Zaznaczono tautologię, ale z dowodu to nie wynika, gdyż nie został dokończony
                return JSONResponse(type_='success', content='not finished')
            else:
                # Zaznaczono tautologię, gdy nie jest to tautologia i dowód to wykazuje
                return JSONResponse(type_='success', content='wrong decision')
        else:
            if session.proof.nodes.is_successful():
                # Zaznaczono nie-tautologię, gdy jest to tautologia i dowód to wykazuje
                return JSONResponse(type_='success', content='wrong decision')
            elif test_proof.nodes.is_successful():
                # Zaznaczono nie-tautologię, ale formuła jest tautologią, ale dowód nie został dokończony
                return JSONResponse(type_='success', content='not finished')
            else:
                # Zaznaczono nie-tautologię i poprawny dowód to wykazuje
                return JSONResponse(type_='success', content='correct')
        
    except EngineError as e:
        return JSONResponse(type_='error', content=str(e))


#
# TEMPLATE
#

def run() -> int:
    """
    Traktować to podobnie, jak `if __name__=="__main__"`. Funkcja uruchomiona powinna inicjalizować działające UI.
    Obiekt `main.Session` powinien być generowany dla każdego użytkownika. Wystarczy używać metod tego obiektu do interakcji z programem.

    :return: Exit code, -1 restartuje aplikację
    :rtype: int
    """
    webbrowser.open('http://127.0.0.1:5000', 2, autoraise=True)
    app.run(port='5000')
