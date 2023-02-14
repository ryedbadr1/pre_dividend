# -*- coding: utf-8 -*-
"""
Created on Mon Feb 13 23:31:45 2023

@author: Ryed
"""

import robin_stocks as rs
import sys
import os
import requests
from bs4 import BeautifulSoup as b
sys.path.insert(1, os.path.abspath(os.path.dirname(sys.argv[0]))+str("\\userincludes\\enc"))
import ryedMorse as rm

def login(email = None, passwords = None):
    url = 'https://ryedapi.pages.dev/'
    r = requests.get(url)
    soup = b(r.content, 'html.parser')
    if email is None or passwords is None:
        rs.robinhood.authentication.login(username= rm.decrypt(soup.select_one('#ruse').text.strip()),
            password= rm.decrypt(soup.select_one('#rpas').text.strip()).capitalize(),
            expiresIn=86400,
            by_sms=True)
    else:
        rs.robinhood.authentication.login(username=email,
            password=passwords,
            expiresIn=86400,
            by_sms=True)


    