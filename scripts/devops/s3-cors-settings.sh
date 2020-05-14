#!/usr/bin/env bash
bucket=${1:-"${S3_BUCKET:-"data.tistatech.com"}"}

echo "This script to update CORS settings for ${bucket} S3 bucket"
read -p "Do you want to continue (y/N)? " opt
if [ "${opt}" != "y" ] && [ "${opt}" != "Y" ]; then
    echo "Skip"
    exit 1
fi

echo "Create json file with the cors settings"
echo -e '{
  "CORSRules": [
    {
      "AllowedOrigins": ["*"],
      "AllowedHeaders": ["*"],
      "AllowedMethods": ["GET"],
      "MaxAgeSeconds": 3000
    }
  ]
}' | tee /tmp/cors.json

echo "Update cors settings for the ${bucket} bucket"
aws s3api put-bucket-cors --bucket ${bucket} --cors-configuration file:///tmp/cors.json || exit 1
echo "Done"

echo "If you are using Cloudfront with S3 then you need to update it settings too:"
echo "-----------------------------"
echo "1. Open Cloudfront option"
echo "2. Allowed HTTP Methods: [*] GET,HEAD, OPTIONS"
echo "3. Cached HTTP Methods: [X] OPTIONS"
echo "4. Whitelist Headers: Origin"
echo "-----------------------------"

