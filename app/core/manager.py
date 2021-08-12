from genericpath import isfile
import os
import sys
from urllib import request as web_request
from needed_files import NEED

class FileManager(object):
    
    BRANCH = "dist-lab"
    REPO_URL = f"https://raw.githubusercontent.com/Larch-Team/Larch/{BRANCH}"
    
    def __init__(self, debug: bool) -> None:
        super().__init__()
        if debug:
            self.directory = os.path.abspath(__file__).removesuffix('manager.py')+'../appdata'
        else:
            self.directory = os.getenv('appdata')+'/Larch'
            if not os.path.isdir(self.directory):
                os.mkdir(self.directory)
        os.chdir(self.directory)
        sys.path = [self.directory] + sys.path
        
        self.download_needed()
        
    def prepare_dirs(self, folder: str):
        path = self.directory[:]
        for i in folder.split('/'):
            path = path + '/' + i
            if '.' in i:
                break
            if not os.path.isdir(path):
                os.mkdir(path)
        
    def download_needed(self):
        for i in NEED:
            if not isfile(f'{self.directory}/{i}'):
                self.download(i)
            
    def download(self, file: str):
        self.prepare_dirs(file)
        url = f"{self.REPO_URL}/app/appdata/{file}"
        response = web_request.urlopen(url)
        webContent = response.read()
        with open(f'{self.directory}/{file}', 'wb') as f:
            f.write(webContent)