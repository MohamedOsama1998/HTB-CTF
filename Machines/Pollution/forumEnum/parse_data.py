#!/usr/bin/env python3

from re import findall
import base64, html

with open('proxy_history.txt', 'r') as file:
	data = file.read()

b64_data = findall(r'base64="true"><!\[CDATA\[(.*?)\]\]', data)

for i in b64_data:
	print()
	print(base64.b64decode(i).decode('utf-8'))
	print('====================================================')
	print('====================================================')
	print()

