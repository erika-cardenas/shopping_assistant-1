# !bin/bash
gcloud config set project $PROJECT_ID

gcloud functions deploy format_products_v4 \
  --gen2 \
  --region=us-central1 \
  --runtime=python310 \
  --source=./src/render_search_results \
  --entry-point=http_format_products\
  --min-instances=0\
  --trigger-http \
  --allow-unauthenticated \
  --run-service-account=$FUNCTIONS_SERVICE_ACCOUNT \
  --set-env-vars=PROJECT_ID=$PROJECT_ID,SEARCH_URL=$SEARCH_URL

