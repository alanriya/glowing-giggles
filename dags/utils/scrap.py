"""
the webscrapper library is used to check for the find all the links available on the index page, 
"""
import os, sys
sys.path.append(os.getcwd())

from urls import INDEX_PAGE
import requests
from bs4 import BeautifulSoup
import pdb

class FileDateScrapper:
    """
    FileDateScrapper will look for the html page at INDEX_PAGE and check if there are new dates, ignoring the first 2 entries.
    """
    def __init__(self, url = INDEX_PAGE):
        self.url = url
    
    def get_content(self):
        r = requests.get(self.url)
        dates = []
        soup = BeautifulSoup(r.content, "html5lib")
        content = soup.find_all("a")
        for a_tag in content:
            current_content = a_tag["href"]
            if ".." in current_content or "latest" in current_content:
                continue
            dates.append(a_tag["href"])            
        self.dates = dates
        self.save_content()

    def save_content(self):
        """
        method to only save content when the last date is updated
        """
        
        lines = None
        flag = False
        with open("./downloads/filedate.txt", "r") as f:
            lines = f.readlines()
            lines = [i.strip() for i in lines]
            if self.dates[-1] not in lines:
                flag = True
            else: 
                return False
        if flag:
            with open("./downloads/filedate.txt", "a") as f:
                f.write(f"{self.dates[-1]}\n")
        return True

FileDateScrapper().get_content()
