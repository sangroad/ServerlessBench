import os
import yaml
import numpy as np
import pandas as pd
import random

SECONDS_OF_A_DAY = 3600*24
MILLISECONDS_PER_SEC = 1000

config = yaml.load(open(os.path.join(os.path.dirname(__file__),'config.yaml')), yaml.FullLoader)
SAMPLE_NUM = config['sample_number']
workloadDir = "../CSVs/%i" % SAMPLE_NUM

def readMappingCSV():
    mappingFileName = "%s/appandIATMap.csv" % (workloadDir)
    mappingFile = open(mappingFileName, "r")
    lines = mappingFile.readlines()[1:]
    ret = {}

    for line in lines:
        splitted = line.split(",")
        name = splitted[0]
        IAT = splitted[1]
        ret[name] = IAT

    return ret

def invokeTimelineGen(actionDict):
    # millisecond
    totalRunTime = config['total_run_time'] * MILLISECONDS_PER_SEC
    timelineFileName = "%s/funcTimeline_%i.csv" % (workloadDir, SAMPLE_NUM)
    timelineFile = open(timelineFileName, "w")
    appNameStr = ""

    for key in actionDict:
        appNameStr += key + ","

    appNameStr = appNameStr[:-1] + "\n"

    timelineFile.write(appNameStr)
    IATs = list(map(int, actionDict.values()))

    for i in range(1, totalRunTime):
        actionLen = len(actionDict)
        data = np.zeros(actionLen)
        for idx, val in enumerate(IATs):
            if i % val == 0:
                data[idx] = 1

        dataStr = ','.join(["%d" % num for num in data]) + "\n"
        timelineFile.write(dataStr)

    timelineFile.close()
    print("Function timeline generation complete!")

if __name__ == '__main__':
    actionIATDict = readMappingCSV()
    invokeTimelineGen(actionIATDict)