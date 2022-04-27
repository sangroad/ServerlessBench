#!/bin/bash

# This script is for workloads that trace is changed,
# but function execution time is not changed

EXEC_TIME=30

# usage: pass runtime of functions to ow_reg_functions.sh
./generate_functions.sh $EXEC_TIME

make clean
make rand

#./rand_run
