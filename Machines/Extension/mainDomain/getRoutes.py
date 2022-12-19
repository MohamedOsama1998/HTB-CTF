#!/usr/bin/env python3

import re, requests

url = "http://snippet.htb"

r = requests.get(url)
data = re.findall(r"const Ziggy = {(.+?)};", r.text)[0]
print(f"{{{data}}}")