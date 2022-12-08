# BackendTwo

---

## Enumeration

- nmap TCP scan:

```
22/tcp open  ssh     OpenSSH 8.2p1 Ubuntu 4ubuntu0.4 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   3072 ea8421a3224a7df9b525517983a4f5f2 (RSA)
|   256 b8399ef488beaa01732d10fb447f8461 (ECDSA)
|_  256 2221e9f485908745161f733641ee3b32 (ED25519)
80/tcp open  http    uvicorn
```

- Enumerated users, found a bunch
- Found a register/login API, registered a user and got access token
- Token can be used in `Authorization: Bearer <TOKEN>` header
- Password change API is vulnerable to mass assignment

---

## Foothold

- After changing my user to a superuser, I got the user flag
- Used `/file` API call to read local files
- With this LFI I read the application source code and by getting `/proc/self/environ`, i got the `API_KEY` which is the JWT secret key
- `API_KEY=68b329da9893e34099c7d8ad5cb9c940`
- Updated `user.py` to plant a backdoor there to get a revshell on port 9000

```bash
└─$ nc -lnvp 9000
listening on [any] 9000 ...
connect to [10.10.16.4] from (UNKNOWN) [10.10.11.162] 41348
bash: cannot set terminal process group (685): Inappropriate ioctl for device
bash: no job control in this shell
To run a command as administrator (user "root"), use "sudo <command>".
See "man sudo_root" for details.

htb@BackendTwo:~$
```

---


## PrivEsc

- pw: `1qaz2wsx_htb!`
- Wordle brute-force??
- Got the words from `/etc/pam.d/sudo` found a `.so` file for this wordle, and got the wordlist used in `/opt/.words`
- with the previous password `sudo su`, 