# Use Python 3.10 as the base image
FROM python:3.10-slim-buster

# Set the working directory inside the container
WORKDIR /app

# Upgrade pip to ensure smooth installation
RUN pip install --upgrade pip

# Copy the requirements file first (for better caching)
COPY requirements.txt .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy all the remaining files (main.py, config.py, plugins/, helper/)
COPY . .

# Command to start the bot
CMD ["python", "main.py"]
