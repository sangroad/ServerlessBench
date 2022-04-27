#!/bin/bash

FIRST=$1
EXEC_TIME=$2

for j in $(seq -f "%03g" 000 999)
do
	../action_update.sh $FIRST $j $EXEC_TIME 128
done
