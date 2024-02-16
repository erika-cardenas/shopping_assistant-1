""" Google Cloud Function to return JSON or HTML from search response
This sample uses the Retail API with client libraries

This can be used for doing AJAX/client side calls to get search results
and render in a div.

Configure the GCF to use a service account which has Retail Editor Role
"""

import flask
import google.auth
import json
import random

from firebase_admin import db, initialize_app
from firebase_functions import https_fn
from flask import request
from google.cloud import retail_v2
from google.cloud import retail
from google.oauth2 import service_account
from google.protobuf.json_format import MessageToDict
from google.protobuf.json_format import MessageToJson


initialize_app()
app = flask.Flask(__name__)

PROJECT_NUMBER='413052074894'

credentials, project = google.auth.default(
    scopes=[
      'https://www.googleapis.com/auth/cloud-platform'
    ]
)
auth_req = google.auth.transport.requests.Request()

client = retail_v2.SearchServiceClient(credentials=credentials)
predict_client = retail_v2.PredictionServiceClient(credentials=credentials)
product_client = retail_v2.ProductServiceClient(credentials=credentials)


@app.post("/search")
def search():
  app.logger.warning("REACHED /SEARCH")
  request_json = request.get_json(silent=False)
  app.logger.warning("REQUEST: %s", request_json)

  session_parameters = request_json['sessionInfo']['parameters']
  # Capture the user's search query.
  query = session_parameters['query']
  # Capture optional number of results to return, if provided.
  num_results = 2
  if "num_results" in session_parameters:
    num_results = int(session_parameters["num_results"])
  session_id = get_session_id(request_json)
  visitorid = session_id
  placement = 'default_search'

  search_request = {
    'placement':
      'projects/' + PROJECT_NUMBER +
      '/locations/global/catalogs/default_catalog/placements/' + placement,
    'query': query,
    'visitor_id': visitorid,
    'page_size': num_results,
    'query_expansion_spec': {
      'condition': 'AUTO'
    }
  }

  response = client.search(search_request)

  res = MessageToDict(response._pb)
  app.logger.warning("RAW RESULT: %s", res["results"])
  data = get_minimal_payload(res["results"])
  app.logger.warning("RESULT: %s", data)
  wh_response = generate_webhook_response(data)

  return flask.jsonify(wh_response)


@app.post("/get_product")
def get_product():
  app.logger.warning("REACHED /GET_PRODUCT")
  request_json = request.get_json(silent=False)
  app.logger.warning("REQUEST: %s", request_json)

  session_parameters = request_json['sessionInfo']['parameters']
  product_ids = session_parameters['product_ids']
  app.logger.warning("PRODUCT_IDS: %s", product_ids)

  data = []
  for product_name in product_ids:  
    product = product_client.get_product(name=product_name)
    # This is temporary hack to get around https://b.corp.google.com/issues/277344760#comment28
    # so that MessageToDict dosn't throw an error on productId being camel case.
    product.retrievable_fields = None
    res = MessageToDict(product._pb)
    obj = {
      "product": res
    }
    data.append(obj)

  app.logger.warning("RESULT: %s", data)
  wh_response = generate_webhook_response(data)

  return flask.jsonify(wh_response)


@app.post("/similar")
def similar():
    app.logger.warning("REACHED /SIMILAR")
    request_json = request.get_json(silent=False)
    app.logger.warning("REQUEST: %s", request_json)

    session_parameters = request_json["sessionInfo"]["parameters"]
    session_id = get_session_id(request_json)
    visitor_id = session_id
    product_id = session_parameters["product_id"]

    page_size = 3
    placement = 'similar'

    user_event = {
        'event_type': 'detail-page-view',
        'visitor_id': visitor_id,
        'product_details': [
            {
                'product': {
                    'id': product_id
                }
            }
        ]
    }

    predict_request = {
        'placement': 'projects/' + PROJECT_NUMBER + '/locations/global/catalogs/default_catalog/placements/' + placement,
        'user_event': user_event,
        'page_size': page_size,
        'filter': 'filterOutOfStockItems',
        'params': {
            'returnProduct': True,
            'returnScore': True
        }
    }

    response = predict_client.predict(predict_request)
    res = MessageToDict(response._pb)
    data = res["results"]
    # Remove unnecessary 'metadata' parent nodes to normalize output between /search and /similar results.
    for i in range(len(data)):
      data[i] = data[i]["metadata"]
    data = get_minimal_payload(data)
    app.logger.warning("RESULT: %s", data)
    wh_response = generate_webhook_response(data)

    return flask.jsonify(wh_response)


