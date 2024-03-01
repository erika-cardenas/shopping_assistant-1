# !bin/bash
gcloud config set project $PROJECT_ID

gcloud functions deploy product_check \
  --gen2 \
  --region=us-central1 \
  --runtime=python310 \
  --source=./src/catalog \
  --entry-point=http_product_check\
  --min-instances=0\
  --trigger-http \
  --allow-unauthenticated \
  --run-service-account=$FUNCTIONS_SERVICE_ACCOUNT \
  --set-env-vars=PROJECT_ID=$PROJECT_ID,LOCATION=$LOCATION,INVENTORY=$INVENTORY
