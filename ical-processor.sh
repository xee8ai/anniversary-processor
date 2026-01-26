#!/bin/bash

BASE_DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )

rm -rf $BASE_DIR/output/ical
/usr/bin/env python3 $BASE_DIR/src/anniversary-processor.py ical
