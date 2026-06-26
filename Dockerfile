FROM python:3.10-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Install dependencies first for better layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# App code + model artifact
COPY textclean.py app.py index.html model.joblib ./

# Cloud Run provides $PORT (default 8080). Bind to it.
ENV PORT=8080
EXPOSE 8080

# Single worker keeps memory low for the free tier; the model is tiny and fast.
CMD exec uvicorn app:app --host 0.0.0.0 --port ${PORT} --workers 1
