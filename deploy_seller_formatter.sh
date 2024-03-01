# !bin/bash
gcloud config set project $PROJECT_ID

gcloud functions deploy format_sellers_v2 \
  --gen2 \
  --region=us-central1 \
  --runtime=python310 \
  --source=./src/render_seller_details \
  --entry-point=http_format_sellers\
  --min-instances=0\
  --trigger-http \
  --allow-unauthenticated \
  --run-service-account=$FUNCTIONS_SERVICE_ACCOUNT \
  --set-env-vars=PROJECT_ID=$PROJECT_ID,DETAILS_SEARCH_URL=$DETAILS_SEARCH_URL
