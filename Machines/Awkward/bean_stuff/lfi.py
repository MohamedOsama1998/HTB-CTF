#!/usr/bin/env python3

import requests, sys

url = 'http://hat-valley.htb'
api = '/api/all-leave'

cookie = sys.argv[1]

r = requests.get(url + api, cookies={
	"token":cookie
	})

print(r.text)