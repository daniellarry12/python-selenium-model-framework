# 🐳 Docker Guide - Selenium Test Framework

Complete guide for running tests in Docker containers. Ensures **100% consistency** across all environments.

---

## 📚 Table of Contents

- [Why Docker?](#-why-docker)
- [Prerequisites](#-prerequisites)
- [Quick Start](#-quick-start)
- [Common Commands](#-common-commands)
- [Environment Variables](#-environment-variables)
- [Volume Mounts](#-volume-mounts)
- [Troubleshooting](#-troubleshooting)
- [Advanced Usage](#-advanced-usage)

---

## 🤔 Why Docker?

### **Problem: "It works on my machine" 🤷**

```bash
# Without Docker
Developer A: Python 3.11 + Chrome 120 → ✅ Tests pass
Developer B: Python 3.9 + Chrome 115 → ❌ Tests fail
CI/CD Server: Python 3.11 + Chrome 125 → ❌ Tests fail

# With Docker
Developer A: Docker → ✅ Tests pass
Developer B: Docker → ✅ Tests pass
CI/CD Server: Docker → ✅ Tests pass
```

### **Benefits:**

✅ **Consistency** - Same environment everywhere (local, CI/CD, production)
✅ **Fast Setup** - From zero to running tests in 2 minutes
✅ **Isolation** - No conflicts with system packages
✅ **Portability** - Works on Windows, macOS, Linux
✅ **Reproducibility** - Exact same Chrome/Python versions
✅ **Clean** - No pollution of host system

---

## 📋 Prerequisites

### 1. **Install Docker**

**macOS:**
```bash
# Install Docker Desktop
brew install --cask docker

# Or download from: https://www.docker.com/products/docker-desktop
```

**Ubuntu/Debian:**
```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker
```

**Windows:**
```bash
# Download and install Docker Desktop
# https://www.docker.com/products/docker-desktop
```

### 2. **Install Docker Compose** (usually included with Docker Desktop)

```bash
# Verify installation
docker --version
docker-compose --version
```

Expected output:
```
Docker version 24.0.0, build xyz
Docker Compose version v2.20.0
```

---

## 🚀 Quick Start

### **Option 1: Docker Compose (Recommended)**

```bash
# 1. Clone the repository
git clone https://github.com/daniellarry12/python-selenium-model-framework.git
cd python-selenium-model-framework

# 2. Run tests with Docker Compose
docker-compose up

# That's it! ✅
# Tests run automatically in Chrome headless mode
```

### **Option 2: Docker Commands**

```bash
# 1. Build the Docker image
docker build -t selenium-framework .

# 2. Run tests
docker run --rm \
  -e DEV_BASE_URL="https://ecommerce-playground.lambdatest.io/..." \
  -e DEV_TEST_EMAIL="pytesttutorial@gmail.com" \
  -e DEV_TEST_PASSWORD="Jahlove1912$" \
  selenium-framework \
  pytest --browser=chrome --headless -v
```

---

## 📋 Common Commands

### **Basic Operations**

```bash
# Build the image
docker-compose build

# Run tests (default: chrome, dev, headless)
docker-compose up

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f tests

# Stop containers
docker-compose down

# Remove everything (containers, networks, volumes)
docker-compose down -v
```

### **Running Specific Tests**

```bash
# Smoke tests only
docker-compose run tests pytest -m smoke

# Specific test file
docker-compose run tests pytest tests/test_login.py -v

# With HTML report
docker-compose run tests pytest --html=reports/report.html --self-contained-html

# Staging environment
docker-compose run tests pytest --env=staging --headless

# Multiple browsers (if supported)
docker-compose run tests pytest --browser=all
```

### **Interactive Mode**

```bash
# Open bash shell inside container
docker-compose run tests bash

# Inside container, run commands manually:
pytest -m smoke
pytest --browser=chrome -v
python -c "import selenium; print(selenium.__version__)"
exit
```

### **Development Mode (Live Code Reload)**

```bash
# Run with volume mount (code changes reflected immediately)
docker-compose run tests pytest -v

# Edit files on host → Changes apply instantly in container ✅
```

---

## 🔐 Environment Variables

### **Method 1: .env File (Recommended)**

Your `.env` file is automatically loaded by Docker Compose:

```bash
# .env (already configured)
TEST_ENV=dev
DEV_BASE_URL=https://ecommerce-playground.lambdatest.io/...
DEV_TEST_EMAIL=pytesttutorial@gmail.com
DEV_TEST_PASSWORD=Jahlove1912$
```

### **Method 2: Override at Runtime**

```bash
# Override environment
docker-compose run -e TEST_ENV=staging tests pytest

# Override multiple variables
docker-compose run \
  -e DEV_BASE_URL="https://new-url.com" \
  -e DEV_TEST_EMAIL="new@email.com" \
  tests pytest -m smoke
```

### **Method 3: Docker Compose Override File**

Create `docker-compose.override.yml`:

```yaml
version: '3.8'

services:
  tests:
    environment:
      - TEST_ENV=staging
      - DEV_BASE_URL=https://my-custom-url.com
```

Docker Compose automatically merges this with `docker-compose.yml`.

---

## 📂 Volume Mounts

### **Understanding Volumes**

```yaml
volumes:
  - .:/app                    # Sync source code (live reload)
  - ./reports:/app/reports    # Persist reports on host
  - ./screenshots:/app/screenshots  # Persist screenshots
```

### **What Gets Synced?**

| Path | Direction | Purpose |
|------|-----------|---------|
| `.:/app` | Host → Container | Code changes reflected instantly |
| `./reports:/app/reports` | Container → Host | Save test reports |
| `./screenshots:/app/screenshots` | Container → Host | Save failure screenshots |

### **Accessing Reports**

```bash
# Run tests
docker-compose run tests pytest --html=reports/report.html

# Reports are saved to ./reports on your host machine
open reports/report.html  # macOS
xdg-open reports/report.html  # Linux
start reports/report.html  # Windows
```

---

## 🐛 Troubleshooting

### **Issue 1: Permission Denied**

```bash
# Error: permission denied while trying to connect to Docker daemon

# Solution (Linux/macOS):
sudo usermod -aG docker $USER
newgrp docker

# Or run with sudo (not recommended):
sudo docker-compose up
```

### **Issue 2: Port Already in Use**

```bash
# Error: Bind for 0.0.0.0:4444 failed: port is already allocated

# Solution: Stop conflicting containers
docker ps  # Find container using port
docker stop <container_id>

# Or change port in docker-compose.yml
```

### **Issue 3: Out of Disk Space**

```bash
# Error: no space left on device

# Solution: Clean up Docker
docker system prune -a --volumes

# Remove unused images
docker image prune -a

# Remove all stopped containers
docker container prune
```

### **Issue 4: Tests Fail in Docker but Pass Locally**

```bash
# Possible causes:
# 1. Missing environment variables
docker-compose run tests env  # Check all env vars

# 2. Chrome/Driver version mismatch
docker-compose run tests google-chrome --version

# 3. Shared memory issue
# Solution: Increase shm_size in docker-compose.yml
shm_size: 4gb  # Instead of 2gb
```

### **Issue 5: Slow Build Times**

```bash
# Problem: Docker rebuilds everything on each change

# Solution 1: Use Docker layer caching (already implemented)
# Solution 2: Use BuildKit
export DOCKER_BUILDKIT=1
docker-compose build

# Solution 3: Multi-stage builds (for production)
# Already optimized in Dockerfile
```

---

## 🔧 Advanced Usage

### **1. Build with Custom Tags**

```bash
# Build with version tag
docker build -t selenium-framework:v1.0 .

# Build with latest and version
docker build -t selenium-framework:latest -t selenium-framework:v1.0 .

# Push to Docker Hub (optional)
docker tag selenium-framework:latest yourusername/selenium-framework:latest
docker push yourusername/selenium-framework:latest
```

### **2. Multi-Stage Builds (Reduce Image Size)**

Current Dockerfile already uses best practices, but for production:

```dockerfile
# Stage 1: Build dependencies
FROM python:3.11-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim
COPY --from=builder /root/.local /root/.local
COPY . /app
WORKDIR /app
CMD ["pytest"]
```

### **3. Resource Limits**

```yaml
# docker-compose.yml
services:
  tests:
    deploy:
      resources:
        limits:
          cpus: '2.0'      # Max 2 CPUs
          memory: 4G        # Max 4GB RAM
        reservations:
          cpus: '1.0'      # Min 1 CPU
          memory: 2G        # Min 2GB RAM
```

### **4. Health Checks**

```yaml
services:
  tests:
    healthcheck:
      test: ["CMD", "python", "-c", "import selenium"]
      interval: 30s
      timeout: 10s
      retries: 3
```

### **5. Parallel Execution (Future)**

```bash
# Run multiple containers in parallel
docker-compose up --scale tests=5

# Each container runs different tests
# 5x faster execution ⚡
```

---

## 📊 Performance Comparison

| Scenario | Without Docker | With Docker |
|----------|---------------|-------------|
| **First Setup** | 30-60 min | 2-3 min |
| **Build Time** | N/A | 1-2 min (first), 10s (cached) |
| **Test Execution** | Same | Same |
| **Consistency** | ⚠️ Variable | ✅ 100% |
| **Portability** | ❌ No | ✅ Yes |

---

## 🎯 Best Practices

### **DO ✅**

```bash
# Use docker-compose for simplicity
docker-compose up

# Keep .env file secure (in .gitignore)
# Use volume mounts for development
# Clean up regularly
docker system prune
```

### **DON'T ❌**

```bash
# Don't hardcode secrets in Dockerfile
# Don't run as root (already handled)
# Don't commit .env file
# Don't skip .dockerignore
```

---

## 📚 Additional Resources

- [Official Docker Docs](https://docs.docker.com/)
- [Docker Compose Docs](https://docs.docker.com/compose/)
- [Selenium Docker Images](https://github.com/SeleniumHQ/docker-selenium)
- [Best Practices Guide](https://docs.docker.com/develop/dev-best-practices/)

---

## 🆘 Getting Help

**Still having issues?**

1. Check logs: `docker-compose logs tests`
2. Debug interactively: `docker-compose run tests bash`
3. Check environment: `docker-compose run tests env`
4. Rebuild from scratch: `docker-compose build --no-cache`
5. Open an issue: [GitHub Issues](https://github.com/daniellarry12/python-selenium-model-framework/issues)

---

<div align="center">

**🐳 Happy Dockerizing! 🐳**

[Back to Main README](README.md)

</div>