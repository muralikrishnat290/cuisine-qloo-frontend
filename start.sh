#!/bin/bash

# Startup script for Railway and other production deployments
# This script handles the ScriptRunContext warnings and ensures proper configuration

echo "🚀 Starting Kitchen Intel Application..."

# Set default port if not provided
export PORT=${PORT:-8080}

# Suppress Python warnings and run Streamlit
export PYTHONWARNINGS="ignore"

echo "🔄 Starting Streamlit server..."

# Run Streamlit with production settings
exec streamlit run main.py \
    --server.address 0.0.0.0 \
    --server.port $PORT \
    --server.headless true \
    --server.fileWatcherType none \
    --server.enableCORS false \
    --server.enableXsrfProtection false \
    --logger.level error \
    --client.showErrorDetails false \
    2>/dev/null