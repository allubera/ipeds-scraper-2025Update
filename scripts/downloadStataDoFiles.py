"""
Download all IPEDS  Complete Do Files for a given set of years
Extract and keep final/revised versions
Make a json specifying columns in each data file
Hannah Recht, 04-04-16

The do files contain the labels for the varaible values.  
Stata files do not have a 'save' function, so we will need to run each script and then save the var labels and definitions to get a crosswalk between dummy values and their actual string definitions.
"""

from urllib.request import urlopen
import json
import zipfile
import os
import csv
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("start", help="start year",
                    type=int)
parser.add_argument("stop", help="stop year",
                    type=int)
args = parser.parse_args()

# Import json of available files, created in scraper.py
with open('data/ipedsfiles.json') as fp:
    allfiles = json.load(fp)

# Download all the data in given years
def downloadData(start, stop):
    print("*****************************")
    print("Downloading do files")
    print("*****************************")
    for i in range(start,stop):
        print("Downloading " + str(i) + " do files")
        # Make directory for the raw files - one per year
        if not os.path.exists('dofiles/' + str(i) + '/'):
            os.makedirs('dofiles/' + str(i) + '/')
        # Download all the files in the json
        for f in allfiles:
            if(f['year']==i):
                # URL to download
                url = f['dourl']
                # dataset file name (XXXX.zip)
                urlname = url.split("http://nces.ed.gov/ipeds/datacenter/data/",1)[1]
                rd = urlopen(url)
                saveurl = "dofiles/" + str(i) +'/' + urlname
                # Save the zip files
                with open(saveurl, "wb") as p:
                     p.write(rd.read())
                     p.close()

                # Unzip .zips
                zip_ref = zipfile.ZipFile(saveurl, 'r')
                zip_ref.extractall("dofiles/" + str(i) +'/')
                zip_ref.close()

                # Remove zip file
                os.remove("dofiles/" + str(i) +'/' + urlname)

# Some datasets have been revised over time, so they'll download XXXX.csv and XXXX_rv.csv
# We only want the revised version
def removeDups(start, stop):
    print("*****************************")
    print("Removing duplicates")
    print("*****************************")
    for i in range(start,stop):
        print("Removing " + str(i) + " duplicates")
        files = os.listdir('dofiles/' + str(i) + '/')
        # See how many files are in each year
        # print([i,len(files)])
        for file in files:
            # file name minus '.csv'
            name = file[:-4]
            # If the file name ends in _rv, keep that one and delete the other (no _rv)
            if(name[-3:] =='_rv'):
                #print(name)
                unrevised = name[:-3]
                if(os.path.exists('dofiles/' + str(i) + '/' + unrevised + '.csv')):
                    os.remove('dofiles/' + str(i) + '/' + unrevised + '.csv')
                    print('Removed ' + unrevised)
#                else:
#                    print('no match ' + unrevised)

downloadData(args.start, args.stop)
removeDups(args.start, args.stop)
