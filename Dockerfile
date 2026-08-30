FROM python:3.11-slim

WORKDIR /app

# Install system libraries required by OpenCV,
# PaddleOCR and other image-processing packages
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copy backend and AI code
COPY backend ./backend
COPY ai ./ai

# Required directories
COPY database ./database
COPY documents ./documents

# Railway provides PORT
CMD ["sh", "-c", "uvicorn backend.main:app --host 0.0.0.0 --port $PORT"]