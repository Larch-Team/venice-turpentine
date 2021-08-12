@echo off
echo Pamietaj, aby byc w odpowiednim dysku
set cwd=%CD% 
cd %appdata%
rmdir larch /q /s
cd %cwd%