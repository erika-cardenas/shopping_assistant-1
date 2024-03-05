# !bin/bash
gcloud config set project $PROJECT_ID

gcloud functions deploy format_sellers \
  --gen2 \
  --region=$REGION \
  --runtime=python310 \
  --source=./src/render_seller_details \
  --entry-point=http_format_sellers\
  --min-instances=0\
  --trigger-http \
  --allow-unauthenticated \
  --run-service-account=$FUNCTIONS_SERVICE_ACCOUNT \
  --set-env-vars=PROJECT_ID=$PROJECT_ID,INVENTORY_URL=$INVENTORY_URL,LOCAL=false
