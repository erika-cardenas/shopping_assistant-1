import vertexai
from vertexai.preview.generative_models import GenerativeModel, Part, Image
import vertexai.preview.generative_models as generative_models
import requests
from PIL import Image as im
import io

def generate(image):
  vertexai.init(project="ccai-demo-414406", location="us-central1")
  model = GenerativeModel("gemini-pro-vision")
  response = model.generate_content(
    [image, """Provide a list of all the following product attributes for the main product in the image: product category, color, model,  style, title and short description  in JSON format"""],
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
  print(response.text)
  return response.text


def resize_and_open_image(image_url):
    response = requests.get(image_url, stream=True)
    response.raise_for_status()  # Raise an exception for bad status codes
    image = im.open(io.BytesIO(response.content))    
    # Calculate aspect ratio to maintain during resizing
    aspect_ratio = image.width / image.height
    new_height = int(100 * aspect_ratio)

    # Resize the image
    img_small = image.resize((100, new_height), im.ADAPTIVE)
    img_small.save("small.jpg")
    part_img = Part.from_image(Image.load_from_file("small.jpg"))

    return part_img

def caption_image(link):
   img = resize_and_open_image(link)
   return generate(img) 

caption_image("https://shop.googlemerchandisestore.com/store/20160512512/assets/items/images/GGOEAXXX0812.jpg")