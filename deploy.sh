#!/bin/bash
cd /opt/star_burger/
docker compose down
git pull
docker compose -f docker-compose.prod.yml build
docker compose -f docker-compose.prod.yml up -d
docker compose -f docker-compose.prod.yml exec web python manage.py migrate --noinput
docker compose -f docker-compose.prod.yml exec web python manage.py collectstatic --no-input --clear

if [ -f .env ]; then
  export $(echo $(cat .env | sed 's/#.*//g'| xargs -0) | envsubst)
fi

LOCAL_USERNAME=$(whoami)
REVISION=$(git rev-parse --short HEAD)

echo "Code version is:" "$REVISION"
echo "Environment:" "$ROLLBAR_ENVIRONMENT"

curl https://api.rollbar.com/api/1/deploy/ \
  -F access_token="$ROLLBAR_ACCESS_TOKEN" \
  -F environment="$ROLLBAR_ENVIRONMENT" \
  -F revision="$REVISION" \
  -F local_username="$LOCAL_USERNAME"

printf "\nDeploy completed!\n"
