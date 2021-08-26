"""
Tutaj umieść dokumentację swojego pluginu
"""
from manager import FileManager
import plugins.UserInterface.__utils__ as utils
from flask import Flask, render_template
import webbrowser

SOCKET = 'UserInterface'
VERSION = '0.0.1'

def path(x:str):
    return utils.get_plugin_path(__file__, x)

app = Flask('flask-local', static_url_path='/static')

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/run', methods=['GET'])
def larch():
    return render_template('larch.html')

def run() -> int:
    """
    Traktować to podobnie, jak `if __name__=="__main__"`. Funkcja uruchomiona powinna inicjalizować działające UI.
    Obiekt `main.Session` powinien być generowany dla każdego użytkownika. Wystarczy używać metod tego obiektu do interakcji z programem.

    :return: Exit code, -1 restartuje aplikację
    :rtype: int
    """
    webbrowser.open('http://127.0.0.1:5000', 2, autoraise=True)
    app.run(port='5000')
