# ===== Hugging Face Spaces Dockerfile =====
# Optimized for HF Spaces deployment with port 7860
# Includes FastAPI RAG chatbot with OpenAI Agents SDK, Qdrant, and Neon PostgreSQL

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# ===== System Dependencies =====
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# ===== Upgrade pip =====
RUN pip install --no-cache-dir --upgrade pip

# ===== Install PyTorch CPU (lightweight for embeddings) =====
# Using CPU-only version to minimize image size for HF Spaces
RUN pip install --no-cache-dir torch==2.6.0+cpu torchvision==0.21.0+cpu --index-url https://download.pytorch.org/whl/cpu

# ===== Copy requirements and install dependencies =====
# Note: sentence-transformers is installed via requirements.txt
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ===== Copy Application Code =====
COPY app/ ./app/
COPY scripts/ ./scripts/

# ===== Create Logs Directory =====
RUN mkdir -p logs

# ===== Create non-root user for security =====
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# ===== Expose HF Spaces Default Port =====
EXPOSE 7860

# ===== Health Check =====
# HF Spaces expects the application to respond on port 7860
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:7860/health || exit 1

# ===== Start Application =====
# HF Spaces sets PORT=7860 by default, but we'll use 7860 explicitly
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860", "--log-level", "info"]
