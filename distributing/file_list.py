import os
from json import dumps

l = {}

for socket in os.listdir('app/appdata/plugins'):
    l[socket] = {}
    for plugin in os.listdir(f'app/appdata/plugins/{socket}'):
        if os.path.isdir(f'app/appdata/plugins/{socket}/{plugin}'):
            l[socket][plugin] = [os.path.join(root, name) for root, dirs, files in os.walk(f'app/appdata/plugins/{socket}/{plugin}') for name in files if '__pycache__' not in root]
        elif plugin in ('__init__.py', '__utils__.py', '__template__.py'):
            continue
        else:
            l[socket][plugin[:-3]] = [f'plugins/{socket}/{plugin}']

print(dumps(l).replace('\\\\', '/'))