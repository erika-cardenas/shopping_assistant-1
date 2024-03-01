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
from typing import  List
from google.api_core.client_options import ClientOptions
from google.cloud import discoveryengine_v1beta as discoveryengine
from google.protobuf.json_format import MessageToJson

import functions_framework

project_id = os.getenv("PROJECT_ID")
location = os.getenv("LOCATION")                    
data_store_id = os.getenv("INVENTORY")
num_results_approx = os.getenv("EXPECTED_RESULTS", 10)
LOCAL = os.getenv("LOCAL", "false")

def search_dataset(
    project_id: str,
    location: str,
    data_store_id: str,
    query: str,
    page_size: int,
) -> List[discoveryengine.SearchResponse]:
   client_options = (
        ClientOptions(api_endpoint=f"{location}-discoveryengine.googleapis.com")
        if location != "global"
        else None
    )
   client = discoveryengine.SearchServiceClient(client_options=client_options)
   serving_config = client.serving_config_path(
        project=project_id,
        location=location,
        data_store=data_store_id,
        serving_config="default_config",
    )
   
   request = discoveryengine.SearchRequest(
        serving_config=serving_config,
        query=query,
        page_size=page_size,
        # query_expansion_spec=discoveryengine.SearchRequest.QueryExpansionSpec(
        #     condition=discoveryengine.SearchRequest.QueryExpansionSpec.Condition.AUTO,
        # ),
        # spell_correction_spec=discoveryengine.SearchRequest.SpellCorrectionSpec(
        #     mode=discoveryengine.SearchRequest.SpellCorrectionSpec.Mode.N
        # ),
    )
   response = client.search(request)
   json_response = extract_results(MessageToJson(response._pb))
   return json_response

def format_title(text):
  # Regular expression pattern to match letters and numbers (alphanumeric)
  regex = r"[^a-zA-Z0-9\s]"  
  result = re.sub(regex, '', text)  
  return result

def format_search_results(data, max_price, min_rating, condition):
    results = []
    for d in data["results"]:
        document = d["document"]["structData"]
        formatted_title = format_title(document["title"])       
        result = {
            "title": formatted_title,
            "seller": document["seller"],
            "seller_rating": float(document["seller_rating"]),
            "price":float(document["price"]),
            "condition": document["condition"],
            "product_id": document["product_id"],
            }  
        if result["price"] < float(max_price) and result["seller_rating"]  > float(min_rating): 
            if condition == "":        
                results.append(result)
            elif result["condition"].lower() == condition.lower():
                results.append(result)

    return results

def extract_results(json_string):
    data = json.loads(json_string)  # Parse the JSON string
    # Assuming "results" is a top-level field
    if "results" in data:
        new_data = {"results": data["results"]} 
        return new_data # json.dumps(new_data)  # Serialize back to JSON
    else:
        return None  # Or another handling mechanism if "results" not found

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


#### WRAPPERS
def search_inventory(product_id, max_price, min_rating, condition):
    results = search_dataset(project_id=project_id, location=location, data_store_id=data_store_id, query=product_id, page_size = 10)
    if results is None:
        return ""
    formatted_results = format_search_results(results, max_price=max_price, min_rating=min_rating, condition=condition)
    return formatted_results


#### LOCAL TESTING
if LOCAL=="true":
    result = search_inventory("GGPIGAAB100413", 10000, 1, "")
    print(result)
