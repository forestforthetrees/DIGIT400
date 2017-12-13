import sys
import re
import webbrowser
from bs4 import BeautifulSoup
import requests

def search(userinput):
    term = userinput.replace(' ','+')
    query = "https://www.google.com/search?num=001&safe=off&q="+term
    htmlText = requests.get(query)
    soup = BeautifulSoup(htmlText.text, "html.parser")
    #textSearch = soup.findAll("div",attrs={'id':'search'})
    for topResult in soup.findAll('h3',attrs={'class':'r'},limit=1):
        for titties in topResult.findAll('a', attrs={'data-href'}):
            return str(titties)