#!/bin/bash
echo "Upgrading database..."
python /app/check_and_upgrade_db.py

# Start Flask app
echo "Starting Flask server..."
cd /app
gunicorn -k eventlet -b :5000 -w 4  --timeout 10000 --reload  app:app &

# Start Nginx for ingress
echo "Starting Nginx..."
nginx -g 'daemon off;'
