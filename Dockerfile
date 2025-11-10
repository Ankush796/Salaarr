# Stable Debian base (no 404 issues)
FROM python:3.9-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /app

# System packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    libffi-dev \
    ffmpeg \
    mediainfo \
    aria2 \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

# Upgrade pip (fast)
RUN python -m pip install --upgrade pip

# Install python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy whole project
COPY . .

# Start bot
CMD ["python", "main.py"]
