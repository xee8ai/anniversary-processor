#!/bin/bash

BASE_DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )

/usr/bin/env python3 $BASE_DIR/src/anniversary-processor.py html
