import csv
import json
import ast
import re 

def format_string(text):
  # Regular expression pattern to match letters and numbers (alphanumeric)
  regex = r"[^a-zA-Z0-9\s]"  
  result = re.sub(regex, '', text)  
  return result

def csv_to_json_list(csv_file):
    categories_gender = {}
    with open(csv_file, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            title = row["title"]
            if title != "" :
                has_gender = False
                if row["gender"] != "Unisex":
                    has_gender = True
                parts = title.split(" ")
                category = parts[-1]
                if category.lower() not in categories_gender:
                    categories_gender[category.lower()] = 0
                if has_gender:
                    categories_gender[category.lower()] += 1
                
    return categories_gender

if __name__ == "__main__":
    csv_file = "datamanipulation/data/3_enriched_catalog.csv"  
    out_filename = 'datamanipulation/data/producttypes.json'

    json_list = csv_to_json_list(csv_file)
    with open(out_filename, 'w') as outfile:
      outfile.write(json.dumps(json_list))
    