# -*- coding: utf-8 -*-
"""
Created on Fri Jan  8 10:05:59 2021

@author: arnau
"""

import requests
from bs4 import BeautifulSoup
import re

def url_get_info(url):
    """
    This function allow to retreive information from an url. 
    Information retreived : product_page_url, universal_ product_code (upc), title
    price_including_tax, price_excluding_tax, number_available, product_description,
    category, review_rating, image_url

    """
    product_info = {"product_page_url":url}
    header_match = {"UPC":"universal_ product_code (upc)", "Price (incl. tax)":"price_including_tax", "Price (excl. tax)":"price_excluding_tax", "Availability":"number_available"}
    
    response = requests.get(url)
    if response.ok:
        soup = BeautifulSoup(response.text, features="html.parser")

        #retreive title
        product_info["title"] = soup.find('h1').text
        #retreive UPC, prices and nb available
        for elt in list(soup.findAll('tr')):
            line_info = re.findall(r"<th>(.*)</th>\n?<td>(.*)</td>",str(elt))
            if line_info[0][0] in header_match:
                product_info[header_match[line_info[0][0]]] = line_info[0][1]
        #retreive description
        product_info["product_description"] = soup.find_all('p')[3].text
        #retreive category
        product_info["category"] = re.findall(r"<a href=.*>(.*)</a>",str(soup.findAll('a')[3]))[0]
        #retreive rating
        rating_treatment = soup.find_all('p')[2]
        product_info["review_rating"] = re.findall(r"<p class=\"star-rating (.*)\">",str(rating_treatment))[0]
        #retreive image url
        product_info["image_url"] = "http://books.toscrape.com/" + re.findall(r"<img alt=.* src=\"../../(.*)\"/>",str(soup.img))[0]
    return product_info
        
if __name__ == "__main__":
    url = "http://books.toscrape.com/catalogue/birdsong-a-story-in-pictures_975/index.html"
    print(url_get_info(url))