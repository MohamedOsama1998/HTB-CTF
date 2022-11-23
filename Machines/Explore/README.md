# Explore

---

## Enumeration

- Started full port scan using nmap, found these open ports:

```bash
nmap -p- -oN port_scan.nmap -v $IP --min-rate=5000
##################################################
PORT      STATE    SERVICE
2222/tcp  open     EtherNetIP-1
5555/tcp  filtered freeciv
37479/tcp open     unknown
42135/tcp open     unknown
59777/tcp open     unknown
```

- Started service enumeration using nmap on the previously found open ports:

```bash
nmap -p 2222,5555,37479,42135,59777 -sC -sV -oN scan.nmap -v $IP
##################################################

PORT      STATE    SERVICE VERSION
2222/tcp  open     ssh     (protocol 2.0)
| fingerprint-strings: 
|   NULL: 
|_    SSH-2.0-SSH Server - Banana Studio
| ssh-hostkey: 
|_  2048 7190e3a7c95d836634883debb4c788fb (RSA)
5555/tcp  filtered freeciv
37479/tcp open     unknown
| fingerprint-strings: 
|   GenericLines: 
|     HTTP/1.0 400 Bad Request
|     Date: Tue, 08 Nov 2022 04:07:26 GMT
|     Content-Length: 22
|     Content-Type: text/plain; charset=US-ASCII
|     Connection: Close
|     Invalid request line:
|   GetRequest: 
|     HTTP/1.1 412 Precondition Failed
|     Date: Tue, 08 Nov 2022 04:07:26 GMT
|     Content-Length: 0
|   HTTPOptions: 
|     HTTP/1.0 501 Not Implemented
|     Date: Tue, 08 Nov 2022 04:07:31 GMT
|     Content-Length: 29
|     Content-Type: text/plain; charset=US-ASCII
|     Connection: Close
|     Method not supported: OPTIONS
|   Help: 
|     HTTP/1.0 400 Bad Request
|     Date: Tue, 08 Nov 2022 04:07:48 GMT
|     Content-Length: 26
|     Content-Type: text/plain; charset=US-ASCII
|     Connection: Close
|     Invalid request line: HELP
|   RTSPRequest: 
|     HTTP/1.0 400 Bad Request
|     Date: Tue, 08 Nov 2022 04:07:31 GMT
|     Content-Length: 39
|     Content-Type: text/plain; charset=US-ASCII
|     Connection: Close
|     valid protocol version: RTSP/1.0
|   SSLSessionReq: 
|     HTTP/1.0 400 Bad Request
|     Date: Tue, 08 Nov 2022 04:07:48 GMT
|     Content-Length: 73
|     Content-Type: text/plain; charset=US-ASCII
|     Connection: Close
|     Invalid request line: 
|     ?G???,???`~?
|     ??{????w????<=?o?
|   TLSSessionReq: 
|     HTTP/1.0 400 Bad Request
|     Date: Tue, 08 Nov 2022 04:07:49 GMT
|     Content-Length: 71
|     Content-Type: text/plain; charset=US-ASCII
|     Connection: Close
|     Invalid request line: 
|     ??random1random2random3random4
|   TerminalServerCookie: 
|     HTTP/1.0 400 Bad Request
|     Date: Tue, 08 Nov 2022 04:07:49 GMT
|     Content-Length: 54
|     Content-Type: text/plain; charset=US-ASCII
|     Connection: Close
|     Invalid request line: 
|_    Cookie: mstshash=nmap
42135/tcp open     http    ES File Explorer Name Response httpd
|_http-title: Site doesnt have a title (text/html).
59777/tcp open     http    Bukkit JSONAPI httpd for Minecraft game server 3.6.0 or older
|_http-title: Site doesnt have a title (text/plain).
```

- port 59777 vulnerability: https://www.exploit-db.com/exploits/50070

1. modified the script and ran it, found in exploit.py
2. got creds.jpg
3. logged in as kristi

---

## PrivEsc

1. forwarded port 5555 to the attacking machine
2. used 'adb' and connected the device
3. adb -s localhost:5555 shell
4. su ---> ROOT!
5. root flag in data/root.txt

---
