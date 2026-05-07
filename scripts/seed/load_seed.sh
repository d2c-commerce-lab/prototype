#!/usr/bin/env sh

set -eu

PROJECT_ROOT="$(CDPATH= cd -- "$(dirname -- "$0")/../.." && pwd)"
SEED_DIR="$PROJECT_ROOT/db/seeds"

CONTAINER_NAME="${CONTAINER_NAME:-d2c-postgres}"
DB_NAME="${DB_NAME:-d2c_commerce}"
DB_USER="${DB_USER:-postgres}"

SEED_FILES="
seed_categories.sql
seed_campaigns.sql
seed_products.sql
seed_coupons.sql
"

if ! command -v docker >/dev/null 2>&1; then
  echo "Error: docker command not found." >&2
  exit 1
fi

if ! docker ps --format '{{.Names}}' | grep -Fxq "$CONTAINER_NAME"; then
  echo "Error: container is not running: $CONTAINER_NAME" >&2
  exit 1
fi

for file in $SEED_FILES
do
  full_path="$SEED_DIR/$file"

  if [ ! -f "$full_path" ]; then
    echo "Error: seed file not found: $full_path" >&2
    exit 1
  fi

  echo "Applying $file ..."

  if ! docker exec -i "$CONTAINER_NAME" psql -U "$DB_USER" -d "$DB_NAME" < "$full_path"; then
    echo "Error: failed to apply $file" >&2
    exit 1
  fi
done

echo "All seed files applied successfully."