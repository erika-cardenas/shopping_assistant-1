import os, json
import uuid 
from google.cloud import storage, pubsub_v1
import functions_framework

PROJECT_ID = os.getenv("PROJECT_ID")
BUCKET = os.getenv("BUCKET")
TOPIC = os.getenv("TOPIC", "thumbnail_generation")

def create_gcs(filename):
    """Creates an empty blob in a Google Cloud Storage bucket."""
    storage_client = storage.Client(project=PROJECT_ID)
    bucket = storage_client.bucket(BUCKET)
    blob = bucket.blob(filename)
    return blob.public_url

# Construct your message data
def publish_message(link, data):
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(PROJECT_ID, TOPIC)

    message_data = {
        "link": link,
        "data": data 
    }
    message = json.dumps(message_data)
    # Data must be serialized as bytestrings for transmission
    data_bytes = json.dumps(message_data).encode('utf-8')  
 

    # Publish the message
    future = publisher.publish(topic_path, data=data_bytes)
    message_id = future.result()  # Optionally get the message ID

    print(f"Published message with ID: {message_id}")


local_testing_data =[
            {
                "title": "Large item",
                "link": "https://shop.googlemerchandisestore.com/store/20190522377/assets/items/images/GGCPGBJB162499.jpg"
            },
             {
                "title": "Other Large item",
                "link": "https://shop.googlemerchandisestore.com/store/20190522377/assets/items/images/GGCPGBJB162499.jpg"
            },
            {
                "title": "Other Large item",
                "link": "https://shop.googlemerchandisestore.com/store/20190522377/assets/items/images/GGCPGBJB162499.jpg"
            },
            {
                "title": "Other Very Large item",
                "link": "https://shop.googlemerchandisestore.com/store/20190522377/assets/items/images/GGCPGBJB162499.jpg"
            },
            {
                "title": "Other Large item",
                "link": "https://shop.googlemerchandisestore.com/store/20190522377/assets/items/images/GGCPGBJB162499.jpg"
            },
            {
                "title": "Other Large item",
                "link": "https://shop.googlemerchandisestore.com/store/20190522377/assets/items/images/GGCPGBJB162499.jpg"
            }
        ]

import time
def test_image_create_local():
    start_time = time.perf_counter()
    filename = f"static_test_{uuid.uuid4()}.jpg"
    url = create_gcs(filename)
    end_time = time.perf_counter()
    print("create gcs: ", end_time-start_time)
    
    start_time = time.perf_counter()
    publish_message(url, local_testing_data)
    end_time = time.perf_counter()
    print("publish message: ", end_time-start_time)
    print(url)
    return {"url": url}

@functions_framework.http
def http_create_thumbnail(request):
    data = request.get_json()
    filename = f"thumbnail_v2_{uuid.uuid4()}.jpg"
    url = create_gcs(filename)
    publish_message(url, data)
    return {"url": url}


test_image_create_local()