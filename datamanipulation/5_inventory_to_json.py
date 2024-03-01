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
                "product_id": row["item_id"],
                "title": format_string(row["item_title"]),
                "seller": format_string(row["seller_name"]),
                "seller_rating": row["seller_rating"],
                "price":row["item_price"],
                "condition": row["item_condition"],
            }
            json_data.append(product)
            count+=1

    return json_data

if __name__ == "__main__":
    csv_file = "datamanipulation/data/4_inventory.csv"  
    out_filename = 'datamanipulation/data/inventory.json'
    out_filename_jsonlines = 'datamanipulation/data/inventory_jsonlines.json'

    json_list = csv_to_json_list(csv_file)
    with open(out_filename, 'w') as outfile:
      outfile.write(json.dumps(json_list))
    with open(out_filename_jsonlines, 'w') as outfile:
        for item in json_list:
            outfile.write(json.dumps(item))
            outfile.write("\n")
