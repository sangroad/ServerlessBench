#!/bin/bash
./generate_functions.sh
#./ow_reg_functions.sh
cd ..;python3 workloadGenerator.py

cd ..;make clean;make
