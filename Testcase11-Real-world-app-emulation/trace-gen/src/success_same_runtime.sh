#!/bin/bash

EXEC_TIME=40
# usage: pass directory of successful workload
python3 workloadGenerator.py $1 $EXEC_TIME
make clean
make success

./success_run $1
