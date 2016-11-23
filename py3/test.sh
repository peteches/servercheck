#!/bin/bash

set -x

python3 -m venv --without-pip $PWD/virtualenv

source $PWD/virtualenv/bin/activate

curl https://bootstrap.pypa.io/get-pip.py | python
deactivate

source $PWD/virtualenv/bin/activate

pip install -r test-reqs.txt

python3 -m nose
