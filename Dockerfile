# ============================================================================
# Production-Ready Selenium Framework - Docker Image
# ============================================================================
# Base: Python 3.11 (slim for smaller image size)
# Includes: Chrome, ChromeDriver, and all test dependencies
# ============================================================================

FROM python:3.11-slim

# Metadata
LABEL maintainer="Daniel Aguilar <daniellarry12>"
LABEL description="Selenium Test Framework with Chrome - Production Ready"
LABEL version="1.0"

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DEBIAN_FRONTEND=noninteractive \
    DISPLAY=:99

# Install system dependencies
RUN apt-get update && apt-get install -y \
    # Essential tools
    wget \
    gnupg \
    unzip \
    curl \
    ca-certificates \
    # Chrome dependencies
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libatspi2.0-0 \
    libcups2 \
    libdbus-1-3 \
    libdrm2 \
    libgbm1 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libwayland-client0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxkbcommon0 \
    libxrandr2 \
    xdg-utils \
    # Clean up
    && rm -rf /var/lib/apt/lists/*

# Install Chromium (supports both amd64 and arm64)
RUN apt-get update \
    && apt-get install -y chromium chromium-driver \
    && rm -rf /var/lib/apt/lists/*

# Verify Chromium installation
RUN chromium --version

# Set working directory
WORKDIR /app

# Copy requirements first (for Docker layer caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Create directories for reports and screenshots
RUN mkdir -p reports screenshots

# Create a non-root user for security
RUN useradd -m -u 1000 testuser && \
    chown -R testuser:testuser /app

# Switch to non-root user
USER testuser

# Health check (verify pytest is installed)
RUN python -c "import pytest; print(f'Pytest version: {pytest.__version__}')"

# Default command (can be overridden)
CMD ["pytest", "--browser=chrome", "--env=dev", "--headless", "-v"]