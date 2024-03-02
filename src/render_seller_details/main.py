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


import os
import requests
import functions_framework


LOCAL = os.getenv("LOCAL", "false")
INVENTORY_URL = os.getenv("INVENTORY_URL")

def generate_webhook_response(payload, template="seller-template"):
  '''
  This works to return a custom payload sucessfully in DFCX -> Flow -> WebhookResponse format.

  Parameters:
    payload: The data being returned
    template: The Custom template for DF Messenger to use to render the rich content. Default is retail-template.
  Returns:
    response: The response object in WebhookResponse format.
  '''

  response = {
    "fulfillmentResponse": {
        "messages": [
            {
                "payload": {
                    "richContent": [
                        [
                            {
                                "type": "custom_template",
                                "name": template,
                                "payload": {
                                    "items": payload
                                }
                            }
                        ]
                    ]
                }
            }
        ]
    },
    "sessionInfo": {
        "parameters": {
            "seller_details": payload
        }
    }
  }

  return response


@functions_framework.http
def http_format_sellers(request):
    request_json = request.get_json()
    response_json = format_sellers(request_json)
    return response_json

def format_sellers(request_json):    
    print("incoming request: ", request_json)
    if 'sessionInfo' in request_json and request_json['sessionInfo']:
        parameters = request_json['sessionInfo']['parameters']
        del parameters["product_details"]
    print("parameters", parameters)
    selected_product = parameters["selected_product_id"]
    query_params = {"product_id": selected_product}
    if "min_rating" in parameters and parameters["min_rating"] != "":
        query_params["min_rating"] = parameters["min_rating"]
    if "max_price" in parameters and parameters["max_price"] != "":
        query_params["max_price"] = parameters["max_price"]
    if "condition" in parameters and parameters["condition"] != "":
        query_params["condition"] = parameters["condition"]

    search_response = requests.get(DETAILS_SEARCH_URL, params=query_params)
    search_response_json = search_response.json()
    
    response = generate_webhook_response(search_response_json)
    print(response)
    return response

# ### LOCAL TESTING
# if LOCAL=="true":
#     data = {'detectIntentResponseId': '6811a2d3-11da-4ebb-86f4-02ef0fb59755', 
#             'intentInfo': {'lastMatchedIntent': 'projects/retail-vertical-project/locations/us-central1/agents/cee5a831-c4f0-41e9-9b2e-f767b0f4ad2d/intents/00000000-0000-0000-0000-000000000000', 
#                            'displayName': 'Default Welcome Intent', 'confidence': 1.0}, 
#                            'pageInfo': {'currentPage': 'projects/retail-vertical-project/locations/us-central1/agents/cee5a831-c4f0-41e9-9b2e-f767b0f4ad2d/flows/a5e97c7f-3d0f-4f31-a53d-7910c95de191/pages/START_PAGE', 'displayName': 'Start Page'}, 
#                            'sessionInfo': 
#                            {'session': 'projects/retail-vertical-project/locations/us-central1/agents/cee5a831-c4f0-41e9-9b2e-f767b0f4ad2d/sessions/dd01fd-d38-633-b58-1009e5185', 
#                             'parameters':
#                                            {
#                                                'selected_product_id':"GGOEGAEJ028915",'max_price': "1000", "min_rating":"2", "condition":"new",
#                                                'products': [{'description': 'These socks feature the Google logo on the side and a cityscape of Seattle on the front', 'link': 'https://shop.googlemerchandisestore.com/store/20160512512/assets/items/images/GGOEDAXQ225310.jpg', 'title': 'WA Classic Cotton Crew Socks'}, 
#                                                                        {'description': 'This pack of three socks from Happy Socks features a variety of colorful and fun designs including dinosaurs polka dots and stripes', 'link': 'https://shop.googlemerchandisestore.com/store/20160512512/assets/items/images/GGOEGAXA185899.jpg', 'title': 'Google Crew Socks  3 pack'}, 
#                                                                        {'description': 'These Google socks are made from a soft and comfortable cotton blend They feature a black background with a colorful polka dot pattern and the Google logo on the top Theyre perfect for everyday wear', 'link': 'https://shop.googlemerchandisestore.com/store/2016051'}]}}, 
#                                                                         'fulfillmentInfo': {'tag': 'messenger'}, 
#                                                                         'messages': [{'payload': {'text': '{"description":"These socks feature the Google logo on the side and a cityscape of Seattle on the front","link":"https://shop.googlemerchandisestore.com/store/20160512512/assets/items/images/GGOEDAXQ225310.jpg","title":"WA Classic Cotton Crew Socks"}, {"description":"This pack of three socks from Happy Socks features a variety of colorful and fun designs including dinosaurs polka dots and stripes","link":"https://shop.googlemerchandisestore.com/store/20160512512/assets/items/images/GGOEGAXA185899.jpg","title":"Google Crew Socks  3 pack"}, {"description":"These Google socks are made from a soft and comfortable cotton blend They feature a black background with a colorful polka dot pattern and the Google logo on the top Theyre perfect for everyday wear","link":"https://shop.googlemerchandisestore.com/store/2016051"}'}, 
#                                                                                       'responseType': 'HANDLER_PROMPT', 'source': 'VIRTUAL_AGENT'}], 
#                                                                                       'text': 'show me socks', 'languageCode': 'en'}
#     formatted = format_sellers(data)