@app.post("/get_ratings")
def get_ratings():
  app.logger.warning("REACHED /GET_REVIEWS")
  request_json = request.get_json(silent=False)
  app.logger.warning("REQUEST: %s", request_json)

  # Eventually this should look up reviews based on the product ID provided.
  session_parameters = request_json['sessionInfo']['parameters']
  product_ids = []
  if "shown_products" in session_parameters:
    product_ids = session_parameters['shown_products']
  app.logger.warning("SHOWN_PRODUCTS: %s", product_ids)
  

  # For now for demo purposes we are just returning the same example reviews regardless of the product.
  reviews = []
  review1 = {
    "product_id": "projects/299022464847/locations/global/catalogs/default_catalog/branches/2/products/GSAB59ARKMF7FXB0",
    "user": "Briene Sanje",
    "rating": "3",
    "desc": """It fit real well at first, I suppose. However after a few hours into the night
               I started to wish I had gone up a size or two. Every couple minutes I had to
               re-adjust the saree. It wasn't a cute look on the dance floor haha. Wish I had
               size up, otherwise I've no other regrets.""",
    "title": "Golden Tangerine Silk Saree"
  }
  review2 = {
    "product_id": "projects/299022464847/locations/global/catalogs/default_catalog/branches/2/products/GSAB59ARKMF7FXB0",
    "user": "Jenny Rahme",
    "rating": "5",
    "desc": """As a first-time saree buyer, I must say, I am head over heels in love with my
               purchase! The moment I delicately draped the saree around me, I felt an instant
               connection, as if it was meant to be.
               What impressed me the most was the comfort it provded throughout the day.""",
    "title": "Golden Tangerine Silk Saree"
  }
  review3 = {
    "product_id": "projects/299022464847/locations/global/catalogs/default_catalog/branches/2/products/GSAB59ARKMF7FXB1",
    "user": "Nadine Bhakta",
    "rating": "4",
    "desc": """I recently had the pleasure of wearing the most enchanting amethyst purple saree
               for a special occasion, and let me tell you, heads turned and compliments poured
               in all night long!
               The fit was mostly great, hugging my curves in all the right places and accentuating
               my silhouette.""",
    "title": "Royal Amethyst Saree"
  }
  review4 = {
    "product_id": "projects/299022464847/locations/global/catalogs/default_catalog/branches/2/products/GSAB59ARKMF7FXB1",
    "user": "Anjali Gupta",
    "rating": "5",
    "desc": """I recently purchased a Royal Amethyst saree from this store, and I must say, it's
               absolutely stunning! The silk is of premium quality, and the intricate silver-thread
               work is a testament to the remarkable craftsmanship. The saree drapes beautifully,
               and the rich color hasn't faded a bit even after a few wears.""",
    "title": "Royal Amethyst Saree"
  }
  # review5 = {
  #   "product_id": "",
  #   "user": "Priya Singh",
  #   "rating": "4",
  #   "desc": """This saree is a lovely addition to my collection. The fabric is light and breezy,
  #              ideal for the summer season, and the subtle embroidery adds a touch of grace. I
  #              was particularly impressed with the color palette — it was exactly as shown on
  #              their website. The customer service was also commendable; they were very helpful
  #              in assisting me with my queries. The only downside is that the saree requires
  #              delicate handling, but that's a small price to pay for such elegance. Will
  #              definitely shop here again!"""
  # }
  # review6 = {
  #   "product_id": "",
  #   "user": "Sunita Patel",
  #   "rating": "2",
  #   "desc": """I'm usually a fan of this store's saree collection, but my latest purchase was a bit
  #              of a letdown. I ordered a Banarasi saree, and while the design was beautiful, the
  #              fabric quality did not meet my expectations. After just one wash, the saree's fabric 
  #              felt rough, and the colors started to fade. Also, I noticed a few loose threads along
  #              the border. It's disheartening because I've always loved their designs, but this
  #              experience has made me question the consistency of their quality. I hope they address
  #              these issues, as I've always admired their collection in the past."""
  # }
  reviews.append(review1)
  reviews.append(review2)
  reviews.append(review3)
  reviews.append(review4)
  # reviews.append(review5)
  # reviews.append(review6)

  # Return 4 reviews selected at random.
  # selected_reviews = random.sample(reviews, 4)
  # Return reviews that match the ids provided in shown_products
  filtered_reviews = [review for review in reviews if review["product_id"] in product_ids]
  app.logger.warning("RESULT: %s", filtered_reviews)
  wh_response = generate_webhook_response(filtered_reviews, template="review-template")

  return flask.jsonify(wh_response)

@app.post("/user_info")
def user_info():
  app.logger.warning("REACHED /USER_INFO")
  user_info = {
    "delivery_address": "638 Maple Street, Apt 11, Cupertino, CA 95014",
    "payment_info": "**********4111",
    "contact_number": "416-555-6704",
    "email": "poetry_reader456@gmail.com"
  }

  wh_response = generate_webhook_response(user_info)
  
  return flask.jsonify(wh_response)


@app.get("/no_op")
def no_op():
  app.logger.warning("REACHED /NO_OP")
  return flask.jsonify(True)


def get_minimal_payload(resp_json):
  results = []
  for item in resp_json:
    output = {"product": {}}
    if "id" in item:
      output["product"]["id"] = item["id"]
    else:
      output["product"]["id"] = item["product"]["id"]
    output["product"]["title"] = item["product"]["title"]
    output["product"]["name"] = item["product"]["name"]
    output["product"]["priceInfo"] = item["product"]["priceInfo"]
    output["product"]["images"] = [item["product"]["images"][0]]
    results.append(output)
  
  return results


def get_session_id(request_json):
  session_path = request_json['sessionInfo']['session']
  session_id = session_path.split('/')[-1]

  return session_id


def generate_webhook_response(payload, template="retail-template"):
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
            "results": payload
        }
    }
  }

  return response


@https_fn.on_request()
def main(req: https_fn.Request) -> https_fn.Response:
  credentials.refresh(auth_req)
  with app.request_context(req.environ):
    return app.full_dispatch_request()

