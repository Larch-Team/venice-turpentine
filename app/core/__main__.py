import json
import os
import sys
from datetime import datetime
from manager import FileManager
from engine import Session
from constants import DEBUG, VERSION

import pop_engine as pop

# Wyjaśnienie sensu istnienia pliku:
# https://www.notion.so/szymanski/The-curious-case-of-the-UserInterface-socket-ab76cfc810d9486bb8ce9199f0cc7efc

if __name__ == "__main__":
    try:
        manager = FileManager(DEBUG, VERSION)
        manager.download_required()

        # Log clearing
        if os.path.exists('log.log'):
            os.remove('log.log')

        # UserInterface socket generation
        UI = pop.Socket('UserInterface', os.path.abspath(
            'plugins/UserInterface'), '0.0.1', '__template__')

        # return exit code -1 to initiate a restart (useful for UI plugin switching)
        exit_code = -1  # Not implemented in cmd plugin
        while exit_code == -1:

            # App run
            try:
                configs = os.listdir(os.path.abspath('config'))
            except FileNotFoundError:
                os.mkdir('config')
                configs = []
            if not configs:
                UI.plug('CLI')
            else:
                p = 'config/config.json' if 'config.json' in configs else config[0]
                with open(p, 'r') as file:
                    config = json.load(file)
                UI.plug(config['chosen_plugins']['UserInterface'])
            exit_code = UI().run()

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
        sys.exit(exit_code)
