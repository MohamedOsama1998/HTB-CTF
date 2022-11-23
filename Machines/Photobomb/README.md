# Photobomb

---

## Setup

Spawned in the machine as always, got the IP and stored it in an environment variable in case I lose it -as always-

```bash
export IP=10.10.11.174
echo $IP

10.10.11.174
```

and to make sure everything is working alright and the target machine is up and running, we can use `ping` to make sure it's alive.

```bash
ping $IP

PING 10.10.11.174 (10.10.11.174) 56(84) bytes of data.
64 bytes from 10.10.11.174: icmp_seq=1 ttl=63 time=69.3 ms
64 bytes from 10.10.11.174: icmp_seq=2 ttl=63 time=68.1 ms
64 bytes from 10.10.11.174: icmp_seq=3 ttl=63 time=67.9 ms
64 bytes from 10.10.11.174: icmp_seq=4 ttl=63 time=70.4 ms
```

---

## Enumeration

First step after spawning in the target machine and connected to the VPN, I start an [`nmap`](https://nmap.org) scan to determine open ports and running services and may be vulnerable using the following flags:

`-sV`: Determine running services/versions on open ports
`-sC`: Run default scripts
`-p-`: Scan all possible ports
`-v`: Verbose output for more information about the scan
`-oN`: Write the output of the scan into a file

```bash
nmap -sV -sC -p- -v -oN scan.nmap $IP
```

After the scan is complete, here's the result:

```bash
TODO
```

---

## TODO

View source -> get auth
Download image -> edit filetype -> png;REVSHELL -> USER!

https://book.hacktricks.xyz/linux-hardening/privilege-escalation -> LD_PRELOAD -> shell.c shell.so in /tmp -> sudo -u root LD_PRELOAD=/tmp/shell.so /opt/cleanup.sh -> ROOTED

