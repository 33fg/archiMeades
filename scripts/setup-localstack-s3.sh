#!/usr/bin/env bash
# Create S3 bucket in LocalStack for local development.
# Run: npm run s3:start  (starts LocalStack + this script)
# Or: docker compose up -d localstack && sleep 5 && ./scripts/setup-localstack-s3.sh

set -e
ENDPOINT="${AWS_ENDPOINT_URL:-http://localhost:4566}"
BUCKET="${S3_BUCKET:-gravitational-simulations}"
# LocalStack accepts these fake credentials; required for aws CLI
export AWS_ACCESS_KEY_ID="${AWS_ACCESS_KEY_ID:-test}"
export AWS_SECRET_ACCESS_KEY="${AWS_SECRET_ACCESS_KEY:-test}"

echo "Creating bucket $BUCKET at $ENDPOINT"

if command -v aws &>/dev/null; then
  aws --endpoint-url="$ENDPOINT" --region us-east-1 s3 mb "s3://$BUCKET" 2>/dev/null || \
    aws --endpoint-url="$ENDPOINT" --region us-east-1 s3 ls "s3://$BUCKET" >/dev/null && echo "Bucket already exists"
else
  # Fallback: use Python boto3 (from project venv)
  SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
  ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
  "$ROOT_DIR/.venv/bin/python" -c "
import boto3
from botocore.config import Config
from botocore.exceptions import ClientError
client = boto3.client('s3', endpoint_url='${ENDPOINT}', region_name='us-east-1',
    aws_access_key_id='${AWS_ACCESS_KEY_ID}', aws_secret_access_key='${AWS_SECRET_ACCESS_KEY}',
    config=Config(signature_version='s3v4'))
try:
    client.create_bucket(Bucket='${BUCKET}')
    print('Bucket created')
except ClientError as e:
    if e.response.get('Error', {}).get('Code') in ('BucketAlreadyOwnedByYou', 'BucketAlreadyExists'):
        print('Bucket already exists')
    else:
        raise
"
fi

echo ""
echo "Add to backend/.env:"
echo "  AWS_ENDPOINT_URL=$ENDPOINT"
echo "  AWS_ACCESS_KEY_ID=test"
echo "  AWS_SECRET_ACCESS_KEY=test"
