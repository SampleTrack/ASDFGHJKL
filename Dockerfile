FROM python:3.10

RUN apt update && apt upgrade -y && apt install -y git

COPY requirements.txt /tmp/requirements.txt

# Upgrade pip and install Python dependencies (this will be cached unless requirements.txt changes)
RUN pip3 install --upgrade pip && \
    pip3 install --upgrade -r /tmp/requirements.txt
 
# Set up working directory
WORKDIR /app

COPY . /app

# Ensure permissions
RUN chmod -R 777 /app

# Expose the port Flask (or any app) runs on
EXPOSE 7860

# Default command to run the app
CMD ["python3", "main.py"]
