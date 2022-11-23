# Paper

---

## Enumeration

- nmap:

```

```

- Response headers shows 'office.paper' -> added to /etc/hosts
- Found 'Michael' as a user with secrets, Nick as an employee?
- found wordpress version 5.2.3 in page source
- used searchsploit and got secret blogs read vulnerability by adding `?static=1`

---

## Foothold

- Found secret link http://chat.office.paper/register/8qozr226AhkCHZdyY -> added subdomain to /etc/hosts
- Registered and started chat with box and found LFI
- got /proc/self/environ and combined it with /etc/passwd and got creds:

rocketchat:Queenofblad3s!23 or maybe user dwight

---

## PrivEsc

- linpeas.sh shows it's vulnerable to CVE-2021-3560 and it worked.

---

