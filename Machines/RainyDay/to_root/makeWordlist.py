#!/usr/bin/env python3

import string

chars = string.printable.strip()
base = "𐍈𐍈𐍈𐍈𐍈𐍈𐍈𐍈𐍈𐍈𐍈𐍈𐍈𐍈𐍈aaH34vyR41n"
# password to put: 𐍈𐍈𐍈𐍈𐍈𐍈𐍈𐍈𐍈𐍈𐍈𐍈𐍈𐍈𐍈aa

for char in chars:
	print(base + char)
