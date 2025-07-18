FROM python:3.11-slim AS base

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    supervisor \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements for all services
COPY requirements.txt /app/requirements.txt

# Install all dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code (existing services)
COPY generator/server.py /app/generator/
COPY resolver/server.py /app/resolver/
COPY proxy.py /app/
COPY database.py /app/
COPY migrate.py /app/

# Create directories for data and logs
RUN mkdir -p /app/generator/markets /app/resolver/resolutions

# Create database file with proper permissions
RUN touch /app/markets.db && chmod 666 /app/markets.db

# Copy supervisor configuration
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash app && chown -R app:app /app
USER app

# Expose ports
EXPOSE 8000 8001 8080

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Start with supervisord
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"] 