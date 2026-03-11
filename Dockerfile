# -------------------------------
# Pi-Optimized Base Image
# -------------------------------
FROM python:3.11-slim-bullseye

# -------------------------------
# Set working directory & environment
# -------------------------------
WORKDIR /app
ENV DEBIAN_FRONTEND=noninteractive
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

# -------------------------------
# Install system dependencies for Pi GPIO & cameras
# -------------------------------
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    python3-dev \
    python3-pip \
    libatlas-base-dev \
    libjpeg-dev \
    libtiff-dev \
    libopenjp2-7-dev \
    libavcodec-dev \
    libavformat-dev \
    libswscale-dev \
    libgpiod2 \
    libgpiod-dev \
    libcap-dev \
    pkg-config \
    cmake \
    git \
    curl \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# -------------------------------
# Upgrade pip tools
# -------------------------------
RUN pip install --upgrade pip setuptools wheel

# -------------------------------
# Copy and install Python dependencies
# -------------------------------
COPY requirements.txt .
# Use precompiled wheels when possible to avoid source compilation
RUN pip install --no-cache-dir -r requirements.txt

# -------------------------------
# Copy hardware scripts
# -------------------------------
COPY ./hardware ./hardware

# -------------------------------
# Create non-root user for security
# -------------------------------
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# -------------------------------
# Set working directory
# -------------------------------
WORKDIR /app/hardware

# -------------------------------
# Default command
# -------------------------------
CMD ["python3", "camera_stream_service.py"]