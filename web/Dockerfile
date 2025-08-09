# Dockerfile for LOGDTW2002 Flask Web Application
FROM python:3.11-slim

LABEL maintainer="LOGDTW2002 Team"
LABEL description="LOGDTW2002 Space Trading Game - Web Edition"

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV FLASK_ENV=production
ENV PORT=5000

# Create app directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements-web.txt .
RUN pip install --no-cache-dir -r requirements-web.txt

# Copy application code
COPY . .
COPY ../game ./game
COPY ../utils ./utils
COPY ../data ./data

# Create necessary directories
RUN mkdir -p web_saves templates static/css static/js

# Set permissions
RUN chmod +x run.py

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/api/status || exit 1

# Run the application
CMD ["python", "run.py"]
