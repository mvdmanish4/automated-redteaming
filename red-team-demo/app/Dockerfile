# Vulnerable E-commerce Application Dockerfile
# =============================================
# ⚠️ WARNING: This container is INTENTIONALLY VULNERABLE
# ⚠️ FOR EDUCATIONAL AND AUTHORIZED TESTING PURPOSES ONLY
# ⚠️ NEVER deploy in production environments
#
# This Dockerfile creates a container with a Flask application
# that demonstrates command injection vulnerabilities.

FROM python:3.11-slim

# Metadata labels
LABEL maintainer="Red Team Demo Project"
LABEL description="Vulnerable e-commerce application for security training"
LABEL warning="INTENTIONALLY VULNERABLE - EDUCATIONAL USE ONLY"

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8080 \
    ENVIRONMENT=production

# Set working directory
WORKDIR /app

# Install system dependencies
# ping and curl are needed for the vulnerable endpoint and testing
RUN apt-get update && apt-get install -y --no-install-recommends \
    iputils-ping \
    curl \
    procps \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user for slightly better security practice
# (though this won't prevent command injection exploitation)
RUN useradd --create-home --shell /bin/bash appuser

# Copy requirements first for better layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY app.py .
COPY productdata.txt .

# Set proper permissions
# Making productdata.txt readable is intentional for the demo
RUN chown -R appuser:appuser /app && \
    chmod 644 productdata.txt

# Switch to non-root user
USER appuser

# Expose the port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Run the application with gunicorn for production
# Using gunicorn for better performance in Cloud Run
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "2", "--threads", "4", "--timeout", "60", "app:app"]
