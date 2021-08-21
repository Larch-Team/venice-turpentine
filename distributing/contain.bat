@echo off
xcopy app\core app\core_temp /S /I
python -m pip install -r distributing/requirements.txt --target app/core_temp
python -m zipapp app/core_temp -o app/larch.pyz -c
rmdir app\core_temp /q /s