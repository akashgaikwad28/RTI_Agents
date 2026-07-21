# Stage 1: Build
FROM python:3.11.8-slim AS build

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl git \
 && rm -rf /var/lib/apt/lists/*

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=off

# Create and activate virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip setuptools wheel
RUN pip install --no-cache-dir --prefer-binary -r requirements.txt

COPY . .

# Stage 2: Runtime
FROM python:3.11.8-slim AS runtime

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates curl \
 && rm -rf /var/lib/apt/lists/*

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN useradd --create-home --shell /bin/bash appuser
WORKDIR /home/appuser/app
USER appuser

COPY --from=build /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY --chown=appuser:appuser . .

# Create writable directories
RUN mkdir -p logs data/vector_store data/checkpoints data/documents data/synthetic_corpus

ENV PYTHONPATH=/home/appuser/app \
    APP_ENV=production \
    PORT=8000

EXPOSE 8000

# Entry point: FastAPI via uvicorn
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000", "--log-level", "info", "--workers", "1"]
