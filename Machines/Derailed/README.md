# Derailed

---

## Enumeration

- IP: `10.10.11.190`
- nmap:

```
PORT     STATE SERVICE VERSION
22/tcp   open  ssh     OpenSSH 8.4p1 Debian 5+deb11u1 (protocol 2.0)
| ssh-hostkey: 
|   3072 1623b09ade0e3492cb2b18170ff27b1a (RSA)
|   256 50445e886b3e4b5bf9341dede52d91df (ECDSA)
|_  256 0abd9223df44026f278da6abb4077837 (ED25519)
3000/tcp open  http    nginx 1.18.0
| http-methods: 
|_  Supported Methods: GET HEAD POST OPTIONS
|_http-favicon: Unknown favicon MD5: D41D8CD98F00B204E9800998ECF8427E
|_http-title: derailed.htb
|_http-server-header: nginx/1.18.0
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel
```

- Website reveals domain name: `derailed.htb`: Added to `/etc/hosts`
- On submitting note as guest, got to page of the note: `http://derailed.htb:3000/clipnotes/109`, started fuzzing for other notes
- found note `001` by user `alice`.
- The web app is vulnerable to timing attack on login submit, it might seem like this:

```
if username exist:
	check password:
else:
	return false
```

- I can enumerate some usernames but only `alice` and the user `test` I created exist, so I might need to somehow impersonate `alice` to access `/administration`.

---

## Privilege Escalation

- 