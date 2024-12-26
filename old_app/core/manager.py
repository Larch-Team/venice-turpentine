from genericpath import isfile
import os
import sys
from typing import Callable, Iterator, Union
from urllib import request as web_request
from urllib.error import URLError
from exceptions import FileManagerError
from misc import setup_iter
from required_files import NEED
from json import loads
from tqdm import tqdm
from time import sleep
from appdirs import user_data_dir
from constants import REPO_URL, ALLOW_DOWNLOAD
import ssl
import certifi

def try_gen(func: Callable[..., Union[str, None]]) -> Iterator[str]:
    def wrapped(*args, **kwargs):
        tries = 0
        while (info := func(*args, **kwargs)):
            tries += 1
            if tries > 6:
                raise FileManagerError("Couldn't download the file")
            yield f'{info}, retrying in 5 seconds (retried {tries} time(s))'
            sleep(5)
        if tries > 0:
            yield 'It was successful'
    return wrapped


class FileManager(object):

    @staticmethod
    def context():
        return ssl.create_default_context(cafile=certifi.where())

    # Class properties

    _directory = None

    @property
    def directory(self):
        return type(self)._directory

    @directory.setter
    def directory(self, val):
        type(self)._directory = val

    _plugins = None

    @property
    def plugins(self):
        return type(self)._plugins

    @plugins.setter
    def plugins(self, val):
        type(self)._plugins = val

    _setups = None

    @property
    def setups(self):
        return type(self)._setups

    @setups.setter
    def setups(self, val):
        type(self)._setups = val

    # Methods

    def __init__(self, debug: bool = None, larch_version: str = None) -> None:
        super().__init__()
        assert self.directory or (
            debug is not None and larch_version is not None), "Jedno trzeba dostarczyć"
        if larch_version is not None and debug is not None:
            self.debug = debug
            self.select_dir(larch_version)

    def select_dir(self, larch_version: str):
        """Creates a folder for storing the software data and chooses it as the cwd"""
        # MANIFEST = {
        #     'larch_version':larch_version,
        #     'additional':[]
        # }

        if self.debug:
            self.directory = os.path.abspath(
                __file__).removesuffix('manager.py')+'../appdata'
        else:
            self.directory = user_data_dir(appname='Larch', appauthor=False, version=larch_version)
        self.prepare_dirs('plugins')
        self.prepare_dirs('setups')
        self.prepare_dirs('saved_proofs')

        # if not os.path.isfile(f'{self.directory}/manifest.json'):
        #     with open(f'{self.directory}/manifest.json', 'w') as f:
        #         dump(MANIFEST, f)
        os.chdir(self.directory)
        sys.path = [self.directory] + sys.path
        

    def prepare_dirs(self, folder: str, absolute: bool = False):
        """Creates the missing directories"""
        full_folder = f'{self.directory}/{folder}' if not absolute else folder 
        osp = os.path
        assert osp.isabs(full_folder)
        if osp.isdir(full_folder):
            return
        self.prepare_dirs(osp.dirname(full_folder), True)
        os.mkdir(full_folder)
    

    @try_gen
    def get_files(self) -> Union[None, str]:
        """Downloads the file list"""
        if self.plugins is None or self.setups is None:
            try:
                response = web_request.urlopen(f"{REPO_URL}/files.json", context=self.context())
            except URLError as e:
                return "Couldn't download the file list"
            files = loads(response.read())
            self.plugins = files['plugins']
            self.setups = files['setups']
        return None

    @try_gen
    def download_file(self, file: str, required: bool = False) -> Union[None, str]:
        """Downloads a given file and saves it at the given location"""
        assert ALLOW_DOWNLOAD
        self.prepare_dirs(os.path.dirname(file))
        url = f"{REPO_URL}/{file}"
        try:
            response = web_request.urlopen(url.replace(' ', '%20'), context=self.context())
        except URLError as e:
            return f'Couldn\'t download {file}, because "{e.reason}"'
        webContent = response.read()
        with open(f'{self.directory}/{file}', 'wb') as f:
            f.write(webContent)
            # if not required:
            #     man = self.read_manifest()
            #     if file not in man['additional']:
            #         man['additional'].append(file)
            #         self.write_manifest(man)
        return None

    def download_required(self, force: bool = False):
        """Downloads all the required files according to `required_files.py`"""
        desc = 'Please wait while we download required plugins'
        pbar = tqdm(NEED, desc, unit='file(s)', position=0, leave=True)
        for i in pbar:
            pbar.write(f"Downloading {i}")
            if not isfile(f'{self.directory}/{i}') or (force and ALLOW_DOWNLOAD):
                for error in self.download_file(i, required=True):
                    pbar.write(error)
        os.system('cls')

    # Plugin downloading

    def download_plugin(self, socket: str, plugin: str, force: bool) -> Iterator[str]:
        """Downloads a plugin from the `Larch-Team/larch-plugins`"""
        yield "Checking the required files"
        yield from (f"\t{i}" for i in self.get_files())
        try:
            files = self.plugins.get(socket, None)[plugin]
        except TypeError:
            raise FileManagerError("No such socket")
        except KeyError:
            raise FileManagerError("No such plugin")
        for n, file in enumerate(files):
            yield f"({n+1}/{len(files)}) Downloading {file}"
            if isfile(f'{self.directory}/{file}') and not force:
                yield "\tThis file already exists"
            else:
                yield from (f"\t{i}" for i in self.download_file(file))

    # Setups

    @staticmethod
    def setup_list() -> list[str]:
        """Returns installed setups"""
        return [name.removesuffix('.json') for name in os.listdir('setups')]

    def setup_search(self) -> list[str]:
        """Returns available setups"""
        self.get_files()
        return [i for i in self.setups.keys() if i not in self.setup_list()]

    def download_setup(self, setup_name: str, force: bool) -> Iterator[str]:
        """Downloads a setup file"""
        if setup_name in self.setup_list() and not force:
            yield "This setup exists locally"
            return
        yield "Checking if the setup exists"
        yield from (f"\t{i}" for i in self.get_files())
        try:
            file = self.setups[setup_name]
        except KeyError:
            raise FileManagerError("No such setup exists")
        else:
            yield "\tSetup was found"
        yield f"Downloading {file}"
        yield from (f"\t{i}" for i in self.download_file(file))

    def download_setup_plugins(self, setup_name: str, force: bool) -> Iterator[str]:
        """Downloads a setup file and automatically downloads all the required files"""
        SOCKET_AMOUNT = 5

        yield from self.download_setup(setup_name, force)
        if setup_name in self.setup_list():
            file = f'setups/{setup_name}.json'
        else:
            file = self.setups[setup_name]
        for n, (socket, plugin) in enumerate(setup_iter(file)):
            yield f"({n+1}/{SOCKET_AMOUNT}) Downloading {plugin} for the {socket} socket"
            yield from (f"\t{i}" for i in self.download_plugin(socket, plugin, force))

    # @staticmethod
    # def read_manifest():
    #     with open("manifest.json", 'r') as target:
    #         return load(target)

    # @staticmethod
    # def write_manifest(manifest):
    #     with open("manifest.json", 'w') as target:
    #         dump(manifest, target)
