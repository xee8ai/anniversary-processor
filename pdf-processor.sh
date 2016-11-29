#!/bin/bash

BASE_DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )

# If there is a local venv: activate
if [ -d $BASE_DIR/venv ]; then
	source $BASE_DIR/venv/bin/activate
fi

/usr/bin/env python3 $BASE_DIR/src/anniversary-processor.py pdf
