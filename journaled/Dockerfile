FROM python:3.10-alpine

# Install necessary packages
RUN apk add --no-cache \
    nginx \
    bash

# Install Flask
RUN pip install flask requests flask_sqlalchemy tzdata pillow gunicorn eventlet

# Copy the run script and Flask app
COPY ./ /app



RUN chmod a+x /app/update_nginx.py
RUN python /app/update_nginx.py


# Expose ingress port for Flask (80 for nginx)
EXPOSE 5000

# Set executable permissions
RUN chmod a+x /app/run.sh
# Start the service
CMD ["/app/run.sh"]
