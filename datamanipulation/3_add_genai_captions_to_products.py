import vertexai
from vertexai.preview.generative_models import GenerativeModel, Part, Image
import vertexai.preview.generative_models as generative_models
import requests
from PIL import Image as im
import io, csv, json, random

def clean_string(text):
  cleaned_text = text.replace("\n", "")
  cleaned_text = cleaned_text.replace("'", "")
  cleaned_text = cleaned_text.replace("`", "")
  cleaned_text = cleaned_text.replace("json", "")
  return cleaned_text

def generate_caption(image, title):
  vertexai.init(project="ccai-demo-414406", location="us-central1")
  model = GenerativeModel("gemini-pro-vision")
  response = model.generate_content(
    [image, title, """Provide a list of all the following product attributes for the main product in the image in the format {"categories":[<val>, <val>], "color":[<val>,<val>], "product_type":<val>, "new_title":<val>, "description":<val>, "gender":<gender>, "google_brand":<val>}  The description should be less than 3 sentences. Mention 1-3 of the dominant colours of the product. The gender has to be men, women or unisex. The google brand can be Google, Youtube, Android, Google Cloud, etc. The new_title should be derived from the input text, but should not contain any size,, colour or gender information"""],
    generation_config={
        "max_output_tokens": 2048,
        "temperature": 0.4,
        "top_p": 1,
        "top_k": 32
    },
    safety_settings={
          generative_models.HarmCategory.HARM_CATEGORY_HATE_SPEECH: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
          generative_models.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
          generative_models.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
          generative_models.HarmCategory.HARM_CATEGORY_HARASSMENT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
    },
    stream=False,
  )
  return response.text


def resize_and_open_image(image_url):
    response = requests.get(image_url, stream=True)
    response.raise_for_status()  # Raise an exception for bad status codes
    image = im.open(io.BytesIO(response.content))    
    # Calculate aspect ratio to maintain during resizing
    aspect_ratio = image.width / image.height
    new_height = int(300 * aspect_ratio)

    # Resize the image
    img_small = image.resize((300, new_height), im.ADAPTIVE)
    img_small.save("product.jpg")
    part_img = Part.from_image(Image.load_from_file("product.jpg"))

    return part_img

def caption_image(link, title):
    img = resize_and_open_image(link)
    caption= generate_caption(img, title) 
    return caption

def skip_processed(file, product_reader):
   with open(file) as f:
    lines_processed = sum(1 for f in file)
   for i in range(1,lines_processed):
      next(product_reader)
   return product_reader

unique_products = []
def add_captions_to_products(products_file, output_file):
    with open(products_file, 'r', newline='') as pfile, \
        open(output_file, 'a', newline='') as outfile:
        product_reader = csv.reader(pfile)
        product_header = next(product_reader) + ['color'] + ["description"]  + ['gender'] + ['google_brand']  # Add seller_name to product header
        writer = csv.writer(outfile)
        writer.writerow(product_header)

        product_reader = skip_processed(output_file, product_reader)
        for product_row in product_reader:
            try:
              link = product_row[5]
              title = product_row[1]
              if link not in unique_products and link is not None:
                unique_products.append(link)
                caption = caption_image(link=link, title=title)
                cleaned = clean_string(caption)
                new_attributes = json.loads(cleaned)
                product_row[2] = new_attributes["product_type"]
                product_row[1] = new_attributes["new_title"]
                writer.writerow(product_row + [new_attributes["color"]] + [new_attributes["description"]] + [new_attributes["gender"]]  + [new_attributes["google_brand"]])
            except Exception as e:
               print("issue with ", product_row)
               print(e)
               pass
        
if __name__ == "__main__":
    products_file = 'datamanipulation/data/2_removed_unnecessary_columns.csv'
    output_file = 'datamanipulation/data/3_enriched_catalog.csv'
    add_captions_to_products(products_file, output_file)
