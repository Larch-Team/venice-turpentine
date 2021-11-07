import webbrowser
from flask_local.app import app
from wsgiserver import WSGIServer

SOCKET = 'UserInterface'
VERSION = '0.0.1'


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
    http_server = WSGIServer(app, host='127.0.0.1', port=5000)
    http_server.start()
