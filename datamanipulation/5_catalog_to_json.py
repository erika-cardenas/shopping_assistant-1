import csv
import json
import random
import re 

def format_string(text):
  # Regular expression pattern to match letters and numbers (alphanumeric)
  regex = r"[^a-zA-Z0-9\s]"  
  result = re.sub(regex, '', text)  
  return result

def csv_to_json_list(csv_file):
    json_data = []
    count = 1

    with open(csv_file, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            product = {
                "id": "id_"+str(count),
                "product_id": row["id"],
                "title": format_string(row["title"]),
                "category": format_string(row["product_type"]),
                "link": row["image_link"],
                "description":format_string(row["description"]),
                "color": row["color"],
            }
            json_data.append(product)
            count+=1

    return json_data

if __name__ == "__main__":
    csv_file = "datamanipulation/data/3_enriched_catalog.csv"  
    out_filename = 'datamanipulation/data/catalog.json'
    out_filename_jsonlines = 'datamanipulation/data/catalog_jsonlines.json'

    json_list = csv_to_json_list(csv_file)
    with open(out_filename, 'w') as outfile:
      outfile.write(json.dumps(json_list))
    with open(out_filename_jsonlines, 'w') as outfile:
        for item in json_list:
            outfile.write(json.dumps(item))
            outfile.write("\n")
