#!/bin/bash
echo 'pytest + coverage: Python 2...'
python2 -m coverage run --source mainframe_1_2 -m pytest -v
echo 'pytest + coverage: Python 3...'
python3 -m coverage run --source mainframe_1_2 -m pytest -v

coverage report -m