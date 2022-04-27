#!/bin/bash

EXEC_TIME=100

./generate_functions.sh $EXEC_TIME
#./ow_reg_functions.sh $EXEC_TIME
cd ..
python3 workloadGenerator.py --threshold $EXEC_TIME
make clean
make

#./run
