# Build stage
FROM python:3.11-slim as builder

WORKDIR /build

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Torch CPU wheel dulu (~200MB, dari index resmi PyTorch — jauh lebih kecil
# daripada wheel default PyPI yang membundel CUDA ~2GB dan sering timeout).
# Dipasang SEBELUM requirements supaya sentence-transformers tidak menarik
# torch versi CUDA.
RUN pip install --retries 10 --timeout 60 --no-cache-dir --user \
    torch==2.5.0 --index-url https://download.pytorch.org/whl/cpu

COPY requirements.txt .
RUN pip install --retries 10 --timeout 60 --no-cache-dir --user -r requirements.txt

# Final stage
FROM python:3.11-slim

WORKDIR /app

RUN groupadd -r appgroup && useradd -r -g appgroup appuser

COPY --from=builder /root/.local /home/appuser/.local
ENV PATH=/home/appuser/.local/bin:$PATH

COPY --chown=appuser:appgroup src/ ./src/
COPY --chown=appuser:appgroup config/ ./config/

USER appuser
EXPOSE 8000

# --reload dihapus: watcher proses tambahan hanya untuk dev, boros memori.
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]