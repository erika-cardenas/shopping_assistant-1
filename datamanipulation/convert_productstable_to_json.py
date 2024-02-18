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
                "title": format_string(row["title"]),
                "category": format_string(row["product_type"]),
                "price": row["cost"],
                "link": row["image_link"],
                "seller_name": format_string(row["seller_name"]),
                "seller_rating": row["seller_rating"],
                "short_description": format_string(row["short_description"]),
                "description":format_string(row["description"]),
                "color": row["color"],
                "condition": generate_product_condition()
            }
            json_data.append(product)
            count+=1

    return json_data

def generate_product_condition():
    conditions = ['new', 'good as new', 'used']  
    condition_probabilities = [0.6, 0.3, 0.1] 
    condition = random.choices(conditions, weights=condition_probabilities)[0] 
    return condition

if __name__ == "__main__":
    csv_file = "datamanipulation/final_catalog_with_keywords.csv"  
    json_list = csv_to_json_list(csv_file)

    # Save to a JSON file (optional)
    with open('datamanipulation/catalog.json', 'w') as outfile:
        for item in json_list:
            outfile.write(json.dumps(item))
            outfile.write('\n')