#!/bin/bash

EXEC_TIME=40

# usage: pass runtime of functions to ow_reg_functions.sh
./generate_functions.sh $EXEC_TIME
./ow_reg_functions.sh $EXEC_TIME
make clean
make

#./run
