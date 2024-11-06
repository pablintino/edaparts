#!/bin/sh

export PATH=${PYENV_DEST}/bin
exec fastapi run $(python -c 'import site; print(site.getsitepackages()[0])')/edaparts/app/main.py --port 80 --workers 4
