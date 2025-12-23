# ===== Base Image =====
FROM python:3.11-slim

# ===== Working Directory =====
WORKDIR /app

# ===== System Dependencies =====
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    git \
    && rm -rf /var/lib/apt/lists/*

# ===== Upgrade pip =====
RUN pip install --no-cache-dir --upgrade pip

# ===== Pre-install heavy packages =====
# Torch CPU version to avoid long compile times
RUN pip install --no-cache-dir torch==2.2.0+cpu torchvision==0.19.0+cpu --index-url https://download.pytorch.org/whl/cpu
# Sentence Transformers
RUN pip install --no-cache-dir sentence-transformers==2.2.2

# ===== Copy and Install Remaining Requirements =====
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ===== Copy Application Code =====
COPY app/ ./app/
COPY scripts/ ./scripts/

# ===== Create Logs Directory =====
RUN mkdir -p logs

# ===== Expose Port =====
EXPOSE 8000

# ===== Healthcheck =====
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import httpx; exit(0 if httpx.get('http://localhost:8000/health', timeout=5.0).status_code == 200 else 1)" || exit 1

# ===== Start Application =====
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
