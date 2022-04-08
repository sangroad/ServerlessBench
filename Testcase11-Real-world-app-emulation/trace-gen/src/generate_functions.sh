#!/bin/bash

python3 actionInfoCSVGenerator.py $1
python3 IATCSVGenerator.py $1
python3 funcTimelineGenerator.py $1
