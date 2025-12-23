# Slim aur lightweight base image
FROM python:3.11-slim

# Working directory set karo
WORKDIR /app

# System dependencies (sirf jo zaruri hain, gcc etc. for potential wheels)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Requirements copy karo pehle (better Docker layer caching ke liye)
COPY requirements.txt .

# Pip upgrade aur packages install (no cache = smaller image)
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Application code copy karo
COPY app/ ./app/
COPY scripts/ ./scripts/

# Logs folder banao (agar code mein use ho raha hai)
RUN mkdir -p logs

# Port expose karo (docs ke liye helpful, lekin Railway ignore karta hai)
EXPOSE 8000

# Health check (optional lekin achha practice hai – /health endpoint hona chahiye)
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import httpx; exit(0 if httpx.get('http://localhost:8000/health', timeout=5.0).status_code == 200 else 1)" || exit 1

# Final CMD – ye Railway ke liye perfect hai ($PORT automatically expand hoga)
CMD uvicorn app.main:app --host 0.0.0.0 --port $PORT
