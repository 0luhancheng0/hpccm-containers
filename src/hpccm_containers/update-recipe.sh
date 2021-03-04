#!/bin/bash

find . -name '*.py' -not \( -name "__init__.py" \) -mindepth 2 | parallel '/Users/ChengLuhan/anaconda3/envs/py37/bin/python {} > {//}/Singularity.{/.}'
