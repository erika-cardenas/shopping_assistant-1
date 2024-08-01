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

import os, json, re, ast
import weaviate
from weaviate.auth import AuthApiKey

from fastapi import FastAPI, Request
from pydantic import BaseModel
from typing import List

WEAVIATE_HTTP_URL = os.getenv('WEAVIATE_HTTP_URL')
WEAVIATE_GRPC_URL = os.getenv('WEAVIATE_GRPC_URL')
WEAVIATE_AUTH_API_KEY = os.getenv('WEAVIATE_AUTH_API_KEY')


app = FastAPI()

class WeaviateRequest(BaseModel):
    query: str

class WeaviateResponse(BaseModel):
    product_id: str
    title: str
    category: str
    link: str
    description: str
    color: str
    gender: str
    brand: str
    price: float
    size: list


@app.post("/search")
async def weaviate_hybrid_search(request: WeaviateRequest) -> List[WeaviateResponse]:
    weaviate_client = weaviate.connect_to_custom(
        http_host=WEAVIATE_HTTP_URL,
        http_port="80",
        http_secure=False,
        grpc_host=WEAVIATE_GRPC_URL,
        grpc_port="50051",
        grpc_secure=False,
        auth_credentials=AuthApiKey(WEAVIATE_AUTH_API_KEY)
) 
    
    catalog = weaviate_client.collections.get("Catalog")

    weaviate_result = catalog.query.hybrid(request.query, limit=5)

    response = []

    for item in weaviate_result.objects:
        result = WeaviateResponse()

        for key in item.keys():
            result.key = item[key]

        response.append(result)
    
    weaviate_client._connection.close()
    return {"response": response}












# from typing import  List
# from google.api_core.client_options import ClientOptions
# from google.cloud import discoveryengine_v1beta as discoveryengine
# from google.protobuf.json_format import MessageToJson

# import functions_framework

# project_id = os.getenv("PROJECT_ID")
# location = os.getenv("LOCATION")                    
# data_store_id = os.getenv("CATALOG")
# num_results_approx = os.getenv("EXPECTED_RESULTS", 4)
# LOCAL = os.getenv("LOCAL", "false")

# def search_dataset(
#     project_id: str,
#     location: str,
#     data_store_id: str,
#     query: str,
#     filters: str,
#     page_size: int,
# ) -> List[discoveryengine.SearchResponse]:
#    client_options = (
#         ClientOptions(api_endpoint=f"{location}-discoveryengine.googleapis.com")
#         if location != "global"
#         else None
#     )
#    client = discoveryengine.SearchServiceClient(client_options=client_options)
#    serving_config = client.serving_config_path(
#         project=project_id,
#         location=location,
#         data_store=data_store_id,
#         serving_config="default_config",
#     )
   
#    request = discoveryengine.SearchRequest(
#         serving_config=serving_config,
#         query=query,
#         page_size=page_size,
#         query_expansion_spec=discoveryengine.SearchRequest.QueryExpansionSpec(
#             condition=discoveryengine.SearchRequest.QueryExpansionSpec.Condition.AUTO,
#         ),
#         filter= filters,
#         spell_correction_spec=discoveryengine.SearchRequest.SpellCorrectionSpec(
#             mode=discoveryengine.SearchRequest.SpellCorrectionSpec.Mode.AUTO
#         ),
#     )
#    response = client.search(request)
#    json_response = extract_results(MessageToJson(response._pb))
#    return json_response

# def format_title(text):
#   # Regular expression pattern to match letters and numbers (alphanumeric)
#   regex = r"[^a-zA-Z0-9\s]"  
#   result = re.sub(regex, '', text)  
#   return result

# def format_search_results(data):
#     results = []
#     for d in data["results"]:
#         document = d["document"]["structData"]
#         formatted_title = format_title(document["title"])    
#         result = {
#             "title": formatted_title,
#             "link": document["link"],
#             "product_id":document["product_id"],
#             "description": document["description"], 
#             "color": document["color"],
#             "brand": document["brand"],
#             "gender": document["gender"]
#             }            
#         results.append(result)

#     return results

# def extract_results(json_string):
#     data = json.loads(json_string)  # Parse the JSON string
#     # Assuming "results" is a top-level field
#     if "results" in data:
#         new_data = {"results": data["results"]} 
#         return new_data # json.dumps(new_data)  # Serialize back to JSON
#     else:
#         return None  # Or another handling mechanism if "results" not found

# @functions_framework.http
# def http_catalog(request):
#     request_args = request.args
#     brand = ""
#     gender = "Unisex"
#     color = ""
#     if "product" in request_args:
#         product = request_args.get("product")
#     else:
#         return []
#     if "gender" in request_args:
#         gender = request_args.get("gender")
#     if "brand" in request_args:
#         brand = request_args.get("brand")
#     if "color" in request_args:
#         color = request_args.get("color") 
#     products = search_catalog(product, gender, brand, color, max_results=num_results_approx)
#     return products

# @functions_framework.http
# def http_product_check(request):
#     request_args = request.args
#     if "product" in request_args:
#         product = request_args.get("product")
#     else:
#         return {"inventory": False, "gendered": False}
    
#     return check_details(product=product)



# def build_filter(filter, value):
#     if value:  
#         return f"{filter}:ANY(\"{value}\", \"{value.lower()}\", \"{value.capitalize()}\")"
#     return "" 


# #### WRAPPERS
# def search_catalog(product, gender="", brand="", color ="", max_results=10):

#     filter_brand = build_filter("brand", brand)
#     filter_gender = build_filter("gender", gender)
#     filter_color = build_filter("color", color)

#     filters = " AND ".join(filter for filter in [filter_brand, filter_gender, filter_color] if filter)
    
#     results = search_dataset(project_id=project_id, location=location, data_store_id=data_store_id, query=product, filters=filters, page_size = max_results)
#     if results is None:
#         return ""
#     formatted_results = format_search_results(results)
#     return formatted_results

# def find_item(json_data, target_name):
#     items = json_data.get("items", [])  # Get the "items" array or an empty list if it doesn't exist
#     for item in items:
#         if item.get("name") == target_name:
#             return item
#     return None  # Item not found

# def check_details(product):
#     products = search_catalog(product, max_results=50)
#     if len(products) < 1:
#         return {"inventory": False, "gendered": False, "found": 0, "colors":{}, "brands": {}}
#     colors = {}
#     brands = {}
#     count_unisex = 0
#     for p in products:
#         color = ast.literal_eval(p['color'])
#         b = p["brand"].lower()
#         for c in color:
#             if c.lower() not in colors:
#                colors[c.lower()] = 1
#             else:
#                 colors[c.lower()] += 1
#         if b != "":
#             if b not in brands:
#                 brands[b] = 1
#             else:
#                 brands[b] += 1

        
#         if p["gender"] == "Unisex":
#             count_unisex+=1
#     if count_unisex > 0.75*len(products):
#         return {"inventory": True, "gendered": False, "found": len(products), "colors": colors, "brands": brands}
#     else:
#         return {"inventory": True, "gendered": True, "found": len(products), "colors": colors, "brands": brands}

# #### LOCAL TESTING
# if LOCAL=="true":
#     products = search_catalog("mugs", brand="google cloud")
#     print(products)
#     result = check_details("magnets")
#     print(result)
