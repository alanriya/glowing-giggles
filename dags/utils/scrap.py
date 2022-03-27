"""
the webscrapper library is used to check for the find all the links available on the index page, 
"""
import os, sys
sys.path.append(os.getcwd())


from dags.utils.urls import INDEX_PAGE
import requests
from bs4 import BeautifulSoup
import pdb

class FileDateScrapper:
    """
    FileDateScrapper will look for the html page at INDEX_PAGE and check if there are new dates, ignoring the first 2 entries.
    """
    def __init__(self, url = INDEX_PAGE):
        self.url = url
    
    def get_content(self, **kwargs):
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
        self.get_current_latest_date(**kwargs)

    def get_current_latest_date(self, **kwargs):
        """
        method to only save content when the last date is updated
        """
        kwargs['ti'].xcom_push(key='current_latest_date', value=self.dates[-1])
        

