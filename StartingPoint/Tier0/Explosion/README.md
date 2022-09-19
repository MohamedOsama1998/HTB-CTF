# Explosion

---

## Setup

Connected to the VPN, spawned in the target machine, as a first step to make sure the target machine is alive I use a quit `ping` command in the terminal to make sure all is set and store the IP in an environment variable:

```shell
└─$ export IP=10.129.1.13
└─$ echo $IP
10.129.1.13

└─$ ping $IP
PING 10.129.1.13 (10.129.1.13) 56(84) bytes of data.
64 bytes from 10.129.1.13: icmp_seq=1 ttl=127 time=68.4 ms
64 bytes from 10.129.1.13: icmp_seq=2 ttl=127 time=68.6 ms
64 bytes from 10.129.1.13: icmp_seq=3 ttl=127 time=68.8 ms
64 bytes from 10.129.1.13: icmp_seq=4 ttl=127 time=68.6 ms
````

All is set!

---

## Enumeration

First, I run a scan on the target machine to identify open ports and running services that might be vulnerable using [nmap](https://nmap.org) with the following flags:
`-sV`: Determine running services/versions on open ports
`-sC`: Run default scripts
`-v`: Verbose output for more information about the scan
`-oN`: Write the output of the scan into a file

```shell
└─$ nmap -sV -sC -v -oN scan.nmap $IP

...

Nmap scan report for 10.129.1.13
Host is up (0.22s latency).
Not shown: 996 closed tcp ports (conn-refused)
PORT     STATE SERVICE       VERSION
135/tcp  open  msrpc         Microsoft Windows RPC
139/tcp  open  netbios-ssn   Microsoft Windows netbios-ssn
445/tcp  open  microsoft-ds?
3389/tcp open  ms-wbt-server Microsoft Terminal Services
```

Here we see the target machine is running a Microsoft Windows OS with RDP server on prt 3389, also later in the scan it shows the computer name is :`Explosion` and the DNS domain name is also `Explosion`, so I edited my `/etc/hosts` file and added this entry `10.129.1.13	explosion.htb`.

The target machine also seemingly runs Samba services which might be worth looking at early on for simple intel that could lead me somewhere

---

## Samba

I started with enumerating Samba shares anonymously with a blank password, see if anything interesting there but all I found was some default shares that are secured with administrator access, so I moved on to explore the RDP server.

```shell
└─$ smbclient -L $IP     
Password for [WORKGROUP\kali]:

        Sharename       Type      Comment
        ---------       ----      -------
        ADMIN$          Disk      Remote Admin
        C$              Disk      Default share
        IPC$            IPC       Remote IPC
```

---

## RDP

I started by trying to connect to the RDP server with the username I already know previously from the nmap scan `Explosion`, but a password was necessary so I couldn't get connection.

```shell
└─$ xfreerdp /v:$IP /u:Explosion    
[22:27:40:190] [20135:20136] [WARN][com.freerdp.crypto] - Certificate verification failure 'self signed certificate (18)' at stack position 0
[22:27:40:190] [20135:20136] [WARN][com.freerdp.crypto] - CN = Explosion
Password: 
[22:27:42:866] [20135:20136] [ERROR][com.freerdp.core] - transport_ssl_cb:freerdp_set_last_error_ex ERRCONNECT_PASSWORD_CERTAINLY_EXPIRED [0x0002000F]
[22:27:42:866] [20135:20136] [ERROR][com.freerdp.core.transport] - BIO_read returned an error: error:14094438:SSL routines:ssl3_read_bytes:tlsv1 alert internal error
```

I then started manually brute forcing common usernames to see if any of them is misconfigured and maybe I can login with a blank password, I used `Impacket: rdp_check.py` script and started testing usernames: `root`, `admin`, `Explosion`, `Administrator` and at last, the username `Administrator` with a blank password clicked!

```shell
└─$ python /opt/impacket/build/scripts-3.10/rdp_check.py Explosion/Administrator:@$IP
Impacket v0.10.1.dev1+20220720.103933.3c6713e3 - Copyright 2022 SecureAuth Corporation

Password:
[*] Access Granted
```

To connect to the RDP server I used `xfreerdp`:

```shell
└─$ xfreerdp /v:$IP /u:Administrator
````

and I'm in! I got an instance of the target machine running in a GUI window with `flag.txt` file on the Desktop:

![RDP Connection](https://imgur.com/gX10TLo.png)

---

## Blue Team Suggestions

- Administrator accounts must have a secure password! at least a password.