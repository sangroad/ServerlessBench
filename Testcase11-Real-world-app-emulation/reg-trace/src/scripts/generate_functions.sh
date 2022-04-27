#!/bin/bash

cd ..
if [ -z "$1" ]; then
	python3 actionInfoCSVGenerator.py
	python3 IATCSVGenerator.py
	python3 funcTimelineGenerator.py
else
	python3 actionInfoCSVGenerator.py --threshold $1
	python3 IATCSVGenerator.py --threshold $1
	python3 funcTimelineGenerator.py --threshold $1
fi
