# !bin/bash
gcloud config set project $PROJECT_ID

gcloud functions deploy cart \
  --gen2 \
  --region=us-central1 \
  --runtime=python310 \
  --source=./src/add_item_to_cart_function \
  --entry-point=http_add_item \
  --trigger-http \
  --allow-unauthenticated \
