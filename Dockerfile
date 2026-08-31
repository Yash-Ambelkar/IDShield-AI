FROM python:3.11-slim

WORKDIR /app

# System libraries required by OpenCV and AI/image processing
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    libgomp1 \
    libgcc-s1 \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copy backend and AI code
COPY ai ./ai
COPY backend ./backend
COPY database ./database
COPY documents ./documents

# Render provides the PORT environment variable
EXPOSE 10000

# Start FastAPI
CMD ["sh", "-c", "uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-10000}"]