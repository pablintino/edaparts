#!/bin/sh

ROOT_DIR="$1"

if [ -z "$ROOT_DIR" ]  ; then
    echo "ERROR: ROOT_DIR as argument required, but not received" >&2
    exit 1
fi

if [ ! -d "${ROOT_DIR}" ]; then
    echo "ERROR: $ROOT_DIR not found" >&2
    exit 1
fi

rm -rf "${ROOT_DIR}/.venv"
python3 -m venv "${ROOT_DIR}/.venv"
. "${ROOT_DIR}/.venv/bin/activate"
pip3 install build
"${ROOT_DIR}/.venv/bin/pip3" install -e .[dev]
