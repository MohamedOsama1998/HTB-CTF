#!/usr/bin/env python3

import requests, argparse

parser = argparse.ArgumentParser()

parser.add_argument('-u', '--url', required=True, help='URL to pwn')
parser.add_argument('-U', '--username', required=True, help='Path to wordlist')
parser.add_argument('-p', '--password', required=True, help='Arguement in the request to brute force')

args = parser.parse_args()

