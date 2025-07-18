# Base image
FROM python:3.13-slim

LABEL authors="f4rukseker"

# Set workdir
WORKDIR /app

# Install dependencies
COPY requirements.txt requirements.lock.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy source files
COPY . .

# Expose port
EXPOSE 8000

# Run the app
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
