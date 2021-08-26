"""
Tutaj umieść dokumentację swojego pluginu
"""
from typing import Any
from manager import FileManager
import plugins.UserInterface.__utils__ as utils
from flask import Flask, render_template, request
import webbrowser
from engine import Session
from exceptions import EngineError
from collections import namedtuple
from flask_local.libs import JSONResponse

SOCKET = 'UserInterface'
VERSION = '0.0.1'


app = Flask('flask_local', static_url_path='/static')
session = Session('main', 'config.json')

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/run', methods=['GET'])
def larch():
    return render_template('larch.html')

# API

@app.route('/API/new_proof', methods=['POST'])
def do_new_proof():
    sentence = request.form.get()
    if session.proof:
        return JSONResponse(type_='error', content="A proof would be deleted")
    try:
        text = session.new_proof(sentence)
    except EngineError as e:
        return JSONResponse(type_='error', content=str(e))
    else:
        if text:
            return JSONResponse(type_='error', content="\n".join(text))
        else:
            return JSONResponse('success')

def run() -> int:
    """
    Traktować to podobnie, jak `if __name__=="__main__"`. Funkcja uruchomiona powinna inicjalizować działające UI.
    Obiekt `main.Session` powinien być generowany dla każdego użytkownika. Wystarczy używać metod tego obiektu do interakcji z programem.

    :return: Exit code, -1 restartuje aplikację
    :rtype: int
    """
    webbrowser.open('http://127.0.0.1:5000', 2, autoraise=True)
    app.run(port='5000')
