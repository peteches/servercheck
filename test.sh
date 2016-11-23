#!/bin/bash

set -x

python3 -m venv $PWD/virtualenv

source $PWD/virtualenv/bin/activate

pip install -m test-reqs.txt

nose2
