#!/bin/bash

# usage: pass directory of successful workload
python3 workloadGenerator.py --path $1
cd ..;make clean;make success
#make success

./success_run $1
