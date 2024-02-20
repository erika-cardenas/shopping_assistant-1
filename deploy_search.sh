# !bin/bash
gcloud config set project $PROJECT_ID

gcloud functions deploy search_v3 \
  --gen2 \
  --region=us-central1 \
  --runtime=python310 \
  --source=./src/search_function \
  --entry-point=http_search \
  --trigger-http \
  --allow-unauthenticated \
  --run-service-account=$FUNCTIONS_SERVICE_ACCOUNT \
  --set-env-vars=PROJECT_ID=$PROJECT_ID,LOCATION=$LOCATION,SEARCH_DATA_STORE_ID=$SEARCH_DATA_STORE_ID,THUMBNAIL_URL=$THUMBNAIL_URL
