#!/bin/sh

# run migrations
alembic upgrade head

# run the seed command
cd /app/ads_directory
quart seed-db