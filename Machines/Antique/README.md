# Antique

---

## Enum

- nmap TCP Scan:

```
PORT   STATE SERVICE VERSION
23/tcp open  telnet
```

- nmap UDP Scan:

```
PORT      STATE  SERVICE
161/udp   open   snmp
```

- `snmpwalk -c public -v2c $IP .` revealed HEX bits represented base64 text, password: P@ssw0rd@123!!123
- RCE -> get revshell

---

## PrivEsc

- Discovered port 631 open for local IP mapping.
- runs CUPS 1.6.1
- found vulnerability in error reading from a file.
- crafted a webshell payload and planted in the error log path
- got revshell afterwards

---
