#-*- coding:utf-8 -*-

import requests
url = 'localhost:8080/action'
payload = "{}"
headers = {}
response = requests.request('POST', url, headers = headers, data = payload)
print(response.text)
