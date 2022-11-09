# Bastion

---

## Enumeration

nmap:

```bash
PORT      STATE SERVICE      VERSION
22/tcp    open  ssh          OpenSSH for_Windows_7.9 (protocol 2.0)
| ssh-hostkey: 
|   2048 3a56ae753c780ec8564dcb1c22bf458a (RSA)
|   256 cc2e56ab1997d5bb03fb82cd63da6801 (ECDSA)
|_  256 935f5daaca9f53e7f282e664a8a3a018 (ED25519)
135/tcp   open  msrpc        Microsoft Windows RPC
139/tcp   open  netbios-ssn  Microsoft Windows netbios-ssn
445/tcp   open  microsoft-ds Windows Server 2016 Standard 14393 microsoft-ds
5985/tcp  open  http         Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-title: Not Found
|_http-server-header: Microsoft-HTTPAPI/2.0
47001/tcp open  http         Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-server-header: Microsoft-HTTPAPI/2.0
|_http-title: Not Found
49664/tcp open  msrpc        Microsoft Windows RPC
49665/tcp open  msrpc        Microsoft Windows RPC
49666/tcp open  msrpc        Microsoft Windows RPC
49667/tcp open  msrpc        Microsoft Windows RPC
49668/tcp open  msrpc        Microsoft Windows RPC
49669/tcp open  msrpc        Microsoft Windows RPC
49670/tcp open  msrpc        Microsoft Windows RPC
```

## Samba

- Found share "Backups" with null authentication
- Mounted it to /smb: mount -t cifs //$IP/Backups /smb
- Machine name: L4mpje-PC (The backup), Copmuter name: BASTION
- Found 'vhd' VirtualHardDrive, mount it using guestmount

```bash
guestmount --add 9b9cfbc4-369e-11e9-a17c-806e6f6e6963.vhd --inspector --ro -v mount-to-path
```

- got SYS and SYSTEM in C:\Windows\System32\Config and got hashes using impacket-secretsdump
- Crackstation got L4. password: bureaulampje
- Logged in and got user.txt

---

## PrivEsc

- Found mRemoteNG
- https://github.com/haseebT/mRemoteNG-Decrypt
- got config file from C:\Users\UName\AppData\Roamin\mRemoteNG
- Creds:

L4mpje:bureaulampje
Administrator:thXLHM96BeKL0ER2

- SSH As Administrator
- get root.txt!

---

