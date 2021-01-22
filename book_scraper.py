# -*- coding: utf-8 -*-
"""
Created on Fri Jan  8 10:05:59 2021

@author: Amelie Noury
"""
import re
import os
import csv
#Web request package
import urllib.request
import requests
from bs4 import BeautifulSoup
#text treatments
from slugify import slugify

def get_book_info_from_url(url):
    """

    This function allow to retreive information from an url.
    This function return a dictionnary with the following book's information :
    product_page_url, universal_ product_code (upc), title, price_including_tax,
    price_excluding_tax, number_available, product_description,category, review_rating, image_url

    """
    product_info = {"product_page_url":url}
    header_match = {"UPC":"universal_ product_code (upc)",
                    "Price (incl. tax)":"price_including_tax",
                    "Price (excl. tax)":"price_excluding_tax",
                    "Availability":"number_available"}

    response = requests.get(url)
    if response.ok:
        soup = BeautifulSoup(response.content, features="html.parser")

        #retreive title
        product_info["title"] = check_tag(soup.h1,methode_text=True)
        #retreive UPC, prices and nb available
        nb_th = 0
        for elt in soup.find('table', {'class':"table table-striped"}).findAll('th'):
            if elt.text in header_match:
               product_info[header_match[elt.text]] = check_tag(soup.find('table', \
               {'class':"table table-striped"}).findAll('td'),nb_th,True)
            nb_th +=1
        #retreive description
        product_info["product_description"] = check_tag(soup.select('#product_description ~ p'), \
        0,True)
        #retreive category
        product_info["category"] = check_tag(soup.find('ul', \
        {'class':"breadcrumb"}).findAll('a'),3,True)
        #retreive rating
        rating_treatment = check_tag(soup.findAll('p',{'class':'star-rating'}),0)
        product_info["review_rating"] = re.findall(r"<p class=\"star-rating (.*)\">", \
        str(rating_treatment))[0]
        #retreive image url
        product_info["image_url"] = "http://books.toscrape.com/" \
        + check_tag(soup.img.attrs["src"]).removeprefix('../../')
    return product_info

def check_tag(tag_request, elt_nb='',methode_text=''):
    """

    This function verifies if the tag exists
    To get the value of the requete we enter in parameters the tag request,
    the element number in the table and if we want to execute the text method.
    If the tag exists, it returns the value of the request, otherwise "NC"

    """
    try:
        if tag_request != []:
            if elt_nb != '':
                if methode_text:
                    return tag_request[elt_nb].text
                else:
                    return tag_request[elt_nb]
            elif methode_text:
                return tag_request.text
            else:
                return tag_request
        else:
            return"NC"
    except:
        return "NC"

def write_csv(dict_list_info, file_name):
    """

    This fonction write the book information retreived earlier in a csv file with headers.
    A list of dictionnary with all books information is enter in parameter, in addition
    the file name needed to save the CSV file.

    """
    with open(file_name, 'w', newline='',encoding='utf-8-sig') as file:
        write_file = csv.DictWriter(file, fieldnames = dict_list_info[0].keys(), dialect='excel')
        write_file.writeheader()
        write_file.writerows(dict_list_info)

def get_all_url_for_category(url_category):
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
            soup = BeautifulSoup(response.content, features="html.parser")
            for elt in soup.findAll("h3"):
                a_tag = check_tag(elt.find("a"))
                link = check_tag(a_tag['href'])
                links.append("http://books.toscrape.com/catalogue" \
                + link.removeprefix('../../..'))
            idx_page += 1
            url_category = url_category.replace("index", "page-" \
            + str(idx_page)).replace("page-" + str(idx_page-1), "page-" + str(idx_page))

        else:
            next_page = False

    print("we scraped {} page(s) of the category : {}".format(idx_page - 1,\
    re.findall(r'<h1>(.*)</h1>',str(soup.findAll('h1')))[0]))

    return links

def get_all_category_from_url(inner_url):
    """

    Retreive all category names with their own urls.
    The general url website is enter in parameter.
    This function return a list of tuple with category name and the url of the category.

    """
    links = []
    response = requests.get(inner_url)
    if response.ok:
        soup = BeautifulSoup(response.content, features="html.parser")
        ul_tag = check_tag(soup.select('ul[class="nav nav-list"] ul'),0)
        for elt in ul_tag.findAll('a'):
            link = inner_url + check_tag(elt['href'])
            category = (elt.text).strip()
            links.append((category,link))
    return links

def fetch_image(image_url, category, book_name):
    """

    Function that fetch the cover of a book and saved it in the category folder.
    This function takes in parameter the image url to fetch the image,
    the category and book name to save the folder at the right place.

    """

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
    INNER_URL = "http://books.toscrape.com/"
    print("This program will extract data from the following website : {}".format(INNER_URL))
    print("*********************STARTING EXTRACTION TRANSFORMATION LOADING************************")
    all_cat = get_all_category_from_url(INNER_URL)

    #create a directory to stock csv if it does not exist
    if not os.path.exists("scraping"):
        os.mkdir("scraping")

    #for each category, retreive all cover's books and write a csv file with book info
    for cat in all_cat:
        list_url = get_all_url_for_category(cat[1])
        dict_list = []
        for elt in list_url:
            dict_list.append(get_book_info_from_url(elt))
            fetch_image(dict_list[-1]["image_url"], slugify(dict_list[-1]["category"], \
            separator="_"), slugify(dict_list[-1]["title"],separator="_",max_length=100))
        write_csv(dict_list,"scraping//"+slugify(cat[0], separator="_") \
        +"//_booksToScrap_"+cat[0]+".csv")

    print("*******************END OF EXTRACTION TRANSFORMATION LOADING******************")
    print("All the files are saved on the following link : {}".format(os.getcwd()+'\\scraping\\'))
    