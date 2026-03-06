# Use the official lightweight Python image.
# https://hub.docker.com/_/python
FROM python:3.9-slim

# Allow statements and log messages to immediately appear in the Knative logs
ENV PYTHONUNBUFFERED True

# Copy local code to the container image.
ENV APP_HOME /app
WORKDIR $APP_HOME
COPY . ./

# Install production dependencies.
RUN pip install --no-cache-dir -r requirements.txt

# Expose port 8080 (the default port expected by Cloud Run)
EXPOSE 8080

# Run the web service on container startup.
# We set the port to 8080 and bind to 0.0.0.0, disable CORS/XSRF, and run headless
CMD streamlit run Assign1_code.py --server.port=8080 --server.address=0.0.0.0 --server.enableCORS=false --server.enableXsrfProtection=false --server.headless=true
