import requests, os, json
from PIL import Image, ImageDraw
import uuid 
from google.cloud import storage, pubsub_v1
import functions_framework

PROJECT_ID = os.getenv("PROJECT_ID")
BUCKET = os.getenv("BUCKET")
TOPIC = os.getenv("TOPIC", "thumbnail_generation")

os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

import requests
from PIL import Image, ImageDraw, ImageFont

import requests
from PIL import Image, ImageDraw, ImageFont

def create_image_grid(data):
    THUMB_SIZE = (250, 250) 
    PADDING_HORIZONTAL = 40
    PADDING_VERTICAL = 30 
    FONT_SIZE = 20    

    images = []
    max_title_width = 0

    # Download and resize images, find widest title
    for item in data:
        response = requests.get(item["link"], stream=True)
        response.raise_for_status()  
        img = Image.open(response.raw)
        img.thumbnail(THUMB_SIZE)
        images.append(img)
        max_title_width = max(max_title_width, len(item["title"]) * FONT_SIZE)

    # Calculate grid dimensions
    cols = 3 
    rows = (len(images) + cols - 1) // cols
    grid_width = (THUMB_SIZE[0] + PADDING_HORIZONTAL) * cols + PADDING_HORIZONTAL 
    grid_height = (THUMB_SIZE[1] + FONT_SIZE + PADDING_VERTICAL) * rows + PADDING_VERTICAL

    # Create the new image
    grid_image = Image.new("RGB", (grid_width, grid_height), "white")
    draw = ImageDraw.Draw(grid_image)

    # Paste images and add titles 
    x, y = PADDING_HORIZONTAL, PADDING_VERTICAL 
    for i, img in enumerate(images):
        title = data[i]["title"]
        draw.text((x, y), title, fill="black")  # Title at top
        grid_image.paste(img, (x, y + FONT_SIZE))  # Image directly below
        x += THUMB_SIZE[0] + PADDING_HORIZONTAL 
        if (i + 1) % cols == 0:
            x = PADDING_HORIZONTAL
            y += THUMB_SIZE[1] + FONT_SIZE + PADDING_VERTICAL

    return grid_image

def upload_to_gcs(image, bucket_name, filename):
    """Uploads an image to a Google Cloud Storage bucket."""
    storage_client = storage.Client(project=PROJECT_ID)
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(filename)

    with open(filename, 'wb') as f:
        image.save(f, 'JPEG')
    blob.upload_from_filename(filename)
    return blob.public_url

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
# To be only used for local testing
def test_image_create_local():
    grid_image = create_image_grid(local_testing_data)
    grid_image.save("output_image.jpg", "JPEG")
    return

def test_image_create_local():
    filename = f"static_test_{uuid.uuid4()}.jpg"
    url = create_gcs(filename)
    publish_message(url, local_testing_data)
    print(url)
    return {"url": url}

@functions_framework.http
def http_create_thumbnail(request):
    data = request.get_json()
    filename = f"thumbnail_v2_{uuid.uuid4()}.jpg"
    url = create_gcs(filename)
    publish_message(url, data)
    # grid_image = create_image_grid(data)
    # url = upload_to_gcs(grid_image, BUCKET, filename) 
    return {"url": url}


test_image_create_local()