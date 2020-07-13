@echo off

call activate venv
python esbo-etc.py %*
call conda deactivate