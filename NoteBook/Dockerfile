FROM python:3.10-alpine

# Install necessary packages
RUN apk add --no-cache \
    nginx \
    bash

# Install Flask
RUN pip install flask==2.3.1 requests flask_sqlalchemy markdown beautifulsoup4 nltk bleach

# Copy the run script and Flask app
#copy local dir to /app
COPY ./ /app


# Set executable permissions
RUN chmod a+x /app/run.sh

# Expose ingress port for Flask (5000 is default for Flask)
EXPOSE 5000

# Start the service
CMD ["/app/run.sh"]
