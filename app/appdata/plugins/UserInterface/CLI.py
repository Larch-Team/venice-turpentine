"""
Najbardziej podstawowy interfejs do programu Larch. wykorzystuje paczkę `prompt_toolkit`.
"""
import json
import logging
import os
import sys
import typing as tp
from collections import OrderedDict, namedtuple
from math import log10
from xml.sax.saxutils import escape
from colors import COLORS, DEFAULT_COLOR
import engine
import prompt_toolkit as ptk

from exceptions import EngineError

SOCKET = 'UserInterface'
VERSION = '0.0.1'

# Logging config

logging.basicConfig(filename='log.log', level=logging.DEBUG,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
logger = logging.getLogger('interface')


def UIlogged(func):
    def new(*args, **kwargs):
        logger.debug(
            f"{func.__name__} with args={str(args)} and kwargs={str(kwargs)}")
        return func(*args, **kwargs)
    return new


# Command parsing execution

class ParsingError(Exception):
    pass


Command = namedtuple('Command', ('func', 'args', 'docs'))


def parser(statement: str, commands: dict) -> list[Command]:
    """Przetwarza komendę do obiektów Command z oddzielonymi funkcjami i argumentami, lub dokumentacją. 

    :param statement: Komenda/grupa komend
    :type statement: str
    :param commands: [description]
    :type commands: dict
    :raises ParsingError: Błąd w parsowaniu, patrz opis
    :return: Lista namedtuples (patrz wyżej)
    :rtype: list[Command]
    """
    comm = []
    for command_raw in statement.split('/'):
        # Function parsing
        command = command_raw.strip()
        func = None
        for comm_, f in commands.items():
            if command.startswith(comm_):
                name, func = comm_, f
                break
        if not func:
            raise ParsingError("Command not found")
        args = command[len(name):].split()

        # Invoking the help command
        if '?' in args or '--help' in args or 'help' in args:
            doc = func['comm'].__doc__ or "Help not found"
            comm.append(Command(func['comm'], None, doc))
            continue

        # Argument conversion
        if func['args'] == 'multiple_strings':
            converted = parse_multiple_string(command, name)
        else:
            converted = parse_args(func, args)

        comm.append(Command(func['comm'], converted, None))
    return comm


def parse_multiple_string(command, name):
    converted = command[len(name):].strip()
    if len(converted) == 0:
        raise ParsingError("More arguments needed")
    return converted


def parse_args(func, args):
    if len(args) > len(func['args']):
        raise ParsingError("Too many arguments")
    elif len(args) < len(func['args']):
        raise ParsingError("More arguments needed")
    converted = []
    for form, val in zip(func['args'], args):
        try:
            new = form(val)
        except ValueError:
            raise TypeError("Wrong argument type")
        converted.append(new)
    return converted


@UIlogged
def performer(command: Command, session: engine.Session) -> tp.Union[str, tp.Iterator[str]]:
    """Wykonuje funkcję na obiekcie sesji"""
    if command.docs:
        return command.docs
    if isinstance(command.args, str):
        return command.func(session, command.args)
    else:
        return command.func(session, *command.args)


# Commands

def do_clear(session) -> str:
    """Clears the screen, useful when dealing with graphical bugs"""
    ptk.shortcuts.clear()
    return ""


def do_exit(session: engine.Session):
    """Exits the app"""
    logger.info("Exiting the app")
    sys.exit(0)


# Plugin manipulation


def do_plug_switch(session: engine.Session, socket_or_name: str, new: str) -> str:
    """Allows to plug in a plugin to a socket

    Arguments:
        - Socket/Old plugin name [str]
        - New plugin's name [str]
    """
    try:
        session.plug_switch(socket_or_name, new)
    except BaseException as e:  # Not sure if this should be rewritten
        logger.error(f"Exception caught: {e}")
        return str(e)
    else:
        return f"Plugin succesfully installed: {new}"


def do_plug_list(session: engine.Session, socket: str) -> str:
    """Lists all the plugins that can be connected to a socket

    Arguments:
        - Socket name [str]
    """
    try:
        plugins = "; ".join(session.plug_list(socket))
    except engine.EngineError as e:
        return str(e)
    else:
        return f"Plugins available locally for {socket}:\n{plugins}"


def do_plug_list_all(session: engine.Session) -> str:
    """Lists all the plugins that can be connected to all of the Sockets"""
    strings = []
    for i in session.get_socket_names():
        plugins = "; ".join(session.plug_list(i))
        strings.append(f"Plugins available locally for {i}:\n{plugins}")
    return "\n\n".join(strings)


def do_plug_gen(session: engine.Session, socket: str, name: str) -> str:
    """Generates an empty plugin

    Arguments:
        - Socket name [str]
        - Plugin name [str]
    """
    try:
        session.plug_gen(socket, name)
    except engine.EngineError as e:
        logger.error(e)
        return e
    else:
        return f"Generated plugin {name} from template"
    
    
def do_plug_get(session: engine.Session, socket_or_name: str, new: str) -> tp.Iterator[str]:
    """Downloads a plugin from the <code>Larch-Team/larch-plugins</code> repository 

    Arguments:
        - Socket/current plugin name [str]
        - Plugin name [str]
    """
    try:
        yield from session.plug_download(socket_or_name, new)
    except engine.EngineError as e:
        logger.error(e)
        yield str(e)
    else:
        yield f"Plugin succesfully downloaded: {new}"
        
def do_plug_update(session: engine.Session, socket_or_name: str, new: str) -> tp.Iterator[str]:
    """Updates a plugin using the <code>Larch-Team/larch-plugins</code> repository 

    Arguments:
        - Socket/current plugin name [str]
        - Plugin name [str]
    """
    try:
        yield from session.plug_download(socket_or_name, new, True)
    except engine.EngineError as e:
        logger.error(e)
        yield str(e)
    else:
        yield f"Plugin succesfully downloaded: {new}"


# Setups


def do_setup_save(session: engine.Session, name: str) -> str:
    """Saves a setup

    Arguments:
        - Setup name [str]    
    """
    try:
        session.setup_save(name)
    except EngineError as e:
        return str(e)
    else:
        return "The setup was saved"
    
def do_setup_delete(session: engine.Session, name: str) -> str:
    """Deletes a setup

    Arguments:
        - Setup name [str]    
    """
    try:
        session.setup_delete(name)
    except EngineError as e:
        return str(e)
    else:
        return "The setup was deleted"
    
    
def do_setup_open(session: engine.Session, name: str) -> tp.Iterator[str]:
    """Initiates a given setup

    Arguments:
        - Setup name [str]    
    """
    try:
        yield from session.setup_open(name)
    except EngineError as e:
        yield str(e)
        return
    else:
        yield f"You are now using {name}"
        

def do_setup_update(session: engine.Session, name: str) -> tp.Iterator[str]:
    """Updates a given setup and initiates it

    Arguments:
        - Setup name [str]    
    """
    try:
        yield from session.setup_open(name, True)
    except EngineError as e:
        yield str(e)
        return
    else:
        yield f"You are now using {name}"
    

def do_setup_list(session: engine.Session) -> str:
    """Lists all local setups"""
    try:
        return session.setup_list()
    except EngineError as e:
        return str(e)
    

# Proof manipulation


def do_prove(session: engine.Session, sentence: str) -> str:
    """Initiates a new proof

    Arguments:
        - Sentence to prove [str]
    """
    if session.proof:
        return "A proof would be deleted"
    try:
        text = session.new_proof(sentence)
    except engine.EngineError as e:
        return str(e)
    else:
        if text:
            return "\n".join(text)
        else:
            return "Sentence tokenized successfully \nProof initialized"


def do_use(session: engine.Session, command) -> str:
    """Uses a rule in the proof

    Arguments:
        - Rule name [str]
        - Depends on rule context
    """
    if len(command) < 2:
        return "Full rule name needed"

    comm_split = command.split()
    name = " ".join(comm_split[:2])
    out = []

    # Context compiling
    context = {}
    c_values = comm_split[2:]
    context_info = session.context_info(name)
    if context_info is None:
        return "No such rule"
    if len(c_values)>len(context_info):
        out.append("Too many args, but the program will continue")
    
    for i, c in enumerate(context_info):
        if i == len(c_values):
            return "More arguments needed: {}".format(", ".join((i.official for i in context_info[i:])))

        vartype = engine.contextdef_translate(c.type_)
        try:
            new = vartype(c_values[i])
        except ValueError:
            return f"{c.official} is of a wrong type"
        
        # Specific context handling
        if c.type_=='sentenceID':
            new -= 1
        
        context[c.variable] = new

    # Rule usage
    try:
        info = session.use_rule(name, context)
    except engine.EngineError as e:
        return str(e)
    if info is None:
        out.append(f"Used '{name}' successfully")

        # Contradiction handling
        branches = session.proof.get_last_modified_branches()
        for i in branches:
            out.append(do_contra(session, i))
        
        ended, closed = session.proof_finished()
        if closed:
            out.append("Proof was succesfully finished")
        elif ended:
            out.append("All branches are closed")

    else:
        out.extend(info)

    return "\n".join(out)


def do_undo(session: engine.Session, amount: int) -> str:
    """Undos last [arg] actions"""
    try:
        rules = session.undo(amount)
        return "\n".join(f'Undid rule: {i.rule}' for i in rules)
    except engine.EngineError as e:
        return str(e)

def do_redo(session: engine.Session, amount: int) -> str:
    """Redoes last [arg] undone actions"""
    try:
        session.redo(amount)
    except engine.EngineError as e:
        return str(e)

def do_contra(session: engine.Session, branch: str) -> str:
    """Detects contradictions and handles them by closing their branches"""
    cont = session.deal_closure(branch)
    if cont:
        return cont
    else:
        return f"No contradictions found on branch {branch}."


def do_leave(session) -> str:
    """Deletes the proof"""
    session.reset_proof()
    return "Proof was deleted"


def do_check(session: engine.Session) -> str:
    """Checks the proof"""
    try:
        problems = session.check()
    except engine.EngineError as e:
        return str(e)
    
    if problems:
        return "\n".join(problems)
    else:
        return "Dowód jest poprawny"
    

def do_hint(session: engine.Session) -> str:
    """Gives you a hint"""
    try:
        hints = session.hint()
    except engine.EngineError as e:
        return str(e)
    if hints is not None:
        return "\n\n".join(hints)
    else:
        return "Podpowiedzi nie ma, trzymaj się tam"
    
    
def do_solve(session: engine.Session) -> str:
    """Solves the proof"""
    try:
        return "\n".join(session.solve())
    except engine.EngineError as e:
        return str(e)


def do_write(session: engine.Session, filename: str):
    """
    Writes a whole proof to a file with the provided name; if the file already exists program will append to it.

    Arguments:
        - filename [str]
    """
    proof = session.gettree()
    if os.path.exists(filename):
        with open(filename, 'ab') as f:
            f.write('\n---\n')
            f.writelines([(i+'\n').encode('utf-8') for i in proof])
        return f"Proof appended to {filename}"
    else:
        with open(filename, 'wb') as f:
            f.writelines([(i+'\n').encode('utf-8') for i in proof])
        return f"Proof saved as {filename}"


def do_save(session: engine.Session, filename: str):
    """Saves current state of proof if needed
    
    Arguments:
        - filename [str]
    """
    try:
        return session.save_proof(filename)
    except engine.EngineError as e:
        return e

def do_load(session: engine.Session, filename: str):
    """Loads a saved proof 
    
    Arguments:
        - filename [str]
    """
    try:
        ret = session.load_proof(filename)
        for i in session.proof.nodes.getbranchnames():
            session.deal_closure(i)
        return ret 
    except EngineError as e:
        return e


# Proof navigation


def do_jump(session: engine.Session, where: str) -> str:
    """Changes the branch

    Arguments:
        - Branch name [str/">"/"right"/"left"/"<"]
    """
    try:
        session.jump({'<': 'left', '>': 'right'}.get(where, where))
        name = {'<': 'the left neighbour',
                '>': 'the right neighbour'}.get(where, where)
        return f"Branch changed to {name}"
    except engine.EngineError as e:
        return str(e)


def do_next(session: engine.Session):
    """Finds an open branch and jumps onto it"""
    try:
        session.next()
    except engine.EngineError as e:
        return str(e)


def do_get_rules_docs(session):
    """Returns all of the rules that can be used in this proof system"""
    try:
        return "\n\n".join(("\n---\n".join(i) for i in session.getrules().items()))
    except engine.EngineError as e:
        return str(e)


def do_get_tree(session: engine.Session) -> str:
    """Returns the proof in the form of a tree"""
    try:
        return "\n".join(session.gettree())
    except engine.EngineError as e:
            return str(e)


def do_debug_get_methods(session: engine.Session) -> str:
    """Returns all methods of the session object"""
    return "\n".join(session.get_methods())

def do_access_colors(session: engine.Session, val: int) -> str:
    """Changes the color palette of branches to a given set
    Based on https://sashamaps.net/docs/resources/20-colors/
    
    Possible values:
        - 0 - No colors, instead only animal names will be used for the branches
        - 1 - Yellow, Blue, Black, White, Grey
        - 2 - Everything in 1 + Orange, Lavender, Maroon, Navy
        - 3 - Everything in 2 + Red, Green, Cyan, Magenta, Pink, Teal, Brown, Beige, Mint
        - 4 - Everything in 3 + Purple, Lime, Olive, Apricot
    """
    session.change_accessibility(val)
    return "Color accessibility changed"

command_dict = OrderedDict({
    # Navigation
    'exit': {'comm': do_exit, 'args': []},
    'get rules': {'comm': do_get_rules_docs, 'args': []},
    'get tree': {'comm': do_get_tree, 'args': []},
    'jump': {'comm': do_jump, 'args': 'multiple_strings'},
    'next': {'comm': do_next, 'args': []},
    # Proof manipulation
    # Czy zrobić oddzielne save i write? save serializowałoby tylko do wczytania, a write drukowałoby input
    'write': {'comm': do_write, 'args': [str]},
    'use': {'comm': do_use, 'args': 'multiple_strings'},
    'undo': {'comm': do_undo, 'args': [int]},
    # 'redo': {'comm': do_redo, 'args': [int]},
    'leave': {'comm': do_leave, 'args': []},
    'prove': {'comm': do_prove, 'args': 'multiple_strings'},
    'hint': {'comm': do_hint, 'args': []},
    'solve': {'comm': do_solve, 'args': []},
    'check': {'comm': do_check, 'args': []},
    'save': {'comm': do_save, 'args': [str]},
    'load': {'comm': do_load, 'args': [str]},
    # Program interaction
    'plugin switch': {'comm': do_plug_switch, 'args': [str, str]},
    'plugin get': {'comm': do_plug_get, 'args': [str, str]},
    'plugin update': {'comm': do_plug_update, 'args': [str, str]},
    'plugin list all': {'comm': do_plug_list_all, 'args': []},
    'plugin list': {'comm': do_plug_list, 'args': [str]},
    'plugin gen': {'comm': do_plug_gen, 'args': [str, str]},
    # Setup usage
    'setup save':{'comm': do_setup_save, 'args': [str]},
    'setup delete':{'comm': do_setup_delete, 'args': [str]},
    'setup open':{'comm': do_setup_open, 'args': [str]},
    'setup update':{'comm': do_setup_update, 'args': [str]},
    'setup list':{'comm': do_setup_list, 'args': []},
    
    # Other
    'clear': {'comm': do_clear, 'args': []},
    'debug get methods': {'comm': do_debug_get_methods, 'args': []},
    'access colors': {'comm': do_access_colors, 'args':[int]}
})


def do_help(session) -> str:
    """Lists all possible commands"""
    return "\n".join(command_dict.keys())


command_dict['?'] = {'comm': do_help, 'args': []}

# Front-end setup

def get_rprompt(session: engine.Session):
    """
    Generuje podgląd gałęzi po prawej
    """
    DEF_PROMPT = "Miejsce na twój dowód".split()
    THRESHOLD = 128

    # Proof retrieval
    if session.proof:
        prompt, closed = session.getbranch_strings()
        color =  COLORS.get(session.proof.branch, DEFAULT_COLOR)
    else:
        prompt = DEF_PROMPT
        closed = None
        color = DEFAULT_COLOR

    # Formatting
    to_show = []
    max_len = max((len(i) for i in prompt))+1
    for i in range(len(prompt)):
        spaces = max_len-len(prompt[i])-int(log10(i+1))
        to_show.append("".join((str(i+1), ". ", prompt[i], " "*spaces)))

    # Adding branch closing symbol
    if closed:
        s = str(closed)
        spaces = max_len-len(s)+int(log10(i+1))+3
        to_show.append(s+spaces*" ")

    # Foreground color calculating
    foreground = "#FFFFFF" if color.text_bright else "#000000" 
    new = " \n ".join(to_show)
    return ptk.HTML(f'\n<style fg="{foreground}" bg="{color.rgb}"> {escape(new)} </style>')

def get_toolbar():
    return ptk.HTML('This is a <b><style bg="ansired">Toolbar</style></b>!')


class Autocomplete(ptk.completion.Completer):

    def __init__(self, session: engine.Session, *args, **kwargs):
        self.engine = session
        super().__init__(*args, **kwargs)

    def get_completions(self, document, complete_event):
        full = document.text
        last = document.get_word_before_cursor()
        if not any((full.startswith(com) for com in command_dict.keys())):
            for i in filter(lambda x: x.startswith(full), command_dict.keys()):
                yield ptk.completion.Completion(i, start_position=-len(full))
        elif full == 'jump ':
            try:
                for i in ['<', '>']+self.engine.getbranches():
                    yield ptk.completion.Completion(i, start_position=-len(last))
            except engine.EngineError:
                return
        elif full.startswith('use '):
            # if any((full.rstrip().endswith(rule) for rule in self.engine.getrules().keys())):
            #     yield ptk.completion.Completion(" ", display=ptk.HTML("<b>Sentence number</b>"))
            # else: #TODO: Write autosuggestion for context
            try:
                for i in filter(lambda x: x.startswith(last), self.engine.getrules()):
                    yield ptk.completion.Completion(i, start_position=-len(last))
            except engine.EngineError:
                return

# run


def run() -> int:
    """
    Traktować to podobnie, jak `if __name__=="__main__"`. Funkcja uruchomiona powinna inicjalizować działające UI.
    Obiekt `main.Session` powinien być generowany dla każdego użytkownika. Wystarczy używać metod tego obiektu do interakcji z programem.

    :return: Exit code, -1 restartuje aplikację
    :rtype: int
    """
    session = engine.Session('main', 'config.json')
    ptk.print_formatted_text(ptk.HTML(
        "\n".join(session.start_help()+['Type ? to get command list; type [command]? to get help'])))
    console = ptk.PromptSession(message=lambda: f"{session.get_current_branch()+bool(session.get_current_branch())*' '}# ", rprompt=lambda: get_rprompt(
        session), complete_in_thread=True, complete_while_typing=True, completer=Autocomplete(session))
    while True:
        command = console.prompt().strip()
        logger.info(f"Got a command: {command}")
        if command == '':
            logger.debug("Command empty")
            continue
        try:
            to_perform = parser(command, command_dict)
        except ParsingError as e:
            ptk.print_formatted_text(e)
            logger.debug(f"ParingError: {e}")
            continue
        except TypeError as e:
            ptk.print_formatted_text(f"błąd: złe argumenty")
            logger.debug(f"Exception caught: {e}")
            continue

        for procedure in to_perform:
            performed = performer(procedure, session)
            if isinstance(performed, tp.Generator):
                for i in performed:
                    ptk.print_formatted_text(ptk.HTML(i))
            else:
                ptk.print_formatted_text(ptk.HTML(performed))


def inAppDir(func):
    def wrapper(*args, **kwargs):
        assert os.getcwd().endswith(("/tests", "\\tests")), "cwd musi być folderem `tests` położonym równolegle do `app`"
        os.chdir('../app/appdata')
        if not os.path.exists('config/config_copy.json'):
            from shutil import copy
            copy('config/config.json', 'config/config_copy.json')
            
        ret = func(*args, **kwargs)

        os.chdir('../../tests')
        return ret
    return wrapper


class Runner(object):

    @inAppDir
    def __init__(self) -> None:
        super().__init__()
        self.session = engine.Session('main', 'config_copy.json')

    @inAppDir
    def __call__(self, command: str) -> str:
        try:
            procedure = parser(command, command_dict)[0]
        except ParsingError as e:
            return e
        except TypeError as e:
            return "błąd: złe argumenty"
        return performer(procedure, self.session)
