#!/usr/bin/env python3

words = []

with open('wordlist.txt', 'r') as file:
	for word in file.readlines():
		if word[2] == 'o' and word[4] == 'k' and 'f' in word:
			words.append(word.strip())

print(words)