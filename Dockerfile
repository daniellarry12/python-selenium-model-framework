# ============================================================================
# Production-Ready Selenium Framework - Docker Image (OPTIMIZED)
# ============================================================================
# Base: Python 3.11-slim-bookworm (Debian 12)
# Size: ~1.5GB (optimized from 1.73GB)
# Includes: Chromium, ChromeDriver, minimal dependencies
# ============================================================================

# Use specific Debian version for reproducibility
FROM python:3.11-slim-bookworm

# Metadata (for image inspection)
LABEL maintainer="Daniel Aguilar <daniellarry12>" \
      description="Selenium Test Framework with Chromium - Production Ready" \
      version="2.0" \
      python.version="3.11" \
      debian.version="bookworm"

# Environment variables (critical for Docker/Python)
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DEBIAN_FRONTEND=noninteractive \
    DISPLAY=:99 \
    # Pip configuration
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies in ONE layer (minimizes image size)
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Essential certificates (needed for HTTPS)
    ca-certificates \
    # Chromium browser and driver
    chromium \
    chromium-driver \
    # Chromium runtime dependencies (ONLY what's needed)
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
    # Clean up APT cache (saves ~40MB)
    && rm -rf /var/lib/apt/lists/* \
    # Verify Chromium installation
    && chromium --version

# Set working directory
WORKDIR /app

# Copy requirements FIRST (Docker layer caching optimization)
# This layer only rebuilds if requirements.txt changes
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt && \
    # Verify critical packages
    python -c "import selenium; import pytest; print(f'✓ Selenium {selenium.__version__}'); print(f'✓ Pytest {pytest.__version__}')"

# Copy application code (happens AFTER pip install for better caching)
COPY . .

# Create necessary directories and setup user in ONE layer
RUN mkdir -p reports screenshots && \
    # Create non-root user for security
    useradd -m -u 1000 -s /bin/bash testuser && \
    # Set ownership
    chown -R testuser:testuser /app

# Switch to non-root user (security best practice)
USER testuser

# Default command (can be overridden via docker run or docker-compose)
CMD ["pytest", "--browser=chrome", "--env=dev", "--headless", "-v"]

# ============================================================================
# Build Instructions:
# ============================================================================
# docker build -t selenium-framework:optimized -f Dockerfile.optimized .
#
# Run:
# docker run --rm -e DEV_BASE_URL="..." selenium-framework:optimized
#
# Size comparison:
# - Original: 1.73GB
# - Optimized: ~1.50GB
# - Savings: ~230MB (13% reduction)
# ============================================================================
