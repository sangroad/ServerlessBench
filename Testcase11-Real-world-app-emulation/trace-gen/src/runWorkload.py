import yaml
import os
import threading
import time
import re
import subprocess

SECONDS_OF_A_DAY = 3600*24
MILLISECONDS_PER_SEC = 1000

config = yaml.load(open(os.path.join(os.path.dirname(__file__),'config.yaml')), yaml.FullLoader)
SAMPLE_NUM = config['sample_number']
workloadDir = "../CSVs/%i" % SAMPLE_NUM
timelinePath = "%s/funcTimeline_%i.csv" % (workloadDir, SAMPLE_NUM)

def runWorkloadThreading(timeline, prevTime):
	curTime = time.time()
	# print("time: %.4f" % start)
	print(curTime - prevTime)

	threading.Timer(0.001, runWorkloadThreading, [timeline, curTime]).start()

def runWorkloadSleep(timeline):
	for line in timeline:
		start = time.time()

		if not '1' in line:
			continue
		else:
			line = line.replace(',', '')
			idx = [m.start() for m in re.finditer('1', line)]
			subprocess.run(["ls"])

			time.sleep(0.001)
			end = time.time()
			print("duration: %.5f" % (end - start))

		# time.sleep(0.001)
		# end = time.time()
		# print("duration: %.5f" % (end - start))


def readTimeline():
	timelineFile = open(timelinePath, "r")
	timeline = timelineFile.readlines()[1:]
	return timeline


if __name__ == '__main__':
	timeline = readTimeline()
	runWorkloadSleep(timeline)
	# runWorkloadThreading(timeline, time.time())