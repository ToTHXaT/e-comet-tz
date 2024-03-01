if [ -f ./.env ]; then
  set -a # automatically export all variables
  source ./.env # should exist
  set +a

  yc serverless function create --name 'e-comet-tz'
  yc serverless function version create \
    --function-name 'e-comet-tz' \
    --runtime python311 \
    --entrypoint index.handler \
    --memory 256m \
    --execution-timeout 180s \
    --service-account-id $SERVICE_ACCOUNT_ID \
    --log-group-name default \
    --source-path ./source \
    --min-log-level debug \
    --environment GITHUB_TOKEN=$GITHUB_TOKEN,DB_HOST=$DB_HOST,DB_PORT=$DB_PORT,DB_USER=$DB_USER,DB_PASSWORD=$DB_PASSWORD,DB_NAME=$DB_NAME

  yc serverless trigger create timer \
    --name daily-github-parsing \
    --invoke-function-service-account-id $SERVICE_ACCOUNT_ID \
    --cron-expression '0 3 ? * *' \
    --invoke-function-name 'e-comet-tz'
else
  echo 'No .env file found'
fi
