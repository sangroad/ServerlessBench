# Copyright (c) 2020 Institution of Parallel and Distributed System, Shanghai Jiao Tong University
# ServerlessBench is licensed under the Mulan PSL v1.
# You can use this software according to the terms and conditions of the Mulan PSL v1.
# You may obtain a copy of Mulan PSL v1 at:
#     http://license.coscl.org.cn/MulanPSL
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY OR FIT FOR A PARTICULAR
# PURPOSE.
# See the Mulan PSL v1 for more details.
#

from io import StringIO
import random
import os
import yaml
import utils
import numpy as np
import pandas as pd

SECONDS_OF_A_DAY = 3600*24
MILLISECONDS_PER_SEC = 1000

config = yaml.load(open(os.path.join(os.path.dirname(__file__),'config.yaml')), yaml.FullLoader)
SAMPLE_NUM = config['sample_number']
workloadDir = "../CSVs/%i" % SAMPLE_NUM

# Generate mapping between application and IAT
def mapActionandIAT():
    actionFileName = "%s/appComputeInfo.csv" % workloadDir
    IATFileName = "%s/possibleIATs.csv" % workloadDir
    actionIATdict = {}

    actionFile = open(actionFileName, "r")
    IATFile = open(IATFileName, "r")

    actionLines = actionFile.readlines()[1:]
    IATLines = IATFile.readlines()[1:]
    i = 0
    prev = ""
    for line in actionLines:
        appName = line.split(",")[0]
        if appName == prev:
            continue
        actionIATdict[appName] = float(IATLines[i][:-1])
        i += 1
        prev = appName

    actionFile.close()
    IATFile.close()

    return actionIATdict

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
    print(appNameStr)
    IATs = list(map(int, actionDict.values()))
    print(IATs)
    print(len(actionDict))

    for i in range(totalRunTime):
        actionLen = len(actionDict)
        data = np.zeros(actionLen)
        for idx, val in enumerate(IATs):
            if i % val == 0:
                data[idx] = 1

        dataStr = ','.join(["%d" % num for num in data]) + "\n"
        timelineFile.write(dataStr)

    timelineFile.close()
    print("function timeline generated")


# Generate 1ms scale timeline
def invokeTimelineGenOld(actionDict):
    # millisecond
    totalRunTime = config['total_run_time'] * MILLISECONDS_PER_SEC
    timelineFileName = "%s/funcTimeline_%i.csv" % (workloadDir, SAMPLE_NUM)
    #timelineFile = open(timelineFileName, "w")
    csv_columns = []
    csv_columns.append("appName")
    csv_rows = []

    for i in range(totalRunTime):
        csv_columns.append(i)

    for key, value in actionDict.items():
        row = []
        data = np.zeros(totalRunTime)
        actionName = key
        IAT = int(value)
        print(value)

        for i in range(0, totalRunTime, IAT):
            data[i] = 1

        row.append(actionName)
        row.extend(data)
        #row.append(data)
        csv_rows.append(row)

    df = pd.DataFrame(csv_rows, columns=csv_columns)
    # df = df.transpose()
    df.to_csv(timelineFileName, mode="w")

if __name__ == '__main__':
    actionIATdict = mapActionandIAT()
    invokeTimelineGen(actionIATdict)