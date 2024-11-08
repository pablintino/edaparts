#! /bin/bash
set -e

export PATH=${PYENV_DEST}/bin

if [ "$RUN_MIGRATIONS" == "true" ]; then
    edaparts-migrate-upgrade
fi

APP_LOCATION="$(python -c 'import site; print(site.getsitepackages()[0])')/edaparts/app/main.py"
exec fastapi run "$APP_LOCATION" --port "$APP_PORT" --workers "$APP_WORKERS"
