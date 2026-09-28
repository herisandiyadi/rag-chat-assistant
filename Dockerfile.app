# Build stage
FROM python:3.11-slim as builder

WORKDIR /build

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Torch CPU wheel dulu (~200MB, dari index resmi PyTorch — jauh lebih kecil
# daripada wheel default PyPI yang membundel CUDA ~2GB dan sering timeout).
RUN pip install --retries 10 --timeout 60 --no-cache-dir \
    torch==2.5.0 --index-url https://download.pytorch.org/whl/cpu

COPY requirements.txt .
RUN pip install --retries 10 --timeout 60 --no-cache-dir -r requirements.txt

# Final stage
FROM python:3.11-slim

WORKDIR /app

# Cache transformer model di /app/.cache (writable, ikut image atau volume).
# ponytail: pakai root user — container internal di host terpercaya.
# Upgrade path saat deploy produksi publik: ganti ke USER appuser + volume
# terpisah dengan chown yang benar.
ENV HF_HOME=/app/.cache/huggingface
ENV TRANSFORMERS_CACHE=/app/.cache/huggingface
ENV SENTENCE_TRANSFORMERS_HOME=/app/.cache/huggingface
RUN mkdir -p /app/.cache/huggingface && chmod -R 777 /app/.cache

COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

COPY src/ ./src/
COPY config/ ./config/

EXPOSE 8000

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]