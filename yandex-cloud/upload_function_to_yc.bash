yc serverless function version create \
  --function-name=e-comet-tz \
  --runtime python3.12 \
  --entrypoint index.handler \
  --memory 128m \
  --execution-timeout 5s \
  --source-path ./hello-js.zip