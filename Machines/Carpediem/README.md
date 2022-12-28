# Carpediem

---

## Enumeration


- nmap

```
PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 8.2p1 Ubuntu 4ubuntu0.5 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   3072 962176f72dc5f04ee0a8dfb4d95e4526 (RSA)
|   256 b16de3fada10b97b9e57535c5bb76006 (ECDSA)
|_  256 6a1696d80529d590bf6b2a0932dc364f (ED25519)
80/tcp open  http    nginx 1.18.0 (Ubuntu)
|_http-title: Comming Soon
|_http-server-header: nginx/1.18.0 (Ubuntu)
| http-methods: 
|_  Supported Methods: GET HEAD
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel
```

- GoBuster in DirScan_1
`gobuster dir -u http://carpediem.htb -w /usr/share/wordlists/dirbuster/directory-list-2.3-small.txt | tee DirScan_1`

- Subdomain fuzz
`└─$ wfuzz -c -u http://carpediem.htb -w /usr/share/wordlists/seclists/Discovery/DNS/subdomains-top1million-5000.txt -H "Host: FUZZ.carpediem.htb" --hw 161 | tee subDomainFuzz`

found `portal` subdomain

- edit UpdateAccount request to login_type=1, go to /admin, IM ADMIN

- Image upload vulnerability in admin profile edit, uploaded a web shell and got a reverse shell as `www-data` in a docker container

---

## Foothold

- Checking env variable got mysql creds:

password: 3dQXeqjMHnq4kqDv
hostname: 3c371615b7aa
port: 3306
IP: 172.17.0.3

```bash
www-data@3c371615b7aa:/$ env

MYSQL_PORT_33060_TCP_ADDR=172.17.0.3
MYSQL_PORT=tcp://172.17.0.3:3306
MYSQL_PORT_3306_TCP_ADDR=172.17.0.3
MYSQL_NAME=/portal/mysql
MYSQL_ENV_MYSQL_ROOT_PASSWORD=3dQXeqjMHnq4kqDv
MYSQL_PORT_3306_TCP_PORT=3306
HOSTNAME=3c371615b7aa
PHP_VERSION=7.4.25
APACHE_CONFDIR=/etc/apache2
PHP_INI_DIR=/usr/local/etc/php
GPG_KEYS=42670A7FE4D0441C8E4632349E4FDC074A4EF02D 5A52880781F755608BF815FC910DEB46F53EA312
MYSQL_ENV_MYSQL_MAJOR=8.0
PHP_LDFLAGS=-Wl,-O1 -pie
MYSQL_PORT_3306_TCP=tcp://172.17.0.3:3306
MYSQL_ENV_GOSU_VERSION=1.12
LANG=C
MYSQL_PORT_33060_TCP_PROTO=tcp
```

- Also checked some interesting config files and got more creds:

*initialize.php*

```php
<?php
$dev_data = array('id'=>'-1','firstname'=>'Developer','lastname'=>'','username'=>'dev_oretnom','password'=>'5da283a2d990e8d8512cf967df5bc0d0','last_login'=>'','date_updated'=>'','date_added'=>'');
if(!defined('base_url')) define('base_url','http://portal.carpediem.htb/');
if(!defined('base_app')) define('base_app', str_replace('\\','/',__DIR__).'/' );
if(!defined('dev_data')) define('dev_data',$dev_data);
if(!defined('DB_SERVER')) define('DB_SERVER',"mysql");
if(!defined('DB_USERNAME')) define('DB_USERNAME',"portaldb");
if(!defined('DB_PASSWORD')) define('DB_PASSWORD',"J5tnqsXpyzkK4XNt");
if(!defined('DB_NAME')) define('DB_NAME',"portal");
?>
```

- Tunneled the connection using chisel and started enumerating other docker containers

- on mysql on `172.17.0.3` found users table:

```
+----+-----------+----------+--------+------------------------+----------+----------------------------------+---------+-----------------------------------+------------+------------+---------------------+---------------------+
| id | firstname | lastname | gender | contact                | username | password                         | address | avatar                            | last_login | login_type | date_added          | date_updated        |
+----+-----------+----------+--------+------------------------+----------+----------------------------------+---------+-----------------------------------+------------+------------+---------------------+---------------------+
|  1 | Jeremy    | Hammond  | Male   | jhammond@carpediem.htb | admin    | b723e511b084ab84b44235d82da572f3 |         | uploads/1635793020_HONDA_XADV.png | NULL       |          1 | 2021-01-20 14:02:37 | 2022-04-01 23:34:50 |
+----+-----------+----------+--------+------------------------+----------+----------------------------------+---------+-----------------------------------+------------+------------+---------------------+---------------------+
```