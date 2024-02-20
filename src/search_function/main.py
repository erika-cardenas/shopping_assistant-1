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
import requests

project_id = os.getenv("PROJECT_ID")
location = os.getenv("LOCATION")                    
data_store_id = os.getenv("SEARCH_DATA_STORE_ID")
thumbnail_url = os.getenv("THUMBNAIL_URL")
num_results_approx = os.getenv("EXPECTED_RESULTS", 6)
def search_sample(
    project_id: str,
    location: str,
    data_store_id: str,
    search_query: str,
    page_size: int,
) -> List[discoveryengine.SearchResponse]:
    #  For more information, refer to:
    # https://cloud.google.com/generative-ai-app-builder/docs/locations#specify_a_multi-region_for_your_data_store
    client_options = (
        ClientOptions(api_endpoint=f"{location}-discoveryengine.googleapis.com")
        if location != "global"
        else None
    )

    # Create a client
    client = discoveryengine.SearchServiceClient(client_options=client_options)

    # The full resource name of the search engine serving config
    # e.g. projects/{project_id}/locations/{location}/dataStores/{data_store_id}/servingConfigs/{serving_config_id}
    serving_config = client.serving_config_path(
        project=project_id,
        location=location,
        data_store=data_store_id,
        serving_config="default_config",
    )

    # Optional: Configuration options for search
    # Refer to the `ContentSearchSpec` reference for all supported fields:
    # https://cloud.google.com/python/docs/reference/discoveryengine/latest/google.cloud.discoveryengine_v1.types.SearchRequest.ContentSearchSpec
    content_search_spec = discoveryengine.SearchRequest.ContentSearchSpec(
        # For information about snippets, refer to:
        # https://cloud.google.com/generative-ai-app-builder/docs/snippets
        snippet_spec=discoveryengine.SearchRequest.ContentSearchSpec.SnippetSpec(
            return_snippet=True
        ),
        # For information about search summaries, refer to:
        # https://cloud.google.com/generative-ai-app-builder/docs/get-search-summaries
        summary_spec=discoveryengine.SearchRequest.ContentSearchSpec.SummarySpec(
            summary_result_count=5,
            include_citations=True,
            ignore_adversarial_query=True,
            ignore_non_summary_seeking_query=True,
        ),
    )

    # Refer to the `SearchRequest` reference for all supported fields:
    # https://cloud.google.com/python/docs/reference/discoveryengine/latest/google.cloud.discoveryengine_v1.types.SearchRequest
    request = discoveryengine.SearchRequest(
        serving_config=serving_config,
        query=search_query,
        page_size=page_size,
        content_search_spec=content_search_spec,
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
def create_unique_results(data):
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
                "sellers": [],
                "category":  result["category"],
                "description": result["description"],
                "html_image": "<img src="+ result["link"] + " width=300px >"
                }            

            # Add unique result to the list
            unique_results.append(unique_result)

        # Add seller name to the corresponding unique result
        seller = {
            "seller_name": result["seller_name"],
            "seller_rating": float(result["seller_rating"]),
            "item_price": float(result["price"]),
            "item_condition": result["condition"],
        }   

        unique_results[-1]["sellers"].append(seller)
    return unique_results

def extract_results(json_string):
    data = json.loads(json_string)  # Parse the JSON string

    # Assuming "results" is a top-level field
    if "results" in data:
        new_data = {"results": data["results"]} 
        return new_data # json.dumps(new_data)  # Serialize back to JSON
    else:
        return None  # Or another handling mechanism if "results" not found

@functions_framework.http
def http_search(request):
    request_args = request.args

    if "query" in request_args:
        query = request_args.get("query")
        if query=="":
            query = "merch"
   
    final_response = get_results(query)
    return final_response

def get_html_products(query, unique_results):
    title_string = "<h3>"+ query+ "</h3>" + "<hr>"
    result_string = ""
    for result in unique_results:
        item_string =  "<h4>" + result["title"] + "<h4> " + "<p>" + result["description"]+ "</p>" "<hr>"
        result_string+= item_string
    return title_string  + result_string

def get_html_thumbnail(thumbnail_url):
    html_string = "<img src="+ thumbnail_url + " width=500px >"
    return html_string


def get_results(query_string):
    results = search_sample(project_id, location, data_store_id, query_string, num_results_approx*3)
    if results is None:
        return {"thumbnail": "", "html_products":"", "results":[]}
    formatted_results = create_unique_results(results)
    requests.post(thumbnail_url, data=json.dumps(formatted_results), headers={'Content-type': 'application/json'})    
    final_response = {"results": formatted_results, "html_products":get_html_products(query_string,formatted_results)} 
    return final_response
results = get_results("green journals")
print(results)