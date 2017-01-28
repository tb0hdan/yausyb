#!/bin/bash

if [ "$(uname)" = "Darwin" ]; then
    prefix="arch -i386"
    python="/usr/bin/python2.7"
else
    prefix=""
    python=$(which python2.7)
fi

${prefix} ${python} -m yausyb.cli.main
