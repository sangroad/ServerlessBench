import csv
import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

MILLISECONDS_PER_SECOND = 1000

def invocation_dist_1ms(path, sampleNum):
	reader = csv.DictReader(open(os.path.join(path, "appandIATMap.csv")))
	appDict = {}
	for row in reader:
		appDict[row['appName']] = row['execTime']

	tmp = "funcTimeline_" + sampleNum + ".csv"
	timeline = pd.read_csv(os.path.join(path, tmp))

	for col in timeline:
		running = False
		timeCnt = 0
		appName = col
		execTime = int(appDict[appName])
		for idx, val in enumerate(timeline[col].values):
			if running == True:
				if timeCnt < execTime:
					timeline[col].values[idx] = 1
					timeCnt += 1
				else:
					running = False
					timeCnt = 0
			if val == 1:
				running = True
				continue
			# print(timeline[col].values)

	timeline["sum"] = timeline.sum(axis=1)
	plotData = timeline["sum"]
	plotData.to_csv(os.path.join(path, "invocationDist.csv"), index=False)
	# print(plotData)

# 1초 안에 몇 개의 function이 실행되었는지, 몇번씩 실행되었는지 확인하면 될듯?
def invocation_dist_1s(path, sampleNum):
	reader = csv.DictReader(open(os.path.join(path, "appandIATMap.csv")))
	appDict = {}
	for row in reader:
		appDict[row['appName']] = row['execTime']

	tmp = "funcTimeline_" + sampleNum + ".csv"
	timeline = pd.read_csv(os.path.join(path, tmp))

	totalInv = pd.DataFrame()
	for col in timeline:
		invCnt = 0
		appName = col
		# execTime = int(appDict[appName])
		invPerSec = []
		for idx, val in enumerate(timeline[col].values):
			if val == 1:
				invCnt += 1
			if idx % MILLISECONDS_PER_SECOND == 0:
				invPerSec.append(invCnt)
				invCnt = 0
		# totalInv.append(invPerSec)
		totalInv[appName] = invPerSec

	totalInv["sum"] = totalInv.sum(axis=1)
	plotData = totalInv["sum"]
	plotData.to_csv(os.path.join(path, "invocationDist.csv"), index=False)
	# plotData = pd.DataFrame(totalInv, dtype=int)
	# plotData.to_csv(os.path.join(path, "invocationDist.csv"), index=False)
	

def drawPlot(path):
	rawData = pd.read_csv(os.path.join(path, "invocationDist.csv")).values
	# runtime = len(y_values)
	# x_values = [0, 0.25*runtime, 0.5*runtime, 0.75*runtime, 1*runtime]
	plt.plot(rawData)
	plt.savefig(os.path.join(path, "dist.png"))


if __name__ == "__main__":
	csvPath = "../CSVs"
	workload = "350"
	workloadPath = os.path.join(csvPath, workload)
	invocation_dist_1s(workloadPath, workload)
	drawPlot(workloadPath)