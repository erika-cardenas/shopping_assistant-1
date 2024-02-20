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

def generate_caption(image):
  vertexai.init(project="ccai-demo-414406", location="us-central1")
  model = GenerativeModel("gemini-pro-vision")
  response = model.generate_content(
    [image, """Provide a list of all the following product attributes for the main product in the image in the format {"category":<val>, "color":[<val>,<val>], "model":<val>, "new_title":<val>,  "description":<val>}  The description should be less than 3 sentences. If the product is multicoloured then mention 2-3 of the most prominent colours """],
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

unique_links=[]
caption_dict = {}
def caption_image(link):
   if link is not None:
    if link not in unique_links:
      unique_links.append(link)
      img = resize_and_open_image(link)
      caption= generate_caption(img) 
      caption_dict[link] = caption
    return caption_dict[link]

def skip_processed(file, product_reader, ):
  #  with open(file) as f:
  #   # lines_processed = sum(1 for f in file)
   lines_processed = 0
   for i in range(1,lines_processed):
      next(product_reader)
   return product_reader

def add_captions_to_products(products_file, output_file):
    with open(products_file, 'r', newline='') as pfile, \
        open(output_file, 'a', newline='') as outfile:
        product_reader = csv.reader(pfile)
        product_header = next(product_reader) + ['color'] + ['description'] + ["short_description"]  # Add seller_name to product header
        writer = csv.writer(outfile)
        # writer.writerow(product_header)

        product_reader = skip_processed(output_file, product_reader)
        for product_row in product_reader:
            try:
              link = product_row[5]
              caption = caption_image(link=link)
              cleaned = clean_string(caption)
              new_attributes = json.loads(cleaned)
              product_row[2] = new_attributes["category"]
              writer.writerow(product_row + [new_attributes["color"]] + [new_attributes["description"]] + [new_attributes["new_title"]])
            except Exception as e:
               print("issue with ", product_row)
               print(e)
               pass
        
def generate_product_condition():
    conditions = ['new', 'good as new', 'used']  # Renamed 'states' to 'conditions'
    condition_probabilities = [0.6, 0.3, 0.1] 
    condition = random.choices(conditions, weights=condition_probabilities)[0] 
    return condition

if __name__ == "__main__":
    products_file = 'datamanipulation2/4_products_with_costs.csv'
    output_file = 'datamanipulation2/5_enriched_catalog.csv'
    add_captions_to_products(products_file, output_file)
