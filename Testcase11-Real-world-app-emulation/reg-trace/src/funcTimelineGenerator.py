import os
import argparse
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
	funcRuntimePerApp = {}	# key: app name, value: runtime of all functions

	for val in appList:
		splitted = val.split(",")
		appName = splitted[0]
		execTime = int(splitted[3])

		if prev == "":
			prev = appName
			funcRuntimePerApp[appName] = list()

		if appName == prev:
			appExecTime += execTime
			funcPerAppCnt += 1
		else:
			prev = appName
			appExecTime = execTime
			funcPerAppCnt = 1
			funcRuntimePerApp[appName] = list()

		ret[appName] = appExecTime
		funcPerApp[appName] = funcPerAppCnt
		funcRuntimePerApp[appName].append(execTime)

	return (ret, funcPerApp, funcRuntimePerApp)

# Generate mapping between app and IAT. Function's runtime is same
def mapActionandIATSame(path):
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
	appExecTime, funcsPerApp, _ = calAppExecTime(actionLines)
	possibleApps = {}   # key: IAT, value: list of map-able apps
	IATcnt = {}    # key: IAT, value: count

	for IAT in IATLines:
		tmpList = []
		for key, time in appExecTime.items():
			if IAT > time:
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

	funcNum = 0
	for name, iat in actionIATdict.items():
		if iat <= config['total_run_time']*MILLISECONDS_PER_SEC:
			funcNum += funcsPerApp[name]


	print("Workload's estimated RPS: %d" % rps)
	print("Number of functions to be executed: %d" % funcNum)

	return (actionIATdict, appExecTime, funcsPerApp)

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
	appExecTime, funcsPerApp, _ = calAppExecTime(actionLines)
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

# Generate 1ms scale timeline
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

def splitDict(inputDict, chunks):
	cnt = 0
	ret = []
	reverse = False

	for i in range(chunks):
		ret.append(dict())

	for key, value in inputDict.items():
		idx = cnt % chunks
		ret[idx][key] = value

		if cnt == chunks - 1 and reverse == False:
			reverse = True
			continue

		if cnt == 0 and reverse == True:
			reverse = False
			continue

		if reverse == True:
			cnt -= 1
		else:
			cnt += 1

	return ret	# list of dictionaries


# Generate 1ms scale timeline. This function generate slow-starting workload
def invokeTimelineGenSlow(actionDict):
	# millisecond
	totalRunTime = config['total_run_time'] * MILLISECONDS_PER_SEC
	timelineFileName = "%s/funcTimeline_%i.csv" % (workloadDir, SAMPLE_NUM)
	# delayed start of functions
	delay = 40 * MILLISECONDS_PER_SEC
	# split actions into chunks
	chunks = 12
	invocations = 0
	appCol = []

	for key in actionDict:
		appCol.append(key)

	timeline = pd.DataFrame(columns=appCol)
	splitted = splitDict(actionDict, chunks)
	# print(splitted)

	for idx, chunk in enumerate(splitted):
		# print(idx * delay)
		for key, iat in chunk.items():
			data = np.zeros(totalRunTime, dtype=np.int8)
			for i in range(idx * delay, totalRunTime, iat):
				data[i] = 1
				invocations += 1
			data[0] = 0
			timeline[key] = data

	timeline.to_csv(timelineFileName, index=False)

	rps = invocations / config['total_run_time']
	print("Function timeline generation complete!")
	print("Estimated rps: %d" % rps)


# argument: name of successful workload
if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument("-th", "--threshold", type=int, help="runtime threshold for every functions")
	args = parser.parse_args()
	th = args.threshold

	if th != None:
		actionIATdict, appExecTime, funcsPerApp = mapActionandIATSame(workloadDir)
	else:
		actionIATdict, appExecTime, funcsPerApp = mapActionandIAT(workloadDir)

	writeMappingCSV(actionIATdict, appExecTime, funcsPerApp)
	# invokeTimelineGen(actionIATdict)
	invokeTimelineGenSlow(actionIATdict)