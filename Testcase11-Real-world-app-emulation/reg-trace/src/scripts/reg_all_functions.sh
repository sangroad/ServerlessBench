#!/bin/bash

# Register all possible functions to openwhisk.
# After registeration, rand_run will run functions randomly

EXEC_TIME=$1

for i in {000..130};
	do
		./reg_999_functions.sh $i $EXEC_TIME &
	done

for job in `jobs -p`;
	do
		wait ${job};
	done
