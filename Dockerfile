FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY tests/ ./tests/

# Expose port
EXPOSE 8000

# Run with gunicorn for production, flask for development
CMD ["python", "-m", "src.app"]