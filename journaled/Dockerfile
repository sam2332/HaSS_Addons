FROM python:3.10-alpine

# Install necessary packages
RUN apk add --no-cache \
    nginx \
    bash

# Install Flask
RUN pip install flask requests flask_sqlalchemy

# Copy the run script and Flask app
COPY ./ /app


# Set executable permissions
RUN chmod a+x /app/run.sh

# Expose ingress port for Flask (5000 is default for Flask)
EXPOSE 5000

# Start the service
CMD ["/app/run.sh"]
