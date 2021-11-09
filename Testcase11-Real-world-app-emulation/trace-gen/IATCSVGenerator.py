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

import random
import os
import yaml
import utils

SECONDS_OF_A_DAY = 3600*24

config = yaml.load(open(os.path.join(os.path.dirname(__file__),'config.yaml')), yaml.FullLoader)
SAMPLE_NUM = config['sample_number']

def pickRandAvgIAT():
    filename = os.path.join(os.path.dirname(__file__),'invokesCDF.csv')
    invokeTime = utils.getRandValueRefByCDF(filename)
    # second scale
    IAT = SECONDS_OF_A_DAY / invokeTime
    return IAT

def sampleActionIATCSVGen(appNum):
    outfile = open("possibleIATs.csv", "w")
    outfile.write("IAT\n")

    for i in range(appNum):
        IAT = pickRandAvgIAT()
        outfile.write("%0.3f\n" % (IAT))

if __name__ == '__main__':
    sampleActionIATCSVGen(SAMPLE_NUM)
