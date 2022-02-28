# this file is for debug
import os
import yaml

SECONDS_OF_A_DAY = 3600*24
MILLISECONDS_PER_SEC = 1000

config = yaml.load(open(os.path.join(os.path.dirname(__file__),'config.yaml')), yaml.FullLoader)
SAMPLE_NUM = config['sample_number']
workloadDir = "../CSVs/%i" % SAMPLE_NUM

def generateActionIATMapping():
    actionFileName = "%s/appComputeInfo.csv" % workloadDir
    IATFileName = "%s/possibleIATs.csv" % workloadDir
    appAndIATMapFileName = "%s/appandIATMap.csv" % workloadDir
    actionIATdict = {}

    actionFile = open(actionFileName, "r")
    IATFile = open(IATFileName, "r")
    outfile = open(appAndIATMapFileName, "w")
    outfile.write("appName,IAT,execTime\n")

    actionLines = actionFile.readlines()[1:]
    IATLines = IATFile.readlines()[1:]
    i = 0
    appExecTime = 0
    prev = ""
    for line in actionLines:
        splitted = line.split(",")
        appName = splitted[0]
        execTime = splitted[3]
        appExecTime += int(execTime)
        if appName == prev:
            continue
        # actionIATdict[appName] = float(IATLines[i][:-1])
        outfile.write("%s,%s,%d\n" % (appName, IATLines[i][:-1], appExecTime))
        i += 1
        prev = appName
        appExecTime = 0

    actionFile.close()
    IATFile.close()

    return actionIATdict

if __name__ == '__main__':
	generateActionIATMapping()