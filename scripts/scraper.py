# -*- coding: utf-8 -*-
"""
Scrape IPEDS http://nces.ed.gov/ipeds/datacenter/DataFiles.aspx
Hannah Recht, 03-24-16

Updated to simplify because IPEDs now has a page with all years in one location. No needs to use continue finder at the current time. 
Amber Lubera, 02-14-2025 
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
        entry['dataurl'] = dirurl + tds[3].a.get('href')
        entry['dicturl'] = dirurl + tds[6].a.get('href')
        # File name minus 'data/' and '.zip'
        entry['name'] = (tds[3].a.get('href')[5:-4]).lower()
        files.append(entry)

# The direct link to view complete data files given below. 
# Previous code commented out but left in case website changes again

# Complete data files entry point
driver.get('https://nces.ed.gov/ipeds/datacenter/DataFiles.aspx?year=-1&surveyNumber=-1&sid=7db6a4c4-3571-4cef-b3f3-59df9576a9e7&rtid=7')

# Go directly to scrapetable 
scrapetable()

'''
# Press continue
driver.find_element_by_xpath("//input[@id='ImageButton1' and @title='Continue']").click()

# Make a list for all the available years
select = Select(driver.find_element_by_id('contentPlaceHolder_ddlYears'))
years = list()
for option in select.options:
    years.append(option.get_attribute('value'))

# Get info on all the available datasets per year, save
def chooseyear(year):
    # Choose year from dropdown
    select.select_by_value(year)
    # Continue to list of datasets
    driver.find_element_by_xpath("//input[@id='contentPlaceHolder_ibtnContinue']").click()
    # Scrape the table of available datasets, add to 'files'
    scrapetable()

# -1 = All years
chooseyear('-1')

'''

# Export to json
with open('data/ipedsfiles.json', 'w') as fp:
    json.dump(files, fp)
