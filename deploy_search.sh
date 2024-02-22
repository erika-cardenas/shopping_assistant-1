# !bin/bash
gcloud config set project $PROJECT_ID

# gcloud functions deploy search_details \
#   --gen2 \
#   --region=us-central1 \
#   --runtime=python310 \
#   --source=./src/search_function \
#   --entry-point=http_search_details\
#   --min-instances=1\
#   --trigger-http \
#   --allow-unauthenticated \
#   --run-service-account=$FUNCTIONS_SERVICE_ACCOUNT \
#   --set-env-vars=PROJECT_ID=$PROJECT_ID,LOCATION=$LOCATION,SEARCH_DATA_STORE_ID=$SEARCH_DATA_STORE_ID

# gcloud functions deploy search_products \
#   --gen2 \
#   --region=us-central1 \
#   --runtime=python310 \
#   --source=./src/search_function \
#   --entry-point=http_search_products\
#   --min-instances=1\
#   --trigger-http \
#   --allow-unauthenticated \
#   --run-service-account=$FUNCTIONS_SERVICE_ACCOUNT \
#   --set-env-vars=PROJECT_ID=$PROJECT_ID,LOCATION=$LOCATION,SEARCH_DATA_STORE_ID=$SEARCH_DATA_STORE_ID

gcloud functions deploy search_products_messenger \
  --gen2 \
  --region=us-central1 \
  --runtime=python310 \
  --source=./src/search_function \
  --entry-point=http_format_products_messenger\
  --min-instances=1\
  --trigger-http \
  --allow-unauthenticated \
  --run-service-account=$FUNCTIONS_SERVICE_ACCOUNT \
  --set-env-vars=PROJECT_ID=$PROJECT_ID,LOCATION=$LOCATION,SEARCH_DATA_STORE_ID=$SEARCH_DATA_STORE_ID
