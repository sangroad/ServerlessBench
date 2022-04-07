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

import os
import yaml
import utils
import sys

SECONDS_OF_A_DAY = 3600*24
MILLISECONDS_OF_A_DAY = SECONDS_OF_A_DAY * 1000

config = yaml.load(open(os.path.join(os.path.dirname(__file__),'config.yaml')), yaml.FullLoader)
SAMPLE_NUM = config['sample_number']
workloadDir = "../CSVs/%i" % SAMPLE_NUM

altTh = None
padding = None

# Pick IAT randomly from invocation CDF
def pickRandAvgIAT(th):
	filename = os.path.join(os.path.dirname(__file__),'../CSVs/invokesCDF.csv')
	invokeTime = utils.getRandValueRefByCDF(filename)
	# millisecond scale
	IAT = MILLISECONDS_OF_A_DAY / invokeTime

	# second scale
	# IAT = SECONDS_OF_A_DAY / invokeTime
	if th != None:
		global altTh
		if IAT < th:
			IAT = altTh
			altTh += padding

	return IAT

# Generate csv file contains IATs
def sampleActionIATCSVGen(appNum, th):
	outfile = open("%s/possibleIATs.csv" % workloadDir, "w")
	outfile.write("IAT\n")

	for i in range(appNum):
		IAT = round(pickRandAvgIAT(th))
		outfile.write("%d\n" % (IAT))

if __name__ == '__main__':
	argument = sys.argv
	del argument[0]
	th = None

	if len(argument) != 0:
		th = int(argument[0])
		padding = th * 0.1
		altTh = th + padding

	sampleActionIATCSVGen(SAMPLE_NUM, th)
