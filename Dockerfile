FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Set port environment variable (many platforms like Render use PORT)
ENV PORT=8080

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create .streamlit directory for potential secrets mounting
RUN mkdir -p .streamlit

# Expose the port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8080/_stcore/health || exit 1

# Run the application
CMD ["streamlit", "run", "main.py", "--server.address", "0.0.0.0", "--server.port", "8080", "--server.headless", "true", "--server.fileWatcherType", "none"]