"""
Tutaj umieść dokumentację swojego pluginu
"""
from typing import Any
from manager import FileManager
import plugins.UserInterface.__utils__ as utils
from flask import Flask, render_template, request
import webbrowser
from engine import Session, contextdef_translate
from exceptions import EngineError
from collections import namedtuple
from flask_local.libs import JSONResponse, get_clickable

SOCKET = 'UserInterface'
VERSION = '0.0.1'


app = Flask('flask_local', static_url_path='/static')
session = Session('main', 'config.json')
#TODO: dodać po skończeniu setup update

@app.route('/', methods=['GET'])
def index():
    session.reset_proof()
    return render_template('index.html')

@app.route('/run', methods=['GET'])
def larch():
    return render_template('larch.html')

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
        if not context.get(variable):
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
        
@app.route('/API/hint', methods=['GET'])       
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
    return get_clickable(session.proof.nodes.sentence, 0, session.proof.nodes.branch)

@app.route('/API/table', methods=['GET'])
def do_get_table():
    node = session.proof.nodes
    html = ['<style> table, th, td {border: 1px solid black; border-collapse: collapse;} </style>','<table>','<tr><th>Proof</th></tr>','</table']
    # for layer in layers:


@app.route('/API/rules', methods=['GET'])
def do_get_rules():
    return session.getrules()

@app.route('/API/undo', methods=['POST'])
def do_undo() -> str:
    """Undos last action"""
    try:
        rules = session.undo(1)
        return JSONResponse(type_='success')
    except EngineError as e:
        return JSONResponse(type_='error', content=str(e))

def run() -> int:
    """
    Traktować to podobnie, jak `if __name__=="__main__"`. Funkcja uruchomiona powinna inicjalizować działające UI.
    Obiekt `main.Session` powinien być generowany dla każdego użytkownika. Wystarczy używać metod tego obiektu do interakcji z programem.

    :return: Exit code, -1 restartuje aplikację
    :rtype: int
    """
    webbrowser.open('http://127.0.0.1:5000', 2, autoraise=True)
    app.run(port='5000')
