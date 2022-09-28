# Base

---

## Setup

Connected to the VPN, spawned in the target machine, as a first step to make sure the target machine is alive I use a quit `ping` command in the terminal to make sure all is set and store the IP in an environment variable:

```shell
└─$ export IP=10.129.129.184
└─$ echo $IP
10.129.129.184

└─$ ping $IP                                                                          
PING 10.129.129.184 (10.129.129.184) 56(84) bytes of data.
64 bytes from 10.129.129.184: icmp_seq=1 ttl=63 time=68.6 ms
64 bytes from 10.129.129.184: icmp_seq=2 ttl=63 time=68.5 ms
64 bytes from 10.129.129.184: icmp_seq=3 ttl=63 time=68.5 ms
64 bytes from 10.129.129.184: icmp_seq=4 ttl=63 time=68.4 ms
````

All is set!

---

## Enumeration

First, I ran a scan on the target machine to identify open ports and running services that might be vulnerable using [nmap](https://nmap.org) with the following flags:
`-sV`: Determine running services/versions on open ports
`-sC`: Run default scripts
`-v`: Verbose output for more information about the scan
`-oN`: Write the output of the scan into a file

scan result:



user : f54846c258f3b4612f78a819573d158e
root : 51709519ea18ab37dd6fc58096bea949

thisisagoodpassword