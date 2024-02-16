# !bin/bash
gcloud config set project $PROJECT_ID

gcloud functions deploy details \
  --gen2 \
  --region=us-central1 \
  --runtime=python310 \
  --source=./src/search_function \
  --entry-point=http_product_details \
  --trigger-http \
  --allow-unauthenticated \
  --run-service-account=$FUNCTIONS_SERVICE_ACCOUNT \
  --set-env-vars=PROJECT_ID=$PROJECT_ID,LOCATION=$LOCATION,DATA_STORE_ID=$SEARCH_DATA_STORE_ID
