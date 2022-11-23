# Carpediem

---

## Setup



---

## Enumeration


1. nmap

2. GoBuster in DirScan_1
`gobuster dir -u http://carpediem.htb -w /usr/share/wordlists/dirbuster/directory-list-2.3-small.txt | tee DirScan_1`

3. Subdomain fuzz
`└─$ wfuzz -c -u http://carpediem.htb -w /usr/share/wordlists/seclists/Discovery/DNS/subdomains-top1million-5000.txt -H "Host: FUZZ.carpediem.htb" --hw 161 | tee subDomainFuzz`

found `portal` subdomain

4. edit UpdateAccount request to login_type=1, go to /admin, IM ADMIN
