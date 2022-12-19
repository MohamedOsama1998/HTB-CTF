#!/usr/bin/env python3

import re, json

with open("raw_users.json", 'r') as file:
	users = json.loads(file.readline())

for user in users:
	# Print email:password format to crack
	# print(f"{user['email']}:{user['password']}")

	# Check for same password usage that was cracked
	if user['password'] == 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f':
		print(f'{user["email"]} have the same password, Their role is: {user["user_type"]}')

	# Print jean's hash
	# if user['name'] == 'Jean Castux':
	# 	print(user['password'])