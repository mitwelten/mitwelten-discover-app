#!/bin/sh

python3 -m unittest discover -s ./tests/util -p "*_test.py"
python3 -m unittest discover -s ./tests/model -p "*_test.py"
