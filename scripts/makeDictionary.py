# -*- coding: utf-8 -*-
"""
Download IPEDS dictionaries and make a master csv dictionary
Note, pre-2009 dictionaries are awfully-formatted HTML.
"""

from urllib.request import urlopen
import json
import zipfile
import os
import xlrd
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

# Make directory for the raw files
if not os.path.exists('raw/dictionary/'):
    os.makedirs('raw/dictionary/')

# The pre-2009 dictionaries are HTML. Fun! Actually misery! 2009+ are mix of .xls and .xlsx and a few .html
# Downloading the pre-2009 dictionary zips will get you a bunch of html files

def downloadDicts(start, stop):
    print("*****************************")
    print("Downloading dictionaries")
    print("*****************************")
    for i in range(start,stop):
        print("Downloading " + str(i) + " dictionaries")
        # Make directory for the raw files - one per year
        if not os.path.exists('dict/' + str(i) + '/'):
            os.makedirs('dict/' + str(i) + '/')
        # Download all the files in the json
        for f in allfiles:
            if(f['year']==i):
                # URL to download
                url = f['dicturl']
                # dataset file name (XXXX.zip)
                urlname = url.split("http://nces.ed.gov/ipeds/datacenter/data/",1)[1]
                rd = urlopen(url)
                saveurl = "dict/" + str(i) +'/' + urlname
                # Save the zip files
                with open(saveurl, "wb") as p:
                     p.write(rd.read())
                     p.close()

                # Unzip .zips
                zip_ref = zipfile.ZipFile(saveurl, 'r')
                zip_ref.extractall("dict/" + str(i) +'/')
                zip_ref.close()

                # Remove zip file
                os.remove("dict/" + str(i) +'/' + urlname)

# As of the current date, xlrd has explicitly removed support for anything other than xls files.
def makeMasterDict(start, stop):
    print("*****************************")
    print("Assembling master dictionary")
    print("*****************************")
    # Set up dictionary CSV
    with open('data/dictionary.csv', 'w', newline='') as f:
        c = csv.writer(f)
        c.writerow(['year', 'dictname', 'dictfile', 'varnumber', 'varname', 'datatype' ,'fieldwidth', 'format', 'imputationvar', 'vartitle'])
    # List of possible sheet names
    sheet_names = ['varlist', 'Varlist', 'VARLIST']
    # Iterate through the specified years
    for i in range(start, stop):
        dict_path = f'dict/{i}/'
        # Ensure directory exists before listing files
        if not os.path.exists(dict_path):
            print(f"Skipping {dict_path}, directory does not exist.")
            continue
        for file in os.listdir(dict_path):
            if file.endswith((".xls", ".xlsx")):
                print(f"Adding {i} {file} to dictionary")
                dictname = file.split(".", 1)[0]
                rowstart = [i, dictname, file]
                workbook_path = os.path.join(dict_path, file)
                try:
                    if file.endswith(".xls"):  # Handle old .xls format
                        workbook = xlrd.open_workbook(workbook_path, on_demand=True)
                        sheet_name = next((s for s in sheet_names if s in workbook.sheet_names()), None)
                        if sheet_name:
                            worksheet = workbook.sheet_by_name(sheet_name)
                            rows = [worksheet.row_values(r) for r in range(2, worksheet.nrows)]
                        else:
                            print(f"Skipping {file}: No matching sheet found.")
                            continue
                    elif file.endswith(".xlsx"):  # Handle new .xlsx format
                        workbook = openpyxl.load_workbook(workbook_path, data_only=True)
                        sheet_name = next((s for s in sheet_names if s in workbook.sheetnames), None)
                        if sheet_name:
                            worksheet = workbook[sheet_name]
                            rows = [[cell.value for cell in row] for row in worksheet.iter_rows(min_row=3)]  # Skip header rows
                        else:
                            print(f"Skipping {file}: No matching sheet found.")
                            continue
                    # Append data to dictionary CSV
                    with open('data/dictionary.csv', 'a', newline='') as f:
                        c = csv.writer(f)
                        for varrow in rows:
                            row = rowstart + varrow
                            c.writerow(row)
                except Exception as e:
                    print(f"Error processing {file}: {e}")


downloadDicts(args.start, args.stop)
makeMasterDict(args.start, args.stop)
