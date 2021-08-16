from genericpath import isfile
import os
import sys
from typing import Union
from urllib import request as web_request
from urllib.error import URLError
from required_files import NEED
from json import dump, load
from tqdm import tqdm
from time import sleep

class FileManager(object):
    
    BRANCH = "dist-lab"
    REPO_URL = f"https://raw.githubusercontent.com/Larch-Team/larch-plugins/{BRANCH}"
    DIRECTORY = None
    
    def __init__(self, debug: bool = None, larch_version: str = None) -> None:
        super().__init__()
        assert self.DIRECTORY or (debug and larch_version), "Jedno trzeba dostarczyć"
        if larch_version and debug:
            self.select_dir(debug, larch_version)
            self.DIRECTORY = self.directory
        else:
            self.directory = self.DIRECTORY
        
        
    def select_dir(self, debug: bool, larch_version: str):
        MANIFEST = {
            'larch_version':larch_version,
            'additional':[]
        }
        
        if debug:
            self.directory = os.path.abspath(__file__).removesuffix('manager.py')+'../appdata'
        else:
            self.directory = os.getenv('appdata')+'/Larch'
            if not os.path.isdir(self.directory):
                os.mkdir(self.directory)
            if not os.path.isfile(f'{self.directory}/manifest.json'):
                with open(f'{self.directory}/manifest.json', 'w') as f:
                    dump(MANIFEST, f)
                    
        os.chdir(self.directory)
        sys.path = [self.directory] + sys.path
        
        
    def prepare_dirs(self, folder: str):
        path = self.directory[:]
        for i in folder.split('/'):
            path = path + '/' + i
            if '.' in i:
                break
            if not os.path.isdir(path):
                os.mkdir(path)
        
        
    def download_required(self):
        desc='Please wait while we download required plugins'
        pbar = tqdm(NEED, desc, unit='file(s)', position=0, leave=True)
        for i in pbar:
            pbar.write(f"Downloading {i}")
            if not isfile(f'{self.directory}/{i}'):
                for error in self.try_download(i, required=True):
                    pbar.write(error)
        os.system('cls')


    def try_download(self, file: str, required: bool = False):
        tries = 0
        while not self.download(file, required):
            tries += 1
            yield f'Couldn\'t download {file}, retrying in 5 seconds (retried {tries} time(s))'
            sleep(5)
        

    def download(self, file: str, required: bool = False) -> bool:
        self.prepare_dirs(file)
        url = f"{self.REPO_URL}/app/appdata/{file}"
        try:
            response = web_request.urlopen(url)
        except URLError as e:
            return False
        webContent = response.read()
        with open(f'{self.directory}/{file}', 'wb') as f:
            f.write(webContent)
            if not required:
                man = self.read_manifest()
                man['additional'].append(file)
                self.write_manifest(man)
        return True
    
    
    @staticmethod
    def read_manifest():
        with open("manifest.json", 'r') as target:
            return load(target)


    @staticmethod
    def write_manifest(manifest):
        with open("manifest.json", 'w') as target:
            dump(manifest, target)
