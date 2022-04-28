import logging
from requests_futures.sessions import FuturesSession
import json
import argparse
import time
import threading
import yaml
import os
import urllib3
import pandas as pd
import shutil
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
logging.basicConfig(level=logging.INFO)

MICROSECONDS_PER_MILLISECONDS = 1000
MILLISECONDS_PER_SECONDS = 1000

config = yaml.load(open(os.path.join(os.path.dirname(__file__),'config.yaml')), yaml.FullLoader)
SAMPLE_NUM = config["sample_number"]
	
wskAuth = "23bc46b1-71f6-4ed5-8c54-816aa4f8c502:123zO3xZCLrMN6v2BKK1dXYFpXlPkccOFqm12CdAsMgRU4VrNZ9lyGVCGuMDGIwP"
auth = tuple(wskAuth.split(":"))

def writeWorkloadNametoPICKME(successDir, pickmePath):
	sshpass = "sshpass ssh caslab@10.150.21.198 "
	echo = "\"echo " + successDir + " > " + pickmePath + "/current_workload\""
	cmd = sshpass + echo
	print(cmd)
	os.system(cmd)

def moveWorkload(workloadDir, runtime):
	targetDir = "../CSVs/success/"
	mapFilePath = os.path.join(workloadDir, "appandIATMap.csv")
	infoFilePath = os.path.join(workloadDir, "appComputeInfo.csv")
	functionFilePath = os.path.join(workloadDir, "funcTimeline.json")

	with open(functionFilePath, "r") as jsonFile:
		invokeInfo = json.load(jsonFile)
		rps = round(len(invokeInfo) / runtime)

	mapFile = pd.read_csv(mapFilePath)
	infoFile = pd.read_csv(infoFilePath)

	smallestIAT = mapFile["IAT"][0]
	totalFuncs = len(infoFile)

	numApps = workloadDir.split("/")[-1]

	newDir = str(rps) + "_" + numApps + "_" + str(smallestIAT) + "_" + str(totalFuncs) + "_" + str(runtime)
	targetDir += newDir
	shutil.copytree(workloadDir, targetDir)

	return targetDir

def endOfTrace(baseUrl):
	session = FuturesSession()
	url = baseUrl + "func-------"
	params = {
		"blocking": "false",
		"result": "false"
	}
	future = session.post(url, params=params, auth=auth, verify=False)

def responseHook(resp, *args, **kwargs):
	resp.data = resp.json()
	if "error" in resp.data:
		logging.error("Response error from openwhisk")

def allocTrace(trace, numWorkers):
	with open(trace, "r") as jsonFile:
		invokeInfo = json.load(jsonFile)

	workers = {}
	for i in range(0, numWorkers):
		workers[i] = []

	idx = 0
	for func in invokeInfo:
		workers[idx].append(func)
		idx = (idx + 1) % numWorkers

	return workers

def runTrace(baseUrl, workerTrace, execTime):
	session = FuturesSession(max_workers=20)
	startTime = time.time()	# second scale

	invCnt = 0
	for action in workerTrace:
		curTime = time.time() - startTime

		if curTime > execTime:
			break

		appName = action['appName']
		invokeTime = action['startTime'] / MILLISECONDS_PER_SECONDS
		waitTime = invokeTime - curTime

		if waitTime > 0:
			time.sleep(waitTime)	# sleep in us scale
		else:
			logging.warning("Invocation delayed for %.10fs" % (-waitTime))

		url = baseUrl + appName
		params = {}
		params['blocking'] = 'false'
		params['result'] = 'false'

		future = session.post(url, params=params, auth=auth, verify=False, hooks={
			"response": responseHook
		})
		invCnt += 1
		if invCnt % 50 == 0:
			logging.info(url)


if __name__ == "__main__":
	traceFileName = "funcTimeline.json"
	defaultTracePath = "../CSVs/%i" % SAMPLE_NUM
	defaultRuntime = config['total_run_time']

	parser = argparse.ArgumentParser()
	parser.add_argument("--num_workers", type=int, default=5)
	parser.add_argument("--trace", type=str, default=defaultTracePath)
	parser.add_argument("--exectime", type=int, default=defaultRuntime)
	parser.add_argument("--controller_ip", type=str, default="10.150.21.197")

	args = parser.parse_args()

	baseUrl = "https://" + args.controller_ip + "/api/v1/namespaces/_/actions/"
	tracePath = os.path.join(args.trace, traceFileName)

	workers = allocTrace(tracePath, args.num_workers)

	threads = []
	for perWorkerTrace in workers.values():
		t = threading.Thread(target=runTrace, kwargs={
			"baseUrl": baseUrl,
			"workerTrace": perWorkerTrace,
			"execTime": args.exectime * MILLISECONDS_PER_SECONDS
		})
		threads.append(t)

	logging.info("--------- Experiment start ---------")
	for thread in threads:
		thread.start()

	for thread in threads:
		thread.join()
	endOfTrace(baseUrl)
	logging.info("--------- Experiment end ---------")

	successDir = moveWorkload(args.trace, args.exectime)
	writeWorkloadNametoPICKME(successDir, "/home/caslab/workspace/PICKME/data")