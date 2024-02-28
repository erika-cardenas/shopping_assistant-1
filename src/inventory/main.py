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
import os, string
from typing import  List
from google.api_core.client_options import ClientOptions
from google.cloud import discoveryengine_v1beta as discoveryengine
from google.protobuf.json_format import MessageToJson

import functions_framework

LOCAL = os.getenv("LOCAL", "false")

inventory = ["pens","shirts", "tees", "tshirts", "sweaters", "hoodies", \
             "sweatshirts", "socks", "caps", "hats", "journals", "glasses", "shades", \
                "notebooks", "keychains" , "stickers", "magnets", "bags", "backpacks", "bottles" \
                    "blankets, mugs, cups, plushies, plushy, toys" ]

inventory_has_gender_specific_options = ["shirts", "tees", "tshirts", "sweaters", "hoodies", \
             "sweatshirts"]

def format_string(text):
    allowed_chars = set(string.ascii_lowercase + " ")  # Set of allowed characters (lowercase letters)
    result = ''.join(char for char in text.lower() if char in allowed_chars)
    return result


def is_part_of_word(word):
    for list_word in inventory:
        if list_word in word:
            return True
    return False

def is_gendered(word):
    for list_word in inventory_has_gender_specific_options:
        if list_word in word:
            return True
    return False


def get_details(query):
    item = format_string(query)
    result = {"item": "false", "gendered": "false", "name": item }
    if  is_part_of_word(item):
        result["item"] = "true"
        result ["name"] = item
    else:
        return result
    if is_gendered(item):
        result["gendered"] = "true"
    return result


@functions_framework.http
def http_check_inventory(request):
    request_args = request.args

    if "query" in request_args:
        title = request_args.get("query")
        result = get_details(title)
        return result
    return {}

@functions_framework.http
def http_get_inventory(request):
    return inventory

#### LOCAL TESTING
if LOCAL=="true":

    results = get_details("android t-shirts")
    i = http_get_inventory("")
    print(results)