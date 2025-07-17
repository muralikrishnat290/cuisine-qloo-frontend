FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Set port environment variable (many platforms like Render use PORT)
ENV PORT=8080

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN pip install streamlit>=1.28.0 requests>=2.31.0 python-dotenv>=1.0.0 streamlit-authenticator>=0.2.3 bcrypt>=4.0.1

# Copy application code
COPY . .

# Create .streamlit directory for potential secrets mounting
RUN mkdir -p .streamlit

# Expose the port
EXPOSE 8080

# Make startup script executable and run it
RUN chmod +x start.sh
CMD ["./start.sh"]