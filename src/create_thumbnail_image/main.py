import requests, os, json, base64
from PIL import Image, ImageDraw
from google.cloud import storage, pubsub_v1
from cloudevents.http import CloudEvent
import functions_framework
import urllib.parse

PROJECT_ID = os.getenv("PROJECT_ID")
BUCKET = os.getenv("BUCKET")
TOPIC = os.getenv("TOPIC", "thumbnail_generation")

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

def extract_filename_from_url(url):
  parsed_url = urllib.parse.urlparse(url)
  filename = parsed_url.path.split('/')[-1]
  return filename if filename else None

def upload_to_gcs(image, bucket_name, url):
    """Uploads an image to a Google Cloud Storage bucket."""
    storage_client = storage.Client(project=PROJECT_ID)
    bucket = storage_client.bucket(bucket_name)
    filename = extract_filename_from_url(url)
    blob = bucket.blob(filename)

    with open(filename, 'wb') as f:
        image.save(f, 'JPEG')
    blob.upload_from_filename(filename)
    return 

@functions_framework.cloud_event
def create_image(cloud_event: CloudEvent) -> None:
    decoded_message = base64.b64decode(cloud_event.data["message"]["data"]).decode()    
    print(f"Received message: {decoded_message}")
    message_json = json.loads(decoded_message)
    print(f"JSON Data: {message_json}")
    image = create_image_grid(message_json["data"])
    upload_to_gcs(image, BUCKET, message_json["link"])


def test_decode():
    message_data= {
  "message": {
    "_comment": "data is base64 encoded string of 'Hello World'",
    "data": "SGVsbG8gV29ybGQ="
  }
}
    print(base64.b64decode(message_data["message"]["data"]).decode())

def test_image_create(data):
    grid_image = create_image_grid(data)
    return grid_image
