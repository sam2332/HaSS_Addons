#!/bin/bash
cd /app

echo "Upgrading database..."
python /app/pre_lauch_scripts/check_and_upgrade_db.py

echo "generating css"
python /app/pre_lauch_scripts/generate_mood_css.py

# Start Flask app
echo "Starting Flask server..."
cd /app
gunicorn -k eventlet -b :5000 -w 4  --timeout 10000 --reload  app:app &

# Start Nginx for ingress
echo "Starting Nginx..."
nginx -g 'daemon off;'
