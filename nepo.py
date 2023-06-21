from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import requests
import re
import wikipediaapi as wiki
from datetime import datetime
import imdb
import matplotlib as mpl
import matplotlib.pyplot as plt
import sys

##########################
###     CONSTANTS      ###
##########################
# IMdb API key
api_key = "k_11m5rq35"

# headers
headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
       'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
       'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
       'Accept-Encoding': 'none',
       'Accept-Language': 'en-US,en;q=0.8',
       'Connection': 'keep-alive'}

# Parent and Relative strings to search for in wikipedia infobox
parent_pattern = re.compile('Parent')
relative_pattern = re.compile('Relative')
starring_pattern = re.compile('Starring')
voice_pattern = re.compile('Voices of')
wikipedia_pattern = re.compile("wiki")

not_nepo_relationships = 'son|daughter|nephew|niece|grandson|grand-daughter|grandnephew|grandniece|in-law|stepson|stepdaughter|brother|sister|cousin'

# url base
wiki_url_base = "https://en.wikipedia.org" # wikipedia

# wikipedia language setting
wiki_wiki = wiki.Wikipedia('en')

# remove white space
def remove_ws(name):
    no_ws = name.replace(" ", "_")
    return no_ws

# create url
def create_url(subject):
    url = wiki_url_base + "/wiki/" + subject
    return url

# does wiki exist
def wiki_exist(name):
    wiki_page = wiki_wiki.page(name)
    does_page_exist = wiki_page.exists()
    return does_page_exist

def get_soup(url):
    data = requests.get(url, headers=headers).text
    soup = BeautifulSoup(data,'html.parser') # full page
    return soup

# get infobox
def get_infobox(soup):
     # check if infobox exists
    infobox = soup.find("table",{"class":"infobox biography vcard"}) # infobox
    
    if infobox is None :
        infobox_alt = soup.find("table",{"class":"infobox vcard"}) # infobox
        return infobox_alt
    else :
        return infobox

def get_infobox_fields(infobox):
    infobox_fields = infobox.find_all('th', {'class' : 'infobox-label'})
    return infobox_fields

def parentfield_exist(infobox_fields):
    does_parent_or_rel_field_exist = bool(re.search("Parent|Relative", str(infobox_fields))) # see if Parent or Relative field is listed in infobox
    return(does_parent_or_rel_field_exist)

def parent_extraction(parent_field):
    parent_wiki_list = []
                            
    for link in parent_field.find_all('a'):
        parent_wiki = link.get('href')
        parent_wiki_link = wiki_url_base + parent_wiki
        parent_wiki_list.append(parent_wiki_link)

        parent_wiki_list[:] = [x for x in parent_wiki_list if "cite_note" not in x] # cited entries are in <a href> tags so remove those links here
    

    return parent_wiki_list


# given name of person, outputs parent links or false if none
def wiki_scrape(name):
    
    subject = remove_ws(name)
    url = create_url(subject)

    # check if wiki page exists
    does_page_exist = wiki_exist(name)

    if does_page_exist is False :
        return [] # no wiki page -> not famous enough, not a nepo baby
    
    elif does_page_exist is True : 
        soup = get_soup(url)
        infobox = get_infobox(soup)

        if infobox is None :
            return [] # no infobox on wiki page -> not a nepo baby
        
        else :
            infobox_fields = get_infobox_fields(infobox)
            does_parent_or_rel_field_exist = parentfield_exist(infobox_fields)

            if does_parent_or_rel_field_exist is False :
                return [] # parent field not listed in infobox -> not a nepo baby
            
            elif does_parent_or_rel_field_exist is True :
                
                try :
                    does_parent_field_exist = bool(re.search("Parent", str(infobox_fields)))
                    does_relative_field_exist = bool(re.search("Relative", str(infobox_fields)))
                    
                    if does_parent_field_exist is True :   
                        parent_field = soup.find('th', string=parent_pattern).parent
                        parent_a_tags = parent_field.find_all('a')
                        
                        if len(parent_a_tags) == 0 :
                            return [] # parents listed in infobox but not linked -> not a nepo baby
                        
                        else : # nepo baby!
                            parent_wiki_list = parent_extraction(parent_field)
                            return parent_wiki_list

                    elif does_relative_field_exist is True : 
                        relative_field = soup.find('th', string=relative_pattern).parent
                        relative_td_tags = relative_field.find_all('td')

                        list_of_relatives = re.split('</li>|<br/>', str(relative_td_tags))

                        parent_wiki_list = []

                        if len(relative_field.find_all('a')) == 0 :
                            return []
                        else :
                            for i in range(len(list_of_relatives)):
                                if bool(re.search(not_nepo_relationships, list_of_relatives[i])) is True:
                                    pass

                                else :
                                    try :
                                        href_match = re.search(r'href=\"(.*)\" title=', list_of_relatives[i])
                                        parent_wiki = href_match.group(1)
                                        parent_wiki_link = wiki_url_base + parent_wiki
                                        parent_wiki_list.append(parent_wiki_link)

                                    except AttributeError :
                                        pass  
                            
                            if len(parent_wiki_list) == 0 :
                                return []
                            else :
                                return parent_wiki_list
                
                except AttributeError :
                    pass