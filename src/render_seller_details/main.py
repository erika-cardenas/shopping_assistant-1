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
DETAILS_SEARCH_URL = os.getenv("DETAILS_SEARCH_URL", "https://us-central1-ccai-demo-414406.cloudfunctions.net/search_details_v2")


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
def http_in_inventory(request):
    print("Webhook Started")
    request_json = request.get_json()
    response_json = do_your_thing(request_json)
    return response_json

def do_your_thing(request_json):    
    print("incoming request: ", request_json)
    if 'sessionInfo' in request_json and request_json['sessionInfo']:
        parameters = request_json['sessionInfo']['parameters']

    selected_product = parameters["selected_product"]
    query_params = {"query": selected_product}
    search_response = requests.get(DETAILS_SEARCH_URL, params=query_params)
    search_response_json = search_response.json()
    
    response = generate_webhook_response(search_response_json)
    return response

### LOCAL TESTING
if LOCAL=="true":
    # do nothing
    print(LOCAL)