# !bin/bash
gcloud config set project $PROJECT_ID

gcloud functions deploy format_sellers \
  --gen2 \
  --region=us-central1 \
  --runtime=python310 \
  --source=./src/render_seller_details \
  --entry-point=http_format_sellers_messenger\
  --min-instances=1\
  --trigger-http \
  --allow-unauthenticated \
  --run-service-account=$FUNCTIONS_SERVICE_ACCOUNT \
  --set-env-vars=PROJECT_ID=$PROJECT_ID,LOCATION=$LOCATION,SEARCH_DATA_STORE_ID=$SEARCH_DATA_STORE_ID,DETAILS_SEARCH_URL=$DETAILS_SEARCH_URL
