#!/usr/bin/env bash

MAYAPY_PATH="/usr/autodesk/maya2024/bin/mayapy"
if [ ! -e ]; then
     echo "ERROR: mayapy not found" >&2
     exit 1
fi

# get path of current script
SCRIPT_PATH="$(realpath ${BASH_SOURCE})"
echo "script path" $SCRIPT_PATH

# remove script from base path
BASE_DIR="${SCRIPT_PATH%/*}"
echo "base dir:" $BASE_DIR

if [ ! -d "$BASE_DIR" ]; then
     echo "ERROR: BASE_DIR not found"
     exit
fi

export PYTHONPATH="$(realpath ${BASE_DIR}/..):$PYTHONPATH"

PIP_LIST=$("${MAYAPY_PATH}" -m pip list 2>/dev/null)

# check pytest is installed
if [ -z "$(echo ${PIP_LIST} | grep pytest)" ]; then
     echo "ERROR: failed to find pytest" >&2
     exit 1
fi
echo "Found pytest"

"${MAYAPY_PATH}" -m pytest "${BASE_DIR}/tests.py" -s
