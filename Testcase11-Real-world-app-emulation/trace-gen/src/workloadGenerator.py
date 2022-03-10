import os
import yaml

config = yaml.load(open(os.path.join(os.path.dirname(__file__),'config.yaml')), yaml.FullLoader)
SAMPLE_NUM = config['sample_number']
workloadDir = "../CSVs/%i" % SAMPLE_NUM
computeInfoFile = "%s/appComputeInfo.csv" % workloadDir

def refractorAppComputeInfo():
	infoFile = open(computeInfoFile, "r")
	computeInfo = infoFile.readlines()[1:]
	prevName = None
	appInfo = {}
	chainLen = 0

	for line in computeInfo:
		splitted = line.rstrip().split(",")
		appName = splitted[0]
		mem = splitted[2]
		execTime = splitted[3]

		if appName != prevName:
			chainLen = 0
			appInfo[appName] = []
			prevName = appName

		chainLen += 1
		appInfo[appName].append([mem, execTime])

	return appInfo

# exec time: ms scale
# specify execTime in update phase
def actionWskGen(chainList):

	for key, val in chainList.items():
		appName = key
		sequenceID = key[3:]
		functionID = 0
		funcChainStr = ""

		for info in val:
			mem = info[0]
			execTime = info[1]

			if int(mem) < 128:
				mem = "128"
			if int(mem) > 512:
				mem = "512"

			# cmd = "./action_update.sh %s %s %s %s" % (sequenceID, functionID, execTime, mem)
			cmd = "./action_update.sh %s %s %s %s" % (str(sequenceID).zfill(3), str(functionID).zfill(3), execTime, mem)
			print(cmd)
			r = os.popen(cmd)
			r.read()
			funcName = "func%s-%s" % (str(sequenceID).zfill(3), str(functionID).zfill(3))
			funcChainStr = funcChainStr + funcName + ","
			functionID += 1

		funcChainStr = funcChainStr[:-1]
		cmd = "wsk -i action update %s --sequence %s" % (appName, funcChainStr)
		print(cmd)
		r = os.popen(cmd)
		r.read()

	# func------- means the end of benchmark
	cmd = "./action_update.sh %s %s %s %s" % ("---", "---", 1, 128)
	r = os.popen(cmd)
	r.read()
	
	print("Workload creation complete")


if __name__ == '__main__':
	seqInfo = refractorAppComputeInfo()
	actionWskGen(seqInfo)