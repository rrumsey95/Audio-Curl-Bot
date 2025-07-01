# Use official Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies for ffmpeg
RUN apt-get update
RUN apt-get install -y ffmpeg
RUN rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Set environment variables (optional, can be overridden)
ENV PYTHONUNBUFFERED=1

# Command to run the bot (note the src/ path)
CMD ["python", "src/Audio-Curl-Bot.py"]