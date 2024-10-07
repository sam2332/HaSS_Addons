#!/bin/bash

# Start Flask app
echo "Starting Flask server..."
cd /app
gunicorn -k eventlet -b :5000 -w 20  --timeout 10000 --reload  app:app &

# Start Nginx for ingress
echo "Starting Nginx..."
nginx -g 'daemon off;'
