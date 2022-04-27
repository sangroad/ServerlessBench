from requests_futures.sessions import FuturesSession
import json
import argparse
import time
import threading
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
	
wskAuth = "23bc46b1-71f6-4ed5-8c54-816aa4f8c502:123zO3xZCLrMN6v2BKK1dXYFpXlPkccOFqm12CdAsMgRU4VrNZ9lyGVCGuMDGIwP"
auth = tuple(wskAuth.split(":"))

def runTrace(baseUrl):
	session = FuturesSession(max_workers=args.workers)
	startTime = time.time()	# microsecond scale
	action = "app0"
	url = baseUrl + action
	params = {}
	params['blocking'] = 'false'
	params['result'] = 'false'
	future = session.post(url, params=params, auth=auth, verify=False)
	endTime = time.time()
	response = future.result()
	print(endTime - startTime)

if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("--workers", default=5, type=int)
	parser.add_argument("--trace", type=str)
	parser.add_argument("--exectime", type=int)
	parser.add_argument("--controller_ip", type=str, default="10.150.3.42")

	args = parser.parse_args()

	baseUrl = "https://" + args.controller_ip + "/api/v1/namespaces/_/actions/"

	runTrace(baseUrl)