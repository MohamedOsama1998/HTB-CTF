# Preignition

---

## Setup

Connected to the VPN, spawned in the target machine, as a first step to make sure the target machine is alive I use a quit `ping` command in the terminal to make sure all is set and store the IP in an environment variable:

```shell
└─$ export IP=10.129.125.127
└─$ echo $IP
10.129.125.127

└─$ ping $IP                                                                          
PING 10.129.125.127 (10.129.125.127) 56(84) bytes of data.
64 bytes from 10.129.125.127: icmp_seq=1 ttl=63 time=68.6 ms
64 bytes from 10.129.125.127: icmp_seq=2 ttl=63 time=68.5 ms
64 bytes from 10.129.125.127: icmp_seq=3 ttl=63 time=68.5 ms
64 bytes from 10.129.125.127: icmp_seq=4 ttl=63 time=68.4 ms
````

All is set!

---

## Enumeration

First, I ran a scan on the target machine to identify open ports and running services that might be vulnerable using [nmap](https://nmap.org) with the following flags:
`-sV`: Determine running services/versions on open ports
`-sC`: Run default scripts
`-v`: Verbose output for more information about the scan
`-oN`: Write the output of the scan into a file

```shell
└─$ nmap -sV -sC -v -oN scan.nmap $IP

...

Nmap scan report for 10.129.125.127
Host is up (0.14s latency).
Not shown: 999 closed tcp ports (conn-refused)
PORT   STATE SERVICE VERSION
80/tcp open  http    nginx 1.14.2
| http-methods: 
|_  Supported Methods: GET HEAD
|_http-server-header: nginx/1.14.2
|_http-title: Welcome to nginx!
```

looks like it's just a `nginx version 1.14.2` web server running on HTTP port 80, so I added an entry in `/etc/hosts` file: `10.129.125.127	preignition.htb`

---

## Dir Busting

I always start a `gobuster` enumeration on a web server whenever I start a CTF challenge to see if there are hidden pages while I work on other stuff, but this time I immediately got a result which looked interested:

```shell
└─$ gobuster dir -u http://preignition.htb -w /usr/share/wordlists/dirbuster/directory-list-2.3-small.txt -x php
===============================================================
Gobuster v3.1.0
by OJ Reeves (@TheColonial) & Christian Mehlmauer (@firefart)
===============================================================
[+] Url:                     http://preignition.htb
[+] Method:                  GET
[+] Threads:                 10
[+] Wordlist:                /usr/share/wordlists/dirbuster/directory-list-2.3-small.txt
[+] Negative Status codes:   404
[+] User Agent:              gobuster/3.1.0
[+] Extensions:              php
[+] Timeout:                 10s
===============================================================
2022/09/18 23:07:22 Starting gobuster in directory enumeration mode
===============================================================
/admin.php            (Status: 200) [Size: 999]
```

so I went to firefox and navigated to `http://preignition.htb/admin.php` and was greeted with a login page, entered the classic `admin, admin` username and password respectively and it worked! and I immediately got the flag.

![Login Page](https://imgur.com/i0iqZvv.png)

---

# Tasks & Answers

**Task 1**: Directory Brute-forcing is a technique used to check a lot of paths on a web server to find hidden pages. Which is another name for this? (i) Local File Inclusion, (ii) dir busting, (iii) hash cracking.
> Dir busting

**Task 2**: What switch do we use for nmap's scan to specify that we want to perform version detection
> -sV

**Task 3**: What does Nmap report is the service identified as running on port 80/tcp?
> HTTP

**Task 4**: What server name and version of service is running on port 80/tcp?
> nginx 1.14.2

**Task 5**: What switch do we use to specify to Gobuster we want to perform dir busting specifically?
> dir

**Task 6**: When using gobuster to dir bust, what switch do we add to make sure it finds PHP pages?
> -x php

**Task 7**: What page is found during our dir busting activities?
> admin.php

**Task 8**: What is the HTTP status code reported by Gobuster for the discovered page?
> 200

**FLAG**: 
> *******************************3

---

## Blue Team Suggestions

- Secure the administrator user with a more secure password.
- Secure traffic requesting `admin.php` page.