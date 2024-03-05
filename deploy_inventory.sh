# !bin/bash
gcloud config set project $PROJECT_ID

gcloud functions deploy inventory \
  --gen2 \
  --region=$REGION \
  --runtime=python310 \
  --source=./src/inventory \
  --entry-point=http_inventory\
  --min-instances=0\
  --trigger-http \
  --allow-unauthenticated \
  --run-service-account=$FUNCTIONS_SERVICE_ACCOUNT 