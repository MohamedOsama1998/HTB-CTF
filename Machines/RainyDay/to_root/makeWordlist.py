#!/usr/bin/env python3

import string

chars = string.printable.strip()
base = "ðððððððððððððððaaH34vyR41n"
# password to put: ðððððððððððððððaa

for char in chars:
	print(base + char)
