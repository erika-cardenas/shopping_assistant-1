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
data_store_id = os.getenv("SEARCH_DATA_STORE_ID")
num_results_approx = os.getenv("EXPECTED_RESULTS", 5)
LOCAL = os.getenv("LOCAL", "false")

def search_dataset(
    project_id: str,
    location: str,
    data_store_id: str,
    search_query: str,
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
        query=search_query,
        page_size=page_size,
        query_expansion_spec=discoveryengine.SearchRequest.QueryExpansionSpec(
            condition=discoveryengine.SearchRequest.QueryExpansionSpec.Condition.AUTO,
        ),
        spell_correction_spec=discoveryengine.SearchRequest.SpellCorrectionSpec(
            mode=discoveryengine.SearchRequest.SpellCorrectionSpec.Mode.AUTO
        ),
    )
   response = client.search(request)
   json_response = extract_results(MessageToJson(response._pb))
   return json_response

def format_title(text):
  # Regular expression pattern to match letters and numbers (alphanumeric)
  regex = r"[^a-zA-Z0-9\s]"  
  result = re.sub(regex, '', text)  
  return result

def transform_url(url):
    filename = os.path.basename(url)  # Get the filename part
    name, ext = os.path.splitext(filename)  # Split into name and extension
    return name

def format_search_results(data):
# Iterate through each result
    unique_results = []
    for d in data["results"]:
        result = d["document"]["structData"]
        formatted_title = format_title(result["title"])
        # Check if title already exists in unique_results
        if not any(existing_result["title"] == formatted_title for existing_result in unique_results):
            # Extract relevant data for unique result
            unique_result = {
                "title": formatted_title,
                "link": result["link"],
                "description": result["description"],
                "product_id":result["product_id"]
                }            

            # Add unique result to the list
            unique_results.append(unique_result)

    return unique_results


def format_details(data):
    details = []
    for d in data["results"]:
        result = d["document"]["structData"]
        formatted_title = format_title(result["title"])
        detail = {
            "seller_name": result["seller_name"],
            "seller_rating": float(result["seller_rating"]),
            "item_price": float(result["price"]),
            "item_condition": result["condition"],
        }          
        details.append(detail)        
    return {"seller_details":details, "title":formatted_title}


def extract_results(json_string):
    data = json.loads(json_string)  # Parse the JSON string

    # Assuming "results" is a top-level field
    if "results" in data:
        new_data = {"results": data["results"]} 
        return new_data # json.dumps(new_data)  # Serialize back to JSON
    else:
        return None  # Or another handling mechanism if "results" not found

@functions_framework.http
def http_search_products(request):
    request_args = request.args

    if "query" in request_args:
        query = request_args.get("query")
        if query=="":
            query = "merch"
    products = get_products(query)
    return products

@functions_framework.http
def http_search_details(request):
    request_args = request.args

    if "query" in request_args:
        title = request_args.get("query")
        details = get_details(title)
        return details
    else:
        return {[]}


#### WRAPPERS
def get_products(query_string):
    results = search_dataset(project_id, location, data_store_id, query_string, num_results_approx*3)
    if results is None:
        return ""
    formatted_results = format_search_results(results)
    return formatted_results


def get_details(query_string):
    results = search_dataset(project_id, location, data_store_id, query_string, num_results_approx)
    if results is None:
        return ""
    formatted_results = format_details(results)
    final_response = formatted_results 
    return final_response

#### LOCAL TESTING
if LOCAL=="true":
    products = get_products("google cloud magnets")

    print(products)

    results = get_details("GGOEYOAA101499")

    print(results)