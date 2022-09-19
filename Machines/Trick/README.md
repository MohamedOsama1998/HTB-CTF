# Trick

## Setup

Spawned in the machine as always, got the IP and stored it in an environment variable in case I lose it -as always-

```shell
└─$ export IP=10.10.11.166
└─$ echo $IP
10.10.11.166
```

and to make sure everything is working alright and the target machine is up and running, we can use `ping` to make sure it's alive.

```shell
└─$ ping $IP
PING 10.10.11.166 (10.10.11.166) 56(84) bytes of data.
64 bytes from 10.10.11.166: icmp_seq=1 ttl=63 time=69.3 ms
64 bytes from 10.10.11.166: icmp_seq=2 ttl=63 time=68.1 ms
64 bytes from 10.10.11.166: icmp_seq=3 ttl=63 time=67.9 ms
64 bytes from 10.10.11.166: icmp_seq=4 ttl=63 time=70.4 ms
```

---

## Scan

First step after spawning in the target machine and connected to the VPN, I start an [`nmap`](https://nmap.org) scan to determine open ports and running services and may be vulnerable using the following flags:

`-sV`: Determine running services/versions on open ports
`-sC`: Run default scripts
`-p-`: Scan all possible ports
`-v`: Verbose output for more information about the scan
`-oN`: Write the output of the scan into a file

``` shell
└─$ nmap -sV -sC -p- -v -oN scan.nmap $IP
```

After the scan is complete, here's the result:

```shell
Nmap scan report for 10.10.11.166
Host is up (0.17s latency).
Not shown: 65531 closed tcp ports (conn-refused)
PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 7.9p1 Debian 10+deb10u2 (protocol 2.0)
| ssh-hostkey: 
|   2048 61:ff:29:3b:36:bd:9d:ac:fb:de:1f:56:88:4c:ae:2d (RSA)
|   256 9e:cd:f2:40:61:96:ea:21:a6:ce:26:02:af:75:9a:78 (ECDSA)
|_  256 72:93:f9:11:58:de:34:ad:12:b5:4b:4a:73:64:b9:70 (ED25519)
25/tcp open  smtp    Postfix smtpd
|_smtp-commands: debian.localdomain, PIPELINING, SIZE 10240000, VRFY, ETRN, STARTTLS, ENHANCEDSTATUSCODES, 8BITMIME, DSN, SMTPUTF8, CHUNKING
53/tcp open  domain  ISC BIND 9.11.5-P4-5.1+deb10u7 (Debian Linux)
| dns-nsid: 
|_  bind.version: 9.11.5-P4-5.1+deb10u7-Debian
80/tcp open  http    nginx 1.14.2
|_http-title: Coming Soon - Start Bootstrap Theme
|_http-favicon: Unknown favicon MD5: 556F31ACD686989B1AFCF382C05846AA
| http-methods: 
|_  Supported Methods: GET HEAD
|_http-server-header: nginx/1.14.2
Service Info: Host:  debian.localdomain; OS: Linux; CPE: cpe:/o:linux:linux_kernel
```

I also added `trick.htb` to my local dns `/etc/hosts`:

```
10.10.11.166	trick.htb
```

---

## Poking Around

### SMTP Enumeration

After reading through the scanning process, I started playing with port 25 running SMTP service, tried to enumerate its users using `smtp-user-snum`, `telnet` using `VRFY` command, but after few minutes all I know is that there's `root` user which looks like to be the target user. However, I didn't get to anything useful in this step.

I then tried submitting the email form and started sniffing the traffic on `tun0` interface to see if I can capture any SMTP packets but I got none. At this point I decided to look somewhere else for a breach, since I spent too much time on this area.

### DNS Enumeration

Next step I tried to enumerate DNS using `dig`:

```shell
└─$ dig axfr trick.htb @trick.htb

; <<>> DiG 9.18.1-1-Debian <<>> axfr trick.htb @trick.htb
;; global options: +cmd
trick.htb.              604800  IN      SOA     trick.htb. root.trick.htb. 5 604800 86400 2419200 604800
trick.htb.              604800  IN      NS      trick.htb.
trick.htb.              604800  IN      A       127.0.0.1
trick.htb.              604800  IN      AAAA    ::1
preprod-payroll.trick.htb. 604800 IN    CNAME   trick.htb.
trick.htb.              604800  IN      SOA     trick.htb. root.trick.htb. 5 604800 86400 2419200 604800
```

After finding out about `preprod-payroll.trick.htb.` I added it to the entries at hosts file:

```
10.10.11.166	trick.htb, preprod-payroll.trick.htb.
```

I then went ahead and openned my browser and headed to `preprod-payroll.trick.htb.`, and was greeted with an admin login page, I started submitting some SQL Injection queries and eventually it worked! `admin' or '1'='1` seemed to log me in to the administrator account.

After navigating through the website I found an `edit account` functionality which lead me to know the password of the admin which is `SuperGucciRainbowCake`.

