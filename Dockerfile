FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y git && apt-get clean

# Copy requirements and install
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Set permissions
RUN chmod +x main.py

# Expose port for Flask
EXPOSE 8080

# Run the bot
CMD ["python3", "main.py"]
