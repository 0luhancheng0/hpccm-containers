#!/bin/bash

find . -name '*.py' -not \( -name "__init__.py" -o -name "*-hpccm.py" \) -mindepth 2 | parallel 'python {} > {//}/Singularity.{/.}'
find . -name '*-hpccm.py' -mindepth 2 | parallel 'hpccm --recipe {} --format singularity --singularity-version 3.7 > {//}/Singularity.{/.}'
