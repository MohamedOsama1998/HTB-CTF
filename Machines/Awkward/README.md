# Awkward

---

## Setup





---

## Enumeration


- nmap -> port 22, 80
- 10.129.201.62 -> http://hat-valley.htb/
- Cookie -> token:guest ?
- dirScan -> /hr, change token to admin -> redirected to dashboard
- Found API call /api/staff-details -> add to repeater, remove cookie, send -> passwords
- Cracked password: christopher.jones:chris123
- Login chrstopher's acc in dashboard -> found JWT
- Cracked JWT Key: 123beany123 "john --format=HMAC-SHA256 --wordlist=rockyou.tx"
