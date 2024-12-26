import json
import os
import sys
from datetime import datetime
from manager import FileManager
from engine import Session
from constants import DEBUG, FORCE_DOWNLOAD, VERSION
import platform

import pop_engine as pop

# Wyjaśnienie sensu istnienia pliku:
# https://www.notion.so/szymanski/The-curious-case-of-the-UserInterface-socket-ab76cfc810d9486bb8ce9199f0cc7efc

if __name__ == "__main__":
    try:
        v1, v2, _ = platform.python_version().split('.')
        if v1 != '3' or int(v2)<9:
            print('Larch wymaga co najmniej Pythona 3.9 do działania. Zainstaluj go ze strony https://www.python.org/downloads/')
            input()
            sys.exit()
            
        manager = FileManager(DEBUG, VERSION)
        manager.download_required(FORCE_DOWNLOAD)

        # Log clearing
        if os.path.exists('log.log'):
            os.remove('log.log')

        # UserInterface socket generation
        UI = pop.Socket('UserInterface', os.path.abspath(
            'plugins/UserInterface'), '0.0.1', '__template__')

        # App run
        try:
            configs = os.listdir(os.path.abspath('config'))
        except FileNotFoundError:
            os.mkdir('config')
            configs = []
        if not configs:
            UI.plug('CLI')
        else:
            p = 'config/config.json' if 'config.json' in configs else configs[0]
            with open(p, 'r') as file:
                config = json.load(file)
            UI.plug(config['chosen_plugins']['UserInterface'])
        UI().run()

    except Exception as e:
        if DEBUG:
            raise e
    
        manager.prepare_dirs('crashes')
        if os.path.isfile('log.log'):
            with open('log.log', 'r') as l:
                logs = l.read()
        else:
            logs = ''
        with open(f'crashes/crash-{datetime.now().strftime("%d-%m-%Y-%H-%M")}.txt', 'w') as f:
            f.write(logs)
            f.write('\nEXCEPTION:\n')
            f.write(str(e))
    else:
        sys.exit()
