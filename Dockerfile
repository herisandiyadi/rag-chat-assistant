FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
# ponytail: default-retries agar download besar tahan jaringan lambat.
RUN pip install --no-cache-dir --timeout 120 --retries 10 -r requirements.txt

COPY . .

ENV PYTHONPATH=/app/src
EXPOSE 8000

CMD ["uvicorn", "socket_server:app", "--host", "0.0.0.0", "--port", "8000"]
