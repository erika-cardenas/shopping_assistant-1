# Copyright 2023 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

# [START genappbuilder_search]
import os, json, re
import pandas as pd
import functions_framework

num_results_approx = os.getenv("EXPECTED_RESULTS", 10)
LOCAL = os.getenv("LOCAL", "false")

def search_by_product_id(product_id):
    if product_id in df.index:
        result_df = df.loc[product_id]
        return result_df.to_dict(orient='records')  # Convert directly to JSON list
    else:
        return None
    
def format_title(text):
  # Regular expression pattern to match letters and numbers (alphanumeric)
  regex = r"[^a-zA-Z0-9\s]"  
  result = re.sub(regex, '', text)  
  return result

def format_search_results(data, max_price, min_rating, condition):
    results = []
    for document in data:
        formatted_title = format_title(document["title"])       
        result = {
            "title": formatted_title,
            "seller": document["seller"],
            "seller_rating": float(document["seller_rating"]),
            "price":float(document["price"]),
            "condition": document["condition"],
            }  
        if result["price"] < float(max_price) and result["seller_rating"]  > float(min_rating): 
            if condition == "":        
                results.append(result)
            elif result["condition"].lower() == condition.lower():
                results.append(result)

    return results

@functions_framework.http
def http_inventory(request):
    request_args = request.args
    max_price = 1000000
    min_rating = 1
    condition = ""
    if "product_id" in request_args:
        product_id = request_args.get("product_id")
    else:
        return []
    if "max_price" in request_args:
        max_price = request_args.get("max_price")
        print("max_price", max_price)
    if "min_rating" in request_args:
        min_rating = request_args.get("min_rating")
        print("min_rating", min_rating)
    if "condition" in request_args:
        condition = request_args.get("condition") 
    
    products = search_inventory(product_id, min_rating= min_rating, max_price=max_price, condition=condition)
    return products

def build_filter(filter, value):
    if value:  
        return f"{filter}:ANY(\"{value}\", \"{value.lower()}\", \"{value.capitalize()}\")"
    return "" 

def load_jsonlines_to_dataframe(fileName):
    data = []
    with open(fileName, 'r') as f:
        for line in f:
            data.append(json.loads(line))

    df = pd.DataFrame(data)
    return df    

#### WRAPPERS
def search_inventory(product_id, max_price, min_rating, condition):
    results = search_by_product_id(product_id=product_id)
    if results is None:
        return ""
    formatted_results = format_search_results(results, max_price=max_price, min_rating=min_rating, condition=condition)
    return formatted_results

main_file_dir = os.path.dirname(__file__)
df = load_jsonlines_to_dataframe(f"{main_file_dir}/inventory_jsonlines.json")
df.set_index('product_id', inplace=True)

#### LOCAL TESTING
if LOCAL=="true":
    result = search_inventory("GGOEGAEB189515", 10000, 1, "")
    print(result)
