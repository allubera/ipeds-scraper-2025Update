import pandas as pd
import json

# Load JSON file
with open('data/ipedsfiles.json', "r") as file:
    data = json.load(file)

# Convert JSON to DataFrame
df = pd.DataFrame(data)

# Save DataFrame to Excel
df.to_excel("data/ipedsDescriptions.xlsx", index=False)

print("JSON data successfully converted to ipedsDescriptions.xlsx")
