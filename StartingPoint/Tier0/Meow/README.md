# Meow

---

## Enumeration

Before starting the enumeration process I always store the IP Address of the victim machine in a environment variable to refer back to in case there's something else occupying my clipboard:
```
$ export IP = 10.129.200.97
```
and just in case:
```
$ echo $IP
10.129.200.97
```

To make sure the target machine is alive and everything is setup correctly, I use `ping` command to see if i get any response from the target machine:
```
$ ping $IP
PING 10.129.200.97 (10.129.200.97) 56(84) bytes of data.
64 bytes from 10.129.200.97: icmp_seq=1 ttl=63 time=68.3 ms
64 bytes from 10.129.200.97: icmp_seq=2 ttl=63 time=67.6 ms
64 bytes from 10.129.200.97: icmp_seq=3 ttl=63 time=68.4 ms
64 bytes from 10.129.200.97: icmp_seq=4 ttl=63 time=68.6 ms
64 bytes from 10.129.200.97: icmp_seq=5 ttl=63 time=79.0 ms
```
Next step I start scanning the target's open ports and services running on it using [nmap](https://nmap.org) with the `-sV` flag to determine the name of the identified service and its description, `-p-` to scan all possible ports, `-v` for verbose output and more information about the scanning process, `-oN` to save the output to a file.
```
$ nmap -sV -sC -p- -v -oN scan.nmap $IP
```

after the scan is complete, here's the result:
```
Nmap scan report for 10.129.200.97
Host is up (0.19s latency).
Not shown: 65534 closed tcp ports (conn-refused)
PORT   STATE SERVICE VERSION
23/tcp open  telnet  Linux telnetd
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel
```

The result shows the only open port is 23 and running a service called [Telnet](https://en.wikipedia.org/wiki/Telnet), this link takes you to the official wiki page, and it does a pretty good job at explaining it.

---

## Telnet 

I tried connecting to the Telnet server using `telnet` command in the terminal window:
```
$ telnet $IP
```
It worked and I connected to the server and got greeted with a login phase:
```
Trying 10.129.200.97...
Connected to 10.129.200.97.
Escape character is '^]'.

  █  █         ▐▌     ▄█▄ █          ▄▄▄▄
  █▄▄█ ▀▀█ █▀▀ ▐▌▄▀    █  █▀█ █▀█    █▌▄█ ▄▀▀▄ ▀▄▀
  █  █ █▄█ █▄▄ ▐█▀▄    █  █ █ █▄▄    █▌▄█ ▀▄▄▀ █▀█


Meow login:
```

I tried different usernames with no password `admin`, `administrator`, `guest`, `meow` and all went through with no success. However, after trying the username `root` and a blank password, I successfully had access to a terminal of the target machine.

```
root@Meow:~# ls
flag.txt  snap
root@Meow:~# cat flag.txt
b40abdfe23665f766f9c61ecba8a4c19
root@Meow:~# 
```

---

## Tasks & Answers

Task 1: What does the acronym VM stand for?
: Virtual Machine.

Task 2: What tool do we use to interact with the operating system in order to issue commands via the command line, such as the one to start our VPN connection? It's also known as a console or shell.
: Terminal

Task 3: What service do we use to form our VPN connection into HTB labs?
: openvpn

Task 4: What is the abbreviated name for a 'tunnel interface' in the output of your VPN boot-up sequence output?
: by using `ifconfig` in the terminal window: `tun`.

Task 5: What tool do we use to test our connection to the target with an ICMP echo request?
: ping.

Task 6: What is the name of the most common tool for finding open ports on a target?
: [nmap](https://nmap.org).

Task 7: What service do we identify on port 23/tcp during our scans?
: [Telnet](https://en.wikipedia.org/wiki/Telnet).

Task 8: What username is able to log into the target over telnet with a blank password?
: root.

FLAG:
: `b40abdfe23665f766f9c61ecba8a4c19`

---

## Vulnerability

This machine was pretty straight forward, this vulnerability was obvious that Telnet service had a user with root privs that can be accessed without a password, giving users - especially root - a password would come in handy.

```
root@Meow:~# sudo -l
Matching Defaults entries for root on Meow:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin

User root may run the following commands on Meow:
    (ALL : ALL) ALL
```

---

## TIP

If you get stuck in the Telnet terminal and CTRL+C does not spare you, in the very beginning of the connection you were prompted with `Escape character is '^]'`.

`'^]'` means ctrl + ] (right bracket), you'll be taken to the telnet prompt where you can type `quit` or simply `q` to terminate the connection.

```
root@Meow:~# 
telnet> quit
Connection closed.
```

---