#! /bin/sh

# Wait for dependencies
./wait-for-it.sh $PG_HOST:$PG_PORT -t 60
# ./wait-for-it.sh $ELASTICSEARCH_HOST:$ELASTICSEARCH_PORT -t 60
./wait-for-it.sh $REDIS_HOST:$REDIS_PORT -t 60

# Ensure /data directory exists
mkdir -p /data

# Download schema.json from URL
if [ -n "$SCHEMA_URL" ]; then
  echo "Downloading schema.json from $SCHEMA_URL"
  curl -sSf -o /data/schema.json "$SCHEMA_URL" || {
    echo "Error: Failed to download schema.json from $SCHEMA_URL"
    exit 1
  }
fi

# Ensure schema file exists
SCHEMA_FILE=${SCHEMA_FILE:-/data/schema.json}
if [ ! -f "$SCHEMA_FILE" ]; then
  echo "Error: Schema file not found at $SCHEMA_FILE"
  exit 1
fi

# Bootstrap and start pgsync
echo "Bootstrapping pgsync with schema file: $SCHEMA_FILE"
bootstrap --config "$SCHEMA_FILE" || {
  echo "Error: Failed to bootstrap pgsync with $SCHEMA_FILE"
  exit 1
}

echo "Starting pgsync..."
pgsync --config "$SCHEMA_FILE" --daemon || {
  echo "Error: Failed to start pgsync"
  exit 1
}