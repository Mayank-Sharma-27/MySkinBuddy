FROM --platform=linux/amd64 python:3.9-slim-bullseye as builder

WORKDIR /app

# Install system dependencies with verbose output
RUN set -x && apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy and install requirements with verbose pip output
COPY requirements.txt .
RUN pip install --no-cache-dir -v -r requirements.txt

FROM --platform=linux/amd64 python:3.9-slim-bullseye

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.9/site-packages/ /usr/local/lib/python3.9/site-packages/
COPY --from=builder /usr/local/bin/ /usr/local/bin/

# Copy application code
COPY . .

# Set environment variables
ENV FLASK_APP=app.py
ENV FLASK_ENV=production

# Expose port
EXPOSE 8080

# Run the application with gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "2", "--threads", "4", "app:app"]