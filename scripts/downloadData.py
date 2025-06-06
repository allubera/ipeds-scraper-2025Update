# Functions to get data from IPEDS csvs into R, format, join into one long data frame

library("jsonlite")
library("dplyr")
library("stringr")
library("openxlsx")
library("readxl")


ipedspath <- "C:/Users/allubera/Documents/PythonScripts/ipeds-scraper-2025/"
allfiles <- fromJSON(readLines("C:/Users/allubera/Documents/PythonScripts/ipeds-scraper-2025/data/ipedsfiles.json",warn=F))
datacols <- fromJSON(readLines("C:/Users/allubera/Documents/PythonScripts/ipeds-scraper-2025/data/ipedscolumns.json",warn = F))

# IPEDS dictionary
dictionary <- read.csv(paste(ipedspath, "data/dictionary.csv", sep=""), stringsAsFactors = F)

# Join colnames to file info, remove FLAGS datasets, using 1990+
ipeds <- left_join(datacols, allfiles, by = c("name", "year"))
ipeds <- ipeds %>% filter(!grepl("flags", name)) %>%
  filter(year >= 1990)

# There are a few duplicates in the way that IPEDS lists its files - remove them
ipeds <-ipeds[!duplicated(ipeds[,"path"]),]

# Search for a variable(s), return list of files that contain it
searchVars <- function(vars) {
  # Filter the full IPEDS metadata dataset info to just those containing your vars
  dt <- ipeds %>% filter(grepl(paste(vars, collapse='|'), columns, ignore.case = T))
  datalist <- split(dt, dt$name)
  return(datalist)
}

# Return the datasets containing the var(s) and selected the necessary columns
getData <- function(datalist, vars, keepallvars) {
  allvars <- tolower(c(vars, "unitid", "year"))
  for (i in seq_along(datalist)) {
    # Construct path to CSV
    csvpath <- datalist[[i]]$path
    fullpath <- paste(ipedspath, csvpath, sep="")
    name <- datalist[[i]]$name
    
    print(paste("Reading in ", fullpath, sep = ""))
    
    # Read CSV - some IPEDS CSVs are malformed, containing extra commas at the end of all rows but the headers
    # Need to handle these. Permanent solution - send list of malformed files to NCES. This is a known issue.
    row1 <- readLines(fullpath, n = 1)
    csvnames <- unlist(strsplit(row1,','))
    d <- read.table(fullpath, header = F, stringsAsFactors = F, sep=",", skip = 1, na.strings=c("",".","NA"))
    if (length(csvnames) == ncol(d)) {
      colnames(d) <- csvnames
    } else if (length(csvnames) == ncol(d) - 1) {
      colnames(d) <- c(csvnames, "xxx")
      print("Malformed CSV - extra column without header. Handled by R function but note for NCES.")
    } else if ((length(csvnames) != ncol(d) - 1) & length(csvnames) == ncol(d)) {
      print("Malformed CSV - unknown column length mismatch error. Note for NCES")
      print(path)
    }
    
    #d <- read.csv(fullpath, header=T, stringsAsFactors = F, na.strings=c("",".","NA"))
    # Give it a year variable
    d$year <- datalist[[i]]$year
    # All lowercase colnames
    colnames(d) <- tolower(colnames(d))
    
    # OPEID can be sometimes integer sometimes character - coerce to character
    if("opeid" %in% colnames(d))
    {
      d$opeid <- as.character(d$opeid)
    }
    if("f2a20" %in% colnames(d))
    {
      d$f2a20 <- as.character(d$f2a20)
    }
    # unitid sometimes has type issues
    d$unitid <- as.character(d$unitid)
    # Select just the need vars
    if(keepallvars == FALSE) {
      selects <- intersect(colnames(d), allvars)
      d <- d %>% select(one_of(selects))
    } else {
      d <- d %>% select(-starts_with("x"))
    }
    assign(name, d, envir = .GlobalEnv)
  }
}

# Bind rows to make one data frame
makeDataset <- function(vars) {
  dt <- ipeds %>% filter(grepl(paste(vars, collapse='|'), columns, ignore.case = T))
  ipeds_list <- lapply(dt$name, get)
  ipedsdata <- bind_rows(ipeds_list)
  ipedsdata <- ipedsdata %>% arrange(year, unitid)
  # Unit id back to numeric
  ipedsdata$unitid <- as.numeric(ipedsdata$unitid)
  return(ipedsdata)
}

# If desired (usually the case): Do all the things: search, get datasets
returnData <- function(myvars, keepallvars = FALSE) {
  dl <- searchVars(myvars)
  getData(dl, myvars, keepallvars)
  makeDataset(myvars)
}
rm(allfiles, datacols)

# Example - some institutional characteristics
instvars <- c("fips", "stabbr", "instnm", "sector", "pset4flg", "instcat", "ccbasic", "control", "deggrant", "opeflag", "opeind", "opeid", "carnegie", "hloffer")
institutions <- returnData(instvars)

# Make Data interpretable 
labels <- read_excel("C:/Users/allubera/Documents/PythonScripts/ipeds-scraper-2025/data/labels.xlsx")
labels <- na.omit(labels)
institutions <- na.omit(institutions)

#remove label title from everything 
labels$label_name = gsub("label_", "",labels$label_name)

institutions <- institutions %>%
  mutate(across(everything(), as.character))
labels <- labels %>%
  mutate(value = as.character(value),
         year = as.character(year))  # Ensure year is also character

# Function to replace values with labels safely
replace_values_with_labels <- function(data, labels) {
  for (col in colnames(data)) {
    if (col %in% labels$label_name) {  # Check if column exists in labels
      for (year in unique(na.omit(data$year))) {  # Remove NA values in year
        year_labels <- labels %>%
          filter(label_name == col & year == as.character(year))  # Ensure year is compared as character
        
        if (nrow(year_labels) > 0) {
          for (i in 1:nrow(year_labels)) {
            value_match <- year_labels$value[i]
            label_replacement <- year_labels$label[i]
            
            # Check if there are actual matches to avoid NA issues
            if (any(data$year == year & data[[col]] == value_match, na.rm = TRUE)) {
              data[data$year == year & data[[col]] == value_match, col] <- label_replacement
            }
          }
        }
      }
    }
  }
  
  return(data)
}

# Apply function
updated_data <- replace_values_with_labels(institutions, labels)


