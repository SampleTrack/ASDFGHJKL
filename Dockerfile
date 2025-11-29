FROM python:3.10-slim

ENV PYTHONUNBUFFERED=1

RUN apt-get update && \
    apt-get install -y git && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip3 install --no-cache-dir --upgrade pip && \
    pip3 install --no-cache-dir -r requirements.txt

COPY . .

# Documentation for Render to know where to look
EXPOSE 8080

CMD ["python3", "main.py"]
