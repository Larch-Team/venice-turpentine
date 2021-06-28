from __future__ import annotations

import json
import logging
import os
import typing as tp

from anytree import node

import pop_engine as pop
from proof import BranchCentric, Proof
from sentence import Sentence
from tree import ProofNode
from close import Close
from usedrule import *
from exceptions import EngineError

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


def DealWithPOP(func):
    """A decorator which convert all PluginErrors to EngineErrors for simpler handling in the UI socket"""
    def new(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except pop.PluginError as e:
            raise EngineError(str(e))
    return new

# Input type handling

TYPE_LEXICON = {
    'sentenceID':int
}

def type_translator(type_):
    if isinstance(type_, str):
        return TYPE_LEXICON[type_]
    else:
        return type_

# Session


class Session(object):
    """
    Obekty sesji stanowią pojedyncze instancje działającego silnika.
    Wszystkie wyjątki określane jako `EngineError` mają wbudowany string w formie "dostępnej dla użytkownika"
    """
    ENGINE_VERSION = '0.0.1'
    SOCKETS = ('Application', 'Assistant', 'Formal', 'Lexicon', 'Output')
    SOCKETS_NOT_IN_CONFIG = ('Application')

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
        self.sockets = {name: pop.Socket(name, os.path.abspath(name), self.ENGINE_VERSION, '__template__.py',
                                         self.config['chosen_plugins'].get(name, None)) for name in self.SOCKETS}
        self.sockets["UserInterface"] = pop.DummySocket("UserInterface", os.path.abspath(
            "UserInterface"), self.ENGINE_VERSION, '__template__.py')

        self.defined = {}
        self.proof = None
        self.branch = ""


    def __repr__(self):
        return f"Session({self.id=})"


    # Plugin manpiulation


    def acc(self, socket: str) -> Module:
        """Zwraca plugin aktualnie podłączony do gniazda o podanej nazwie"""
        if (sock := self.sockets.get(socket, None)) is None:
            raise EngineError(f"There is no socket named {socket}")
        else:
            return sock()


    @EngineChangeLog
    def plug_switch(self, socket_or_old: str, new: str) -> None:
        """Podłącza plugin do gniazda

        :param socket_or_old: Nazwa aktualnie podłączonego pluginu, lub gniazda
        :type socket_or_old: str
        :param new: Nazwa nowego pluginu
        :type new: str
        :raises EngineError: Nie znaleziono pluginu
        """
        # Socket name searching
        socket = self.sockets.get(socket_or_old, None)
        if socket:
            socket_name = socket_or_old

        else:
            for i in self.config['chosen_plugins'].items():
                if i[1] == socket_or_old:
                    socket_name = i[0]
                    socket = self.sockets[socket_name]
        if not socket:
            raise EngineError(f"Socket/plugin {socket_or_old} not found in the program")
        # Plugging
        try:
            socket.plug(new)
        except (pop.PluginError, pop.LackOfFunctionsError, pop.FunctionInterfaceError, pop.VersionError) as e:
            raise EngineError(str(e))

        # Config editing
        if socket_name not in self.SOCKETS_NOT_IN_CONFIG:
            self.config['chosen_plugins'][socket_name] = new
        self.write_config()


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


    # Config reading and writing


    def read_config(self):
        logger.debug("Config loading")
        with open(f"config/{self.config_name}", 'r') as target:
            self.config = json.load(target)


    def write_config(self):
        logger.debug("Config writing")
        with open(f"config/{self.config_name}", 'w') as target:
            json.dump(self.config, target)


    # Proof manipulation


    @EngineLog
    @DealWithPOP
    def new_proof(self, statement: str) -> None:
        """Parsuje zdanie, testuje poprawność i tworzy z nim dowód

        :param statement: Zdanie
        :type statement: str

        :raises EngineError: Któryś z pluginów nie został podłączony
        :raises EngineError: Takie zdanie nie może istnieć
        """
        try:
            tokenized = self.acc('Lexicon').tokenize(
                statement, self.acc('Formal').get_used_types(), self.defined)
        except self.acc('Lexicon').utils.CompilerError as e:
            raise EngineError(str(e))
        tokenized = Sentence(tokenized, self)
        problem = self.acc('Formal').check_syntax(tokenized)
        if problem:
            logger.warning(f"{statement} is not a valid statement \n{problem}")
            raise EngineError(problem)
        else:
            tokenized = self.acc('Formal').prepare_for_proving(tokenized)
            
            self.proof = BranchCentric(tokenized, self.config)


    @EngineLog
    def reset_proof(self) -> None:
        self.proof = None


    @EngineLog
    @DealWithPOP
    def deal_closure(self, branch_name: str) -> tp.Union[None, str]:
        """Wywołuje proces sprawdzenia zamykalności gałęzi oraz (jeśli można) zamyka ją; Zwraca informacje o podjętych akcjach"""
        # Tests
        if not self.proof:
            raise EngineError("There is no proof started")
        
        # Branch checking
        closure, info = self.proof.deal_closure(self.acc('Formal'), branch_name)
        if closure:
            EngineLog(f"Closing {branch_name}: {str(closure)}, {info=}")
            return f"{branch_name}: {info}"
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
    @DealWithPOP
    def use_rule(self, rule: str, context: dict[str, tp.Any]) -> tp.Union[None, tuple[str]]:
        """Uses a rule of the given name on the current branch of the proof.
        Context allows to give the Formal additional arguments 
        Use `self.acc('Formal').get_needed_context(rule)` to check for needed context

        :param rule: Rule name (from `Formal` plugin)
        :type rule: str
        :param context: Arguments for rule usage
        :type context: dict[str, tp.Any]
        :return: Names of new branches
        :rtype: tp.Union[None, tuple[str]]
        """
        # Tests
        if not self.proof:
            raise EngineError(
                "There is no proof started")
        if rule not in self.acc('Formal').get_rules().keys():
            raise EngineError("No such rule")

        # Context checking
        context_info = self.acc('Formal').get_needed_context(rule)
        if {i.variable for i in context_info} != set(context.keys()):
            raise EngineError("Wrong context")

        return self.proof.use_rule(self.acc('Formal'), rule, context, None)


    @EngineLog
    def undo(self, actions_amount: int) -> tuple[str]:
        if not self.proof:
            raise EngineError(
                "There is no proof started")

        rules = [self.metadata['usedrules'].pop() for _ in range(actions_amount)]
        min_layer = min((r.layer for r in rules))
        self.proof.nodes.pop(min_layer)

        return rules


    # Proof navigation


    @DealWithPOP
    def getbranch_strings(self) -> list[list[str], str]:
        """Zwraca gałąź oraz stan zamknięcia w formie czytelnej dla użytkownika"""
        try:
            branch, closed = self.proof.get_node().getbranch_sentences()
        except KeyError:
            raise EngineError(
                f"Branch '{self.branch}' doesn't exist in this proof")
        except AttributeError:
            raise EngineError("There is no proof started")
        reader = lambda x: self.acc('Output').get_readable(x, self.acc('Lexicon').get_lexem)
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


    @DealWithPOP
    def getrules(self) -> dict[str, str]:
        """Zwraca nazwy reguł wraz z dokumentacją"""
        return self.acc('Formal').get_rules()


    @DealWithPOP
    def gettree(self) -> list[str]:
        """Zwraca całość drzewa jako listę ciągów znaków"""
        if not self.proof:
            raise EngineError(
                "There is no proof started")
        
        printed = self.proof.nodes.gettree()
        return self.acc('Output').write_tree(printed, self.acc('Lexicon').get_lexem)


    def next(self) -> None:
        """Przeskakuje do następnej otwartej gałęzi"""
        if not self.proof:
            raise EngineError("There is no proof started")
        return self.proof.next()
 

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
