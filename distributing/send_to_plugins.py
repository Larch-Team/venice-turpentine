from json import dump
import shutil
from file_list import files
import os

assert os.getcwd().endswith('Larch'), "Zmień CWD"

files = files()
setups = files['setups']
plugins = files['plugins']

to_submit = list(setups.values()) + sum(sum((list(i.values()) for i in plugins.values()), []), [])
for i in to_submit:
    shutil.copyfile('app/appdata/'+i, '../larch-plugins/'+i)
    
for i in plugins:
    for j in ['__init__.py', '__template__.py', '__utils__.py']:
        if os.path.isfile(f'app/appdata/plugins/{i}/{j}'):
            shutil.copyfile(f'app/appdata/plugins/{i}/{j}', f'../larch-plugins/plugins/{i}/{j}')

with open('../larch-plugins/files.json', 'w') as f:
    dump(files, f)