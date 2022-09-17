import base64

enc_password = base64.b64decode("0Nv32PTwgYjzg9/8j5TbmvPd3e7WhtWWyuPsyO76/Y+U193E")
key = "armando".encode("ascii")

for i in range(len(enc_password)):
	print(chr((enc_password[i] ^ key[i % len(key)]) ^ 0xdf ), end="")

print()