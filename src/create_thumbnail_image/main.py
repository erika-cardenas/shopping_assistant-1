import requests, os
from PIL import Image, ImageDraw
import uuid 
from google.cloud import storage
import functions_framework

PROJECT_ID = os.getenv("PROJECT_ID")
BUCKET = os.getenv("BUCKET")

os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

def create_image_grid(data):
    THUMB_SIZE = (200, 200) 
    PADDING = 50
    FONT_SIZE = 30    

    images = []
    max_title_width = 0

    # Download and resize images, find widest title
    for item in data:
        response = requests.get(item["link"], stream=True)
        response.raise_for_status()  # Check for download errors
        img = Image.open(response.raw)
        img.thumbnail(THUMB_SIZE)
        images.append(img)
        max_title_width = max(max_title_width, len(item["title"]) * FONT_SIZE)

    # Calculate grid dimensions
    cols = 3  # Adjust as needed for how many columns in your grid
    rows = (len(images) + cols - 1) // cols
    grid_width = (THUMB_SIZE[0] + PADDING) * cols + PADDING 
    grid_height = (THUMB_SIZE[1] + PADDING + FONT_SIZE) * rows + PADDING

    # Create the new image
    grid_image = Image.new("RGB", (grid_width, grid_height), "white")
    draw = ImageDraw.Draw(grid_image)

    # Paste images and add titles
    x, y = PADDING, PADDING
    for i, img in enumerate(images):
        grid_image.paste(img, (x, y))
        title = data[i]["title"]
        draw.text((x, y + THUMB_SIZE[1] + PADDING), title, fill="black")
        x += THUMB_SIZE[0] + PADDING 
        if (i + 1) % cols == 0:
            x = PADDING
            y += THUMB_SIZE[1] + PADDING + FONT_SIZE

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

@functions_framework.http
def http_create_thumbnail(request):
    data = request.get_json()
    print(data)
    filename = f"thumbnail_{uuid.uuid4()}.jpg"
    grid_image = create_image_grid(data)
    url = upload_to_gcs(grid_image, BUCKET, filename) 
    print("generated ", url)
    return {"url": url}