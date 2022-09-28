# Blue

---

## Setup

Spawned in the machine as always, got the IP and stored it in an environment variable in case I lose it -as always-

```shell
└─$ export IP=10.10.10.40
└─$ echo $IP
10.10.10.40
```

and to make sure everything is working alright and the target machine is up and running, we can use `ping` to make sure it's alive.

```shell
└─$ ping $IP
PING 10.10.10.40 (10.10.10.40) 56(84) bytes of data.
64 bytes from 10.10.10.40: icmp_seq=1 ttl=63 time=69.3 ms
64 bytes from 10.10.10.40: icmp_seq=2 ttl=63 time=68.1 ms
64 bytes from 10.10.10.40: icmp_seq=3 ttl=63 time=67.9 ms
64 bytes from 10.10.10.40: icmp_seq=4 ttl=63 time=70.4 ms
```

---

## Enumeration

First step after spawning in the target machine and connected to the VPN, I start an [`nmap`](https://nmap.org) scan to determine open ports and running services and may be vulnerable using the following flags:

`-sV`: Determine running services/versions on open ports
`-sC`: Run default scripts
`-v`: Verbose output for more information about the scan
`-oN`: Write the output of the scan into a file
`-p-`: To scan all possible ports

``` shell
└─$ nmap -sV -sC -v -oN scan.nmap $IP
```