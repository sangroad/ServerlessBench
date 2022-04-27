#!/bin/bash

if [ -z "$1" ] && [ -z "$2" ]; then
	python3 ../workloadGenerator
elif [ -z "$2" ]; then
	if [[ "$1" == *"_"* ]]; then
		python3 ../workloadGenerator --path $1
	else
		python3 ../workloadGenerator --threshold $1
	fi
else
	python3 ../workloadGenerator --path $1 --threshold $2
fi