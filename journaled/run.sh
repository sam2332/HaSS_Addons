#!/bin/bash

# Start Flask app
echo "Starting Flask server..."
python3 /app/app.py &

# Start Nginx for ingress
echo "Starting Nginx..."
nginx -g 'daemon off;'
