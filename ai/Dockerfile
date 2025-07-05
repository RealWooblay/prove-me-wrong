FROM python:3.11-slim AS base

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    supervisor \
    && rm -rf /var/lib/apt-lists/*

WORKDIR /app

# Copy requirements for both services
COPY generator/requirements.txt /app/generator-requirements.txt
COPY resolver/requirements.txt /app/resolver-requirements.txt

# Install Python dependencies for both services
RUN pip install --no-cache-dir -r generator-requirements.txt -r resolver-requirements.txt httpx

# Copy application code
COPY generator/server.py /app/generator/
COPY resolver/server.py /app/resolver/
COPY proxy.py /app/
COPY database.py /app/
COPY migrate.py /app/

# Create directories for data
RUN mkdir -p /app/generator/markets /app/resolver/resolutions

# Create database file with proper permissions
RUN touch /app/markets.db && chmod 666 /app/markets.db

# Copy supervisor configuration and startup script
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf
COPY start.sh /app/start.sh

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash app && chown -R app:app /app
RUN chmod +x /app/start.sh
USER app

# Expose port (Railway will set PORT environment variable)
EXPOSE ${PORT:-8000}

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8000}/health || exit 1

# Start both services with supervisor and proxy
CMD ["/app/start.sh"] 