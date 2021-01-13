# -*- coding: utf-8 -*-
"""
Created on Fri Jan  8 10:05:59 2021

@author: arnau
"""

import requests, urllib.request
from bs4 import BeautifulSoup
import re
import os
import csv

def url_get_info(url):
    """
    This function allow to retreive information from an url. 
    This function return a dictionnary with the following book's information :
    product_page_url, universal_ product_code (upc), title, price_including_tax, 
    price_excluding_tax, number_available, product_description,category, review_rating, image_url
    
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
                product_info[header_match[line_info[0][0]]] = (line_info[0][1]).replace("Â","")
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
    This fonction write the book information retreived earlier in a csv file with headers.
    A list of dictionnary with all books information is enter in parameter, in addition
    the file name needed to save the CSV file.
    
    """
    #exist_file = os.path.isfile(file_name)
    with open(file_name, 'w', newline='') as file:
        w = csv.DictWriter(file, fieldnames = dict_list_info[0].keys())
        #if not exist_file:
        w.writeheader()
        w.writerows(dict_list_info)
        
def get_category_url(url_category):
    """ 
    This function allow to retreive all book's url from a category of book.
    The url in parameter is the url of the category.
    This function return a list with all books url of the category.
    
    """
    links = []
    next_page = True
    idx_page = 1
    
    while next_page:
        response = requests.get(url_category)
        if response.ok:
            soup = BeautifulSoup(response.text, features="html.parser")
            for elt in soup.findAll("h3"):
                a = elt.find("a")
                link = a['href']
                links.append("http://books.toscrape.com/catalogue" + link.removeprefix('../../..'))
            idx_page += 1
            url_category = url_category.replace("index", "page-" + str(idx_page)).replace("page-" + str(idx_page-1), "page-" + str(idx_page))
 
        else:
            next_page = False
        
    print("nous avons scrapé les {} page(s) de la categorie : {}".format(idx_page - 1,re.findall(r'<h1>(.*)</h1>',str(soup.findAll('h1')))[0]))
            
    return links

def get_all_category(inner_url):
    """
    Retreive all category names with their own urls.
    The general url website is enter in parameter.
    This function return a list of tuple with category name and the url of the category.
    
    """
    links = []
    response = requests.get(inner_url)
    if response.ok:
        soup = BeautifulSoup(response.text, features="html.parser")
        ul = soup.findAll('ul')[2]
        for elt in ul.findAll('a'):
            link = inner_url + elt['href']
            category = (elt.text).strip()
            links.append((category,link))
        
    return links

def fetch_image(image_url, category, book_name):
    """
    Function that fetch the cover of a book and saved it 
    in the category folder.
    This function takes in parameter the image url to fetch the image,
    the category and book name to save the folder at the right place.
    
    """
    #file name treatment
    book_name = book_name.decode().replace(" ","_").replace("Ã©",'e')
    category = category.replace(" ", "_")

    punc = '''!()-[]{};:'"\, <>./?@#$%^&*~'''
    for pct in punc:
        book_name = book_name.replace(pct,"")
        
    if len(book_name) > 100:
        book_name = book_name[:100]+"..."
    
    #we do not import the picture if it has been already saved
    if not os.path.exists("scraping/"+category+"/"+book_name+".jpg"):
        if requests.get(image_url).ok:
            response = urllib.request.urlopen(image_url)
            #We create the category path if it does not exist
            if not os.path.exists("scraping//"+category):
                os.mkdir("scraping//"+category)
            #We saved the picture
            with open("scraping/"+category+"/"+book_name+".jpg",'wb') as pic:
                pic.write(response.read())
        
if __name__ == "__main__":
    #Retreive url categories
    inner_url = "http://books.toscrape.com/"
    all_cat = get_all_category(inner_url)
 
    #create a directory to stock csv if it does not exist    
    if not os.path.exists("scraping"):
        os.mkdir("scraping")

    #for each category, retreive all cover's books and write a csv file with book info        
    for cat in all_cat:
        list_url = get_category_url(cat[1])
        dict_list = []
        for elt in list_url:
            dict_list.append(url_get_info(elt))
            fetch_image(dict_list[-1]["image_url"], dict_list[-1]["category"], dict_list[-1]["title"])
        write_csv(dict_list,"scraping//booksToScrap_"+cat[0]+".csv")
    