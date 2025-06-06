#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 17 13:29:34 2025
Using do files downloaded from IPEDS to get interpretable data.
@author: amberlubera
"""

import os
import re
import argparse
import pandas as pd

parser = argparse.ArgumentParser()
parser.add_argument("start", help="start year", type=int)
parser.add_argument("stop", help="stop year", type=int)
args = parser.parse_args()

def extract_and_compile_labels(start, stop, output_excel='data/labels.xlsx'):
    print("*****************************")
    print("Assembling master labels Dict")
    print("*****************************")
    
    all_labels = []

    for i in range(start, stop):
        dict_path = f'dofiles/{i}/'
        if not os.path.exists(dict_path):
            continue

        for file in os.listdir(dict_path):
            if file.endswith(".do"):
                print(f"Processing {i} {file}")
                file_path = os.path.join(dict_path, file)

                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        do_file_content = f.read()
                except UnicodeDecodeError:
                    print(f"Warning: {file_path} contains non-UTF-8 characters. Trying alternative encoding.")
                    with open(file_path, 'r', encoding='latin-1') as f:
                        do_file_content = f.read()

                # Extract label definitions
                for match in re.finditer(r'label define\s+([a-zA-Z_][a-zA-Z0-9_]*)\s+(.*)', do_file_content):
                    label_name = match.group(1)
                    value_labels_str = match.group(2)

                    # Extract value-label pairs
                    for pair in re.findall(r'(\d+)\s+"([^"]*)"', value_labels_str):
                        value, label = pair
                        all_labels.append([i, file, label_name, int(value), label])

    # Save to Excel file
    df = pd.DataFrame(all_labels, columns=['year', 'filename', 'label_name', 'value', 'label'])
    os.makedirs("data", exist_ok=True)  # Ensure 'data/' directory exists
    df.to_excel(output_excel, index=False)

    print(f"Labels successfully saved to {output_excel}")

extract_and_compile_labels(args.start, args.stop)

''' 
*The following are the possible values for the item imputation field variables
*A Not applicable
*B Institution left item blank
*C Analyst corrected reported value
*D Do not know
*G Data generated from other data values
*H Value not derived - data not usable
*J Logical imputation
*K Ratio adjustment
*L Imputed using the Group Median procedure
*N Imputed using Nearest Neighbor procedure
*P Imputed using Carry Forward procedure
*R Reported
*Z Implied zero
''' 
# I also found this note which we will need to think about. O noticed that this was the same in many files. 

# Expected output:
# {'gender': {1: 'Male', 2: 'Female'}, 'age_group': {1: '
