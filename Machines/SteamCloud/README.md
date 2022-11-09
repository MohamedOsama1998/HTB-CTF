# SteamCloud

---

## Enumeration

- nmap scan:

```bash
Not shown: 65528 closed tcp ports (conn-refused)
PORT      STATE SERVICE
22/tcp    open  ssh
2379/tcp  open  etcd-client
2380/tcp  open  etcd-server
8443/tcp  open  https-alt
10249/tcp open  unknown
10250/tcp open  unknown
10256/tcp open  unknown
```


kubectl --token=$token --certificate-authority=ca.crt --server=https://10.10.11.133:8433
