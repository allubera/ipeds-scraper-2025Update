# IPEDS scraper

Download data from IPEDS [complete data files](http://nces.ed.gov/ipeds/datacenter/DataFiles.aspx). 

For each year, IPEDS splits data into several files - up to several dozen. The datasets are each saved as .csv and compressed into .zip (Stata file .zip are also available). For some years, revised datasets are available. These are included in the same .zip file. In revised file cases, the non-revised file is deleted in scripts/downloadData.py and the final version is saved.

Each file has a corresponding dictionary .zip, which includes .xls, .xlsx, or .html dictionaries. According to NCES, there is no comprehensive dictionary available.

Beware: variable names frequently change between years. In other cases, the variable name will stay the same but the value levels will change (e.g. 1,2,3 in 2000 and 5,10,15,20 in 2001). I don't have a good answer for comparing between years, besides looking at the data dictionaries. If you have a better answer please share!

In addition to these changes, the R script has been updated to allow querying and combining specific variables into a dataframe, but then also making that dataframe interpretable through replacing dummy values in the files with their string values from the labels dictionary. 

## Functions
### Scrape list of available files
Assembles [data/ipedsfiles.json](data/ipedsfiles.json) with info on all available complete data files from IPEDS (year, survey, title, data file .zip url, dictionary file .zip url)
```python
python3 scripts/scraper.py
```

### Make list of available files available for browsing
Assembles [data/ipedsfiles.json](data/ipedsfiles.json) with info on topics of items for easier searching 
```python
python3 scripts/scraperDescriptions.py
```
### Download do files
Download stata do files listed in [data/ipedsfiles.json](data/ipedsfiles.json) for a given range of years.
```python
python3 scripts/downloadStataDoFiles.py STARTYEAR STOPYEAR
```

### Download data files
Download data files listed in [data/ipedsfiles.json](data/ipedsfiles.json) for a given range of years.
```python
python3 scripts/downloadData.py STARTYEAR STOPYEAR
```
### Assemble a master dictionary
Downloads and extracts dictionary files for given years from [data/ipedsfiles.json](data/ipedsfiles.json), compiles the .xls and .xlsx dictionaries into [data/dictionary.csv](data/dictionary.csv)
* Note: pre-2009 dictionaries are saved in .html files and are not parsed here.
```python
python3 scripts/makeDictionary.py STARTYEAR STOPYEAR
```
### Assemble a master data label repository
Reads re-naming conventions from do files and creates a master list of data labels and values by year and file for later matching 
```python
python3 scripts/extract_and_compile_labels.py STARTYEAR STOPYEAR
```



### Get column names
Get column names from downloaded files for a given range of years and save in a json.
```python
python3 scripts/getColumnNames.py STARTYEAR STOPYEAR
```
