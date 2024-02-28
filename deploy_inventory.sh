# !bin/bash
gcloud config set project $PROJECT_ID

gcloud functions deploy check_inventory \
  --gen2 \
  --region=us-central1 \
  --runtime=python310 \
  --source=./src/inventory \
  --entry-point=http_check_inventory \
  --trigger-http \
  --allow-unauthenticated \
