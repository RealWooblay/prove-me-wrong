#!/bin/bash

# Set environment variables for the processes
export ASI_API_KEY="${ASI_API_KEY}"
export DATABASE_URL="${DATABASE_URL}"
export PYTHONUNBUFFERED="1"

# Debug information
echo "=== Startup Debug Info ==="
echo "Current directory: $(pwd)"
echo "DATABASE_URL: ${DATABASE_URL}"
echo "ASI_API_KEY: ${ASI_API_KEY:0:10}..."
echo "Files in /app:"
ls -la /app/
echo "========================"

# Run database migration first
echo "Running database migration..."
python /app/migrate.py

# Start supervisord
exec /usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf 