import os
from json import dumps

plugins = {}
for socket in os.listdir('app/appdata/plugins'):
    plugins[socket] = {}
    for plugin in os.listdir(f'app/appdata/plugins/{socket}'):
        if '__pycache__' in plugin:
            continue
        elif os.path.isdir(f'app/appdata/plugins/{socket}/{plugin}'):
            plugins[socket][plugin] = [os.path.join(root, name) for root, dirs, files in os.walk(f'app/appdata/plugins/{socket}/{plugin}') for name in files if '__pycache__' not in root]
        elif plugin in ('__init__.py', '__utils__.py', '__template__.py'):
            continue
        else:
            plugins[socket][plugin[:-3]] = [f'plugins/{socket}/{plugin}']

setups = {i[:-5]:f'app/appdata/setups/{i}' for i in os.listdir('app/appdata/setups')}
    

print(dumps({'plugins':plugins, 'setups':setups}).replace('\\\\', '/'))