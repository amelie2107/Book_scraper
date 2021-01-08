# -*- coding: utf-8 -*-
"""
Created on Fri Jan  8 10:05:59 2021

@author: arnau
"""

import requests
from bs4 import BeautifulSoup

r = requests.get("http://books.toscrape.com/catalogue/birdsong-a-story-in-pictures_975/index.html")
soup = BeautifulSoup(r.text, features="html.parser")
print(soup.text)

