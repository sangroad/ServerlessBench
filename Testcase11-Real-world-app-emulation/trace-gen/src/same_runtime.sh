#!/bin/bash

# usage: pass directory of successful workload
python3 workloadGenerator.py $1 10
make clean
make success

./success_run $1
