# -*- coding: utf-8 -*-
"""
Scrape IPEDS http://nces.ed.gov/ipeds/datacenter/DataFiles.aspx
Hannah Recht, 03-24-16
"""


from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import Select
import json



driver = webdriver.Chrome()

# Directory url for downloads
dirurl = "http://nces.ed.gov/ipeds/datacenter/"



files = list()

def scrapetable():
    # Scrape table of datasets
    content = driver.page_source
    soup = BeautifulSoup(''.join(content), "lxml")
    table = soup.find("table", { "id" : "contentPlaceHolder_tblResult" })
    # Get info and URLs for data zip and dictionary zip
    for row in table.find_all('tr')[1:]:
        entry = dict()
        tds = row.find_all('td')
        entry['year'] = int(tds[0].text)
        entry['survey'] = tds[1].text
        entry['title'] = tds[2].text
        #Changed from 3 to 4 in order to get the STATA version of the file 
        entry['dataurl'] = dirurl + tds[4].a.get('href')
        #added to get the stata do file download location 
        entry['dicturl'] = dirurl + tds[6].a.get('href')
        # File name minus 'data/' and '.zip'
        entry['name'] = (tds[3].a.get('href')[5:-4]).lower()
        link_text = "STATA" 
        cell_content = tds[5].get_text()
        links = cell_content.split(',')
        for link in links:
            if link.strip() == link_text:  # `strip()` removes extra spaces
                # Now find the corresponding href by searching through <a> tags
                for a_tag in tds[5].find_all('a'):
                    if a_tag.get_text().strip() == link_text:
                        entry['dourl'] = dirurl + a_tag.get('href')
                        break  # Exit the loop once the desired link is found
                break  # Exit the loop once the correct link is matched
        files.append(entry)

#There is now a page with all the links which should make this all easier

driver.get('https://nces.ed.gov/ipeds/datacenter/DataFiles.aspx?year=-1&surveyNumber=-1&sid=7db6a4c4-3571-4cef-b3f3-59df9576a9e7&rtid=7')

scrapetable()

# Export to json
with open('data/ipedsfiles.json', 'w') as fp:
    json.dump(files, fp)


