from __future__ import annotations
from genericpath import isfile

import json
import logging
import os
import typing as tp
from manager import FileManager
from misc import setup_iter

import pop_engine as pop
from exceptions import EngineError, FileManagerError, PluginError, RaisedUserMistake
from proof import BranchCentric, Proof
from rule import ContextDef
from sentence import Sentence
from tree import ProofNode
from close import Close
import lexer
from usedrule import *

Module = pop.Module


# Logging config

logger = logging.getLogger('engine')


def EngineLog(func):
    def new(*args, **kwargs):
        logger.debug(
            f"{func.__name__} with args={str(args)} and kwargs={str(kwargs)}")
        return func(*args, **kwargs)
    return new


def EngineChangeLog(func):
    def new(*args, **kwargs):
        logger.info(
            f"{func.__name__} with args={str(args)} and kwargs={str(kwargs)}")
        return func(*args, **kwargs)
    return new

# Input type handling


TYPE_LEXICON = {
    'sentenceID': int,
    'tokenID': int
}


def contextdef_translate(contextdef: ContextDef):
    if isinstance(contextdef, str):
        return TYPE_LEXICON[contextdef]
    else:
        return contextdef

# Session


class Session(object):
    """
    Obekty sesji stanowią pojedyncze instancje działającego silnika.
    Wszystkie wyjątki określane jako `EngineError` mają wbudowany string w formie "dostępnej dla użytkownika"
    """
    ENGINE_VERSION = '0.0.1'
    SOCKETS = {'Assistant': '0.0.1',
               'Formal': '0.2.0',
               'Lexicon': '0.0.1',
               'Output': '0.0.1'}
    SOCKETS_NOT_IN_CONFIG = ()

    def __init__(self, session_ID: str, config_file: str):
        """Obekty sesji stanowią pojedyncze instancje działającego silnika.

        :param session_ID: ID sesji
        :type session_ID: str
        :param config_file: nazwa pliku config
        :type config_file: str
        """
        self.id = session_ID
        self.config_name = config_file
        self.read_config()
        self.sockets = {name: pop.Socket(name, os.path.abspath(f"plugins/{name}"), version, '__template__.py',
                                         self.config['chosen_plugins'].get(name, None)) for name, version in self.SOCKETS.items()}
        self.sockets["UserInterface"] = pop.DummySocket("UserInterface", os.path.abspath(
            f"plugins/UserInterface"), '0.0.1', '__template__.py')

        self.defined = {}
        self.proof = None
        self.branch = ""

        self.compile_lexer()

    def __repr__(self):
        return f"Session({self.id=})"

    # Plugin manpiulation

    def _find_socket(self, name: str) -> pop.Socket:
        socket = self.sockets.get(name, None)
        if socket:
            return socket

        for i in self.config['chosen_plugins'].items():
            if i[1] == name:
                socket_name = i[0]
                return self.sockets[socket_name]
        else:
            raise EngineError(f"Socket/plugin {name} not found in the program")

    def acc(self, socket: str) -> Module:
        """Zwraca plugin aktualnie podłączony do gniazda o podanej nazwie"""
        if (sock := self.sockets.get(socket, None)) is None:
            raise EngineError(f"There is no socket named {socket}")
        else:
            try:
                return sock()
            except PluginError as e:
                raise EngineError(str(e))

    @EngineChangeLog
    def plug_switch(self, socket_or_old: str, new: str) -> None:
        """Podłącza plugin do gniazda

        :param socket_or_old: Nazwa aktualnie podłączonego pluginu, lub gniazda
        :type socket_or_old: str
        :param new: Nazwa nowego pluginu
        :type new: str
        :raises EngineError: Nie znaleziono pluginu
        """
        socket = self._find_socket(socket_or_old)
        if socket.name in ('Formal', 'Lexicon') and self.proof:
            raise EngineError(
                f"Finish your proof before changing the {socket.name} plugin")

        # Plugging
        try:
            socket.plug(new)
        except (pop.PluginError, pop.LackOfFunctionsError, pop.FunctionInterfaceError, pop.VersionError) as e:
            raise EngineError(str(e))

        # Config editing
        if socket.name not in self.SOCKETS_NOT_IN_CONFIG:
            self.config['chosen_plugins'][socket.name] = new
        self.write_config()

        # Deal with lexer
        if socket.name == 'Lexicon':
            self.compile_lexer()

    def plug_list(self, socket: str) -> list[str]:
        """Zwraca listę wszystkich pluginów dla danej nazwy.

        :param socket: Socket name
        :type socket: str
        :raises EngineError: No socket with this name
        :rtype: list[str]
        """
        sock = self.sockets.get(socket, None)
        if sock is None:
            raise EngineError(f"There is no socket named {socket}")
        else:
            return sock.find_plugins()

    def plug_gen(self, socket: str, name: str) -> None:
        """Tworzy ze wzorca plik dla pluginu

        :param socket: Socket name
        :type socket: str
        :param name: Name of the new plugin
        :type name: str
        :raises EngineError: No socket with this name
        """
        sock = self.sockets.get(socket, None)
        if sock is None:
            raise EngineError(f"There is no socket named {socket}")
        else:
            sock.generate_template(name)

    def plug_download(self, socket_or_old: str, name: str, force: bool = False) -> tp.Iterator[str]:
        """Pobiera plugin

        :param socket_or_old: Nazwa aktualnie podłączonego pluginu, lub gniazda
        :type socket_or_old: str
        :param new: Nazwa pluginu
        :type new: str
        :param force: Czy wymusić pobieranie (pozwala na updatowanie pluginów), defaults to None
        :type force: bool
        """
        socket = self._find_socket(socket_or_old)
        try:
            yield from FileManager().download_plugin(socket.name, name, force)
        except FileManagerError as e:
            yield str(e)
            return

    def plug_search(self, socket_or_old: str = None) -> tp.Union[list[str], None, dict[str, list[str]]]:
        """
        Zwraca możliwe do zainstalowania pluginy

        :param socket_or_old: Nazwa socketu, lub pluginu do niego podłączonego, defaults to None
        :type socket_or_old: str, optional
        :return: Jeżeli podano socket_or_old, to zwraca listę dla danego pluginu, jeśli nie podano zwraca listę dla wszystkich socketów
        :rtype: tp.Union[list[str], None, dict[str, list[str]]]
        """
        if socket_or_old is None:
            for i in self.SOCKETS.keys():
                return {i: self.plug_search(i)}

        fm = FileManager()
        try:
            fm.get_files()
        except FileManagerError as e:
            raise EngineError(str(e))
        socket = self._find_socket(socket_or_old)
        plugins = fm.plugins.get(socket.name, None)
        installed = socket.find_plugins()
        return None if plugins is None else [i for i in plugins if i not in installed]

    # Setups

    def setup_save(self, name: str) -> None:
        """Zapisuje setup pod wskazaną nazwą"""
        p = f'setups/{name}.json'
        if isfile(p):
            raise EngineError("This setup already exists")
        with open(p, 'w') as f:
            json.dump(self.config['chosen_plugins'], f)

    def setup_delete(self, name: str) -> None:
        """Usuwa setup o podanej nazwie, jeśli nie znajdzie uruchamia wyjątek EngineError"""
        p = f'setups/{name}.json'
        if not isfile(p):
            raise EngineError("This setup doesn't exists")
        os.remove(p)

    def setup_list(self) -> list[str]:
        """Wyświetla listę zainstalowanych setupów"""
        return FileManager.setup_list()


    def setup_search(self) -> list[str]:
        """Zwraca możliwe do zainstalowania setupy"""
        fm = FileManager()
        try:
            return fm.setup_search()
        except FileManagerError as e:
            raise EngineError(str(e))

    def setup_open(self, name: str, force: bool = False) -> tp.Iterable[str]:
        """
        Uruchamia setup o podanej nazwie, w razie potrzeby go pobiera

        :param name: Nazwa setupu
        :type name: str
        :param force: Czy wymusić pobieranie (pozwala na aktualizowanie setupów), defaults to False
        :type force: bool, optional
        :raises EngineError: Błędy pobierania
        :yield: Informacje o statusie pobierania
        :rtype: Iterable[str]
        """
        p = f'setups/{name}.json'
        try:
            yield from FileManager().download_setup_plugins(name, force)
        except FileManagerError as e:
            raise EngineError(str(e))
        yield "Activating the setup"
        for socket, plugin in setup_iter(p):
            yield f"\tPlugging {plugin} into {socket} socket"
            try:
                self.plug_switch(socket, plugin)
            except EngineError as e:
                yield "\t\t"+str(e)

    # Lexer

    def compile_lexer(self) -> None:
        """
        Kompiluje lexer na bazie pluginu Lexiconu
        Raczej zbędne poza zastosowaniami technicznymi
        """
        self.lexer = lexer.BuiltLexer(self.acc('Lexicon').get_lexicon(),
                                      use_language=self.acc(
                                          'Formal').get_tags()
                                      )

    # Config reading and writing

    def change_accessibility(self, level: int):
        self.config['accessibility'] = level
        self.write_config()

    def read_config(self):
        logger.debug("Config loading")
        if not os.path.isfile(f"config/{self.config_name}"):
            with open(f"config/{self.config_name}", 'w') as target:
                target.write(
                    r'{"chosen_plugins": {"Assistant": "pan","UserInterface": "CLI","Lexicon": "classic","Formal": "analytic_freedom","Output":"actual_tree"}}')
        with open(f"config/{self.config_name}", 'r') as target:
            self.config = json.load(target)

    def write_config(self):
        logger.debug("Config writing")
        with open(f"config/{self.config_name}", 'w') as target:
            json.dump(self.config, target)

    # Proof manipulation

    @EngineLog
    def new_proof(self, statement: str) -> tp.Union[None, list[str]]:
        """Parsuje zdanie, testuje poprawność i tworzy z nim dowód

        :param statement: Zdanie
        :type statement: str

        :raises EngineError: Któryś z pluginów nie został podłączony
        :raises EngineError: Takie zdanie nie może istnieć
        """
        try:
            tokenized = self.lexer.tokenize(statement)
        except lexer.LrchLexerError as e:
            raise [EngineError(str(e))]
        tokenized = Sentence(tokenized, self)
        problem = self.acc('Formal').check_syntax(tokenized)
        if problem:
            logger.warning(
                f"{statement} is not a valid statement \n{problem.name}")
            return self.acc('Assistant').mistake_syntax(problem)
        else:
            tokenized = self.acc('Formal').prepare_for_proving(tokenized)

            self.proof = BranchCentric(tokenized, self.config)
            self.deal_closure(self.proof.nodes.getbranchnames()[0])

    @EngineLog
    def reset_proof(self) -> None:
        self.proof = None

    @EngineLog
    def deal_closure(self, branch_name: str) -> tp.Union[None, str]:
        """Wywołuje proces sprawdzenia zamykalności gałęzi oraz (jeśli można) zamyka ją; Zwraca informacje o podjętych akcjach"""
        # Tests
        if not self.proof:
            raise EngineError("There is no proof started")

        # Branch checking
        closure, info = self.proof.deal_closure(
            self.acc('Formal'), branch_name)
        if closure:
            EngineLog(f"Closing {branch_name}: {str(closure)}, {info=}")
            return info
        else:
            return None

    def context_info(self, rule: str):
        """
        Zwraca kontekst wymagany dla reguły w postaci obiektów ContextDef

        ContextDef:
        variable    - Nazwa do przywołań, używana podczas dostarczania kontekstu w `use_rule`
        official    - Nazwa do wyświetlania użytkownikowi
        docs        - Dokumentacja dla zmiennej wyświetlalna dla użytkownika
        type_       - Typ zmiennej, albo jest to dosłownie typ, albo string wyrażony w `TYPE_LEXICON`
        """
        return self.acc('Formal').get_needed_context(rule)

    @EngineLog
    def use_rule(self, rule: str, context: dict[str, tp.Any]) -> tp.Union[None, list[str]]:
        """Uses a rule of the given name on the current branch of the proof.
        Context allows to give the Formal additional arguments 
        Use `self.acc('Formal').get_needed_context(rule)` to check for needed context

        :param rule: Rule name (from `Formal` plugin)
        :type rule: str
        :param context: Arguments for rule usage
        :type context: dict[str, tp.Any]
        :return: Readable information about the proof state, None if everything's good
        :rtype: tp.Union[None, list[str]]
        """
        # Tests
        if not self.proof:
            raise EngineError(
                "There is no proof started")
        if rule not in self.acc('Formal').get_rules_docs().keys():
            raise EngineError("No such rule")

        # Context checking
        context_info = self.acc('Formal').get_needed_context(rule)
        if {i.variable for i in context_info} != set(context.keys()):
            raise EngineError("Wrong context")

        try:
            self.proof.use_rule(rule, context, None)
        except RaisedUserMistake as e:
            if self.sockets['Assistant'].isplugged():
                return self.acc('Assistant').mistake_userule(e) or [e.default]
            else:
                return [e.default]
        return None

    @EngineLog
    def undo(self, actions_amount: int) -> tuple[str]:
        """Wycofuje `actions_amount` operacji zwracając informacje o nich"""
        if not self.proof:
            raise EngineError(
                "There is no proof started")
        if len(self.proof.metadata['usedrules']) < actions_amount:
            raise EngineError("Nothing to undo")

        rules = [self.proof.metadata['usedrules'].pop()
                 for _ in range(actions_amount)]
        min_layer = min((r.layer for r in rules))
        self.proof.nodes.pop(min_layer)

        # Poprawianie gałęzi
        if self.proof.metadata['usedrules']:
            self.proof.branch = self.proof.metadata['usedrules'][-1].branch
        else:
            self.proof.branch = self.proof.nodes.branch

        return rules

    # Proof assist

    def start_help(self) -> list[str]:
        """Zwraca listę podpowiedzi do wyświetlenia użytkownikowi"""
        return self.acc('Assistant').hint_start() or []

    @EngineLog
    def hint(self) -> list[str]:
        """Zwraca listę podpowiedzi w formacie HTML"""
        if not self.proof:
            raise EngineError(
                "There is no proof started")

        return self.acc('Assistant').hint_command(self.proof)

    @EngineLog
    def check(self, proof: Proof = None) -> list[str]:
        """Sprawdza dowód i zwraca listę błędów w formacie HTML"""
        proof = proof or self.proof
        if not proof:
            raise EngineError("There is no proof started")
        if not proof.nodes.is_closed():
            raise EngineError("Nie możesz sprawdzić nieskończonego dowodu")

        mistakes = proof.check()
        l = []
        for i in mistakes:
            if v := self.acc('Assistant').mistake_check(i) is not None:
                l.extend(v)
            else:
                l.append(i.default)
        return l

    @EngineLog
    def solve(self, proof: Proof = None) -> tuple[str]:
        """Dokańcza podany, lub aktualny dowód, zwraca informację o sukcesie procedury"""
        proof = proof or self.proof
        if not proof:
            raise EngineError(
                "There is no proof started")

        if self.acc('Formal').solver(proof):
            return ("Udało się zakończyć dowód", f"Formuła {'nie '*(not proof.nodes.is_successful())}jest tautologią")
        else:
            return ("Nie udało się zakończyć dowodu",)

    # Proof navigation

    def getbranch_strings(self) -> tuple[list[str], tp.Optional[str]]:
        """Zwraca gałąź oraz stan zamknięcia w formie czytelnej dla użytkownika"""
        try:
            branch, closed = self.proof.get_node().getbranch_sentences()
        except KeyError:
            raise EngineError(
                f"Branch '{self.branch}' doesn't exist in this proof")
        except AttributeError as e:
            raise EngineError("There is no proof started")

        def reader(x): return self.acc('Output').get_readable(x)
        if closed:
            return [reader(i) for i in branch], str(closed)
        else:
            return [reader(i) for i in branch], None

    def getbranches(self):
        """Zwraca wszystkie *nazwy* gałęzi"""
        if not self.proof:
            raise EngineError(
                "There is no proof started")

        return self.proof.nodes.getbranchnames()

    def getrules(self) -> dict[str, str]:
        """Zwraca nazwy reguł wraz z dokumentacją"""
        return self.acc('Formal').get_rules_docs()

    def gettree(self) -> list[str]:
        """Zwraca całość drzewa jako listę ciągów znaków"""
        if not self.proof:
            raise EngineError(
                "There is no proof started")

        printed = self.proof.nodes.gettree()
        return self.acc('Output').write_tree(printed)

    @EngineLog
    def next(self) -> None:
        """Przeskakuje do następnej otwartej gałęzi"""
        if not self.proof:
            raise EngineError("There is no proof started")
        return self.proof.next()

    @EngineLog
    def jump(self, new: str) -> None:
        """Skacze do gałęzi o nazwie new, albo na prawego/lewego sąsiadu, jeżeli podamy "left/right"

        :param new: Target branch
        :type new: str
        """
        if not self.proof:
            raise EngineError("There is no proof started")
        return self.proof.jump(new)

    def proof_finished(self) -> tuple[bool, bool]:
        """Zwraca informację o zamknięciu wszystkich gałęzi oraz o ich zamknięciu ze względu na zakończenie dowodzenia w nich"""
        if not self.proof:
            raise EngineError("There is no proof started")
        return self.proof.nodes.is_closed(), self.proof.nodes.is_successful()

    def get_current_branch(self) -> str:
        return self.proof.branch if self.proof else ""

    # Misc

    def get_socket_names(self):
        return self.SOCKETS

    def get_methods(self) -> list[str]:
        return [i for i in dir(self) if callable(getattr(self, i)) and not i.startswith('__')]

# Misc
