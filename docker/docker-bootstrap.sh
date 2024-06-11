#!/bin/sh

set -eo

# run the init firstly
/app/docker/docker-init.sh

echo "Starting docker bootstraping"
# run the app
echo "Starting the app\n"
/app/.venv/bin/hypercorn --config=hypercorn.toml ads_directory/asgi:app
ech "Started the app\n"







