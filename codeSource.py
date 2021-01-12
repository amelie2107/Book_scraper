# -*- coding: utf-8 -*-
"""
Created on Fri Jan  8 10:05:59 2021

@author: arnau
"""

import requests
from bs4 import BeautifulSoup
import re
import os
import csv

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
        product_info["title"] = soup.find('h1').text.encode()
        #retreive UPC, prices and nb available
        for elt in list(soup.findAll('tr')):
            line_info = re.findall(r"<th>(.*)</th>\n?<td>(.*)</td>",str(elt))
            if line_info[0][0] in header_match:
                product_info[header_match[line_info[0][0]]] = line_info[0][1]
        #retreive description
        product_info["product_description"] = soup.find_all('p')[3].text.encode() #encode manually characters because I think chain is too long
        #retreive category
        product_info["category"] = re.findall(r"<a href=.*>(.*)</a>",str(soup.findAll('a')[3]))[0]
        #retreive rating
        rating_treatment = soup.find_all('p')[2]
        product_info["review_rating"] = re.findall(r"<p class=\"star-rating (.*)\">",str(rating_treatment))[0]
        #retreive image url
        product_info["image_url"] = ("http://books.toscrape.com/" + re.findall(r"<img alt=.* src=\"../../(.*)\"/>",str(soup.img))[0])
    return product_info

def write_csv(dict_list_info, file_name):
    """
    This fonction write the list of dictionnairy in a csv file with headers.
    a list of dictionnary with all books information is in parameter, in addition
    the file name in which we will save all the books information.
    """
    #exist_file = os.path.isfile(file_name)
    with open(file_name, 'w') as file:
        w = csv.DictWriter(file, fieldnames = dict_list_info[0].keys())
        #if not exist_file:
        w.writeheader()
        w.writerows(dict_list_info)
        
def get_category_url(url_category):
    """ 
    This function allow to retreive all book's url from a category of book.
    The url in parameter is the url of the category.
    """
    links = []
    next_page = True
    idx_page = 1
    url_category = url_category.replace("index", "page-" + str(idx_page))
    
    while next_page:
        url_category = url_category.replace("page-" + str(idx_page-1), "page-" + str(idx_page))
        response = requests.get(url_category)
        if response.ok:
            soup = BeautifulSoup(response.text, features="html.parser")
            h3 = soup.findAll("h3")
            for elt in h3:
                a = elt.find("a")
                link = a['href']
                links.append("http://books.toscrape.com/catalogue" + link.removeprefix('../../..'))
            idx_page += 1
        else:
            next_page = False
        
    print("nous avons scrapé les {} page(s) de la categorie : {}".format(idx_page - 1,re.findall(r'<h1>(.*)</h1>',str(soup.findAll('h1')))[0]))
            
    return links
            
        
if __name__ == "__main__":
    list_url_childrens = get_category_url("http://books.toscrape.com/catalogue/category/books/childrens_11/index.html")
    dict_list = []
    for elt in list_url_childrens:
        dict_list.append(url_get_info(elt))
    write_csv(dict_list,"booksToScrap.csv")
    