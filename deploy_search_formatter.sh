# !bin/bash
gcloud config set project $PROJECT_ID

gcloud functions deploy format_products_v3 \
  --gen2 \
  --region=us-central1 \
  --runtime=python310 \
  --source=./src/render_search_results \
  --entry-point=http_format_products_messenger\
  --min-instances=1\
  --trigger-http \
  --allow-unauthenticated \
  --run-service-account=$FUNCTIONS_SERVICE_ACCOUNT \
  --set-env-vars=PROJECT_ID=$PROJECT_ID,LOCATION=$LOCATION,SEARCH_DATA_STORE_ID=$SEARCH_DATA_STORE_ID,SEARCH_URL=$SEARCH_URL

