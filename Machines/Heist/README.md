# Heist

---

## Enumeration

nmap scan:

```bash
PORT      STATE SERVICE       VERSION
80/tcp    open  http          Microsoft IIS httpd 10.0
| http-title: Support Login Page
|_Requested resource was login.php
| http-cookie-flags: 
|   /: 
|     PHPSESSID: 
|_      httponly flag not set
|_http-server-header: Microsoft-IIS/10.0
| http-methods: 
|   Supported Methods: OPTIONS TRACE GET HEAD POST
|_  Potentially risky methods: TRACE
135/tcp   open  msrpc         Microsoft Windows RPC
445/tcp   open  microsoft-ds?
5985/tcp  open  http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-title: Not Found
|_http-server-header: Microsoft-HTTPAPI/2.0
49669/tcp open  msrpc         Microsoft Windows RPC
Service Info: OS: Windows; CPE: cpe:/o:microsoft:windows

Host script results:
| smb2-security-mode: 
|   311: 
|_    Message signing enabled but not required
|_clock-skew: 28s
| smb2-time: 
|   date: 2022-11-08T05:30:00
|_  start_date: N/A
```

### SMB

- anon login denied, need auth
- After Web, found Hazard:stealth1agent SMB creds
- Has READ access on IPC$

### Web

- Logged in as Guest, found users Hazard, Support Admin
- got file config.txt
- Cracked the secret: stealth1agent

### Win-RM

- Nothing initially, no creds worked

### Impacket-lookupsid.py

- Found other users to spray:

```
500: SUPPORTDESK\Administrator (SidTypeUser)
501: SUPPORTDESK\Guest (SidTypeUser)
503: SUPPORTDESK\DefaultAccount (SidTypeUser)
504: SUPPORTDESK\WDAGUtilityAccount (SidTypeUser)
513: SUPPORTDESK\None (SidTypeGroup)
1008: SUPPORTDESK\Hazard (SidTypeUser)
1009: SUPPORTDESK\support (SidTypeUser)
1012: SUPPORTDESK\Chase (SidTypeUser)
1013: SUPPORTDESK\Jason (SidTypeUser)
```

- Found creds using metasploit aux/scanner/winrm/winrm_login

```
Chase:Q4)sJu\Y8qz*A3?d
```

- Used these creds to get evil-winrm connection, got user.txt

---

## PrivEsc

