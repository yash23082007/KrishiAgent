FROM python:3.11-slim

# Install system dependencies (including ffmpeg for audio conversion)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Create database directory if needed
RUN mkdir -p db static/audio temp

EXPOSE 8000

CMD ["python", "main.py"]
