import os
import sys
import urllib

class FileManager(object):
    NEED = [
        
    ]
    BRANCH = "dist-lab"
    REPO_URL = f"https://raw.githubusercontent.com/Larch-Team/Larch/{BRANCH}/app/"
    
    def __init__(self, debug: bool) -> None:
        super().__init__()
        if debug:
            self.directory = os.path.abspath(__file__).removesuffix('manager.py')+'../appdata'
        else:
            self.directory = os.getenv('appdata')+'/Larch'
        os.chdir(self.directory)
        sys.path = [self.directory] + sys.path
        
    def prepare_dir(self):
        if not os.path.exists(self.directory):
            os.mkdir(self.directory)
        
    def download_needed(self):
        pass
        
    def download(self, file: str):
        pass