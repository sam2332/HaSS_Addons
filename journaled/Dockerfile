FROM python:3.10-alpine

# Install necessary packages
RUN apk add --no-cache \
    nginx \
    bash

# Install Flask
RUN pip install flask requests flask_sqlalchemy tzdata pillow gunicorn eventlet nltk 

# Copy the run script and Flask app
COPY ./ /app



RUN chmod a+x /app/docker/update_nginx.py
RUN python /app/docker/update_nginx.py

RUN chmod a+x /app/docker/ntkl_setup.py
RUN python /app/docker/ntkl_setup.py


# Expose ingress port for Flask (80 for nginx)
EXPOSE 5000

# Set executable permissions
RUN chmod a+x /app/run.sh

# Start the service
CMD ["/app/run.sh"]
