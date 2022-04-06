import os
import sys
import yaml
import numpy as np
import pandas as pd
import random

SECONDS_OF_A_DAY = 3600*24
MILLISECONDS_PER_SEC = 1000

config = yaml.load(open(os.path.join(os.path.dirname(__file__),'config.yaml')), yaml.FullLoader)
SAMPLE_NUM = config['sample_number']
workloadDir = "../CSVs/%i" % SAMPLE_NUM
successDir = "../CSVs/success"

def dedupLists(list1, list2):
	return list(set(list1) - set(list2))

def getLeftIATs(IATs):
	ret = []
	for val in IATs:
		if val != -1:
			ret.append(val)

	return ret

def calAppExecTime(appList):
	appExecTime = 0
	prev = ""
	ret = {}
	funcPerApp = {}
	funcPerAppCnt = 0

	for val in appList:
		splitted = val.split(",")
		appName = splitted[0]
		execTime = splitted[3]

		if prev == "":
			prev = appName

		if appName == prev:
			appExecTime += int(execTime)
			funcPerAppCnt += 1
		else:
			prev = appName
			appExecTime = int(execTime)
			funcPerAppCnt = 1

		ret[appName] = appExecTime
		funcPerApp[appName] = funcPerAppCnt

	return (ret, funcPerApp)

# Generate mapping between app and IAT
def mapActionandIAT(path):
	actionFileName = "%s/appComputeInfo.csv" % path
	IATFileName = "%s/possibleIATs.csv" % path
	actionIATdict = {}	# key: action name, value: IAT

	actionFile = open(actionFileName, "r")
	IATFile = open(IATFileName, "r")

	actionLines = actionFile.readlines()[1:]
	IATLines = IATFile.readlines()[1:]

	for idx, line in enumerate(IATLines):
		IATLines[idx] = round(float(line[:-1]))

	IATLines.sort()
	appExecTime, funcsPerApp = calAppExecTime(actionLines)
	possibleApps = {}   # key: IAT, value: list of map-able apps
	IATcnt = {}    # key: IAT, value: count

	for IAT in IATLines:
		tmpList = []
		for key, time in appExecTime.items():
			if IAT > time * 2:
				tmpList.append(key)
		if IATcnt.get(IAT) == None:
			IATcnt[IAT] = 1
		else:
			IATcnt[IAT] += 1

		possibleApps[IAT] = tmpList

	allocated = []
	for key, apps in possibleApps.items():
		for i in range(IATcnt[key]):
			dedup = dedupLists(apps, allocated)
			selected = random.choice(dedup)
			allocated.append(selected)
			actionIATdict[selected] = key


	print("App and IAT mapping done!")
	actionFile.close()
	IATFile.close()

	rps = 0
	for _, iat in actionIATdict.items():
		rps += MILLISECONDS_PER_SEC / iat

	print("Workload's estimated RPS: %d" % rps)

	return (actionIATdict, appExecTime, funcsPerApp)

def writeMappingCSV(actionDict, appExecTime, funcPerApp):
	appAndIATMapFileName = "%s/appandIATMap.csv" % workloadDir
	outfile = open(appAndIATMapFileName, "w")
	outfile.write("appName,IAT,execTime,functionsPerApp\n")

	for key, value in actionDict.items():
		outfile.write("%s,%s,%s,%s\n" % (key, value, appExecTime[key], funcsPerApp[key]))

	outfile.close()

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

# argument: name of successful workload
if __name__ == '__main__':
	# argument = sys.argv
	# del argument[0]

	# if len(argument) > 0:
	# 	baseDir = "%s/%s" % (successDir, argument[0])
	# 	mapActionandIAT(baseDir)
	# else:
		# actionIATdict, appExecTime, funcsPerApp = mapActionandIAT(workloadDir)

	actionIATdict, appExecTime, funcsPerApp = mapActionandIAT(workloadDir)
	writeMappingCSV(actionIATdict, appExecTime, funcsPerApp)
	invokeTimelineGen(actionIATdict)