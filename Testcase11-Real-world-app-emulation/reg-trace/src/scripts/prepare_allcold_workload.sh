#!/bin/bash

EXEC_TIME=30

# usage: pass runtime of functions to ow_reg_functions.sh
./generate_functions.sh $EXEC_TIME

sleep 20s;
# register all possible functions to openwhisk
./reg_all_functions.sh $EXEC_TIME
cd ..;make clean;make rand
#make rand

#./rand_run
