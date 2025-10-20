# Stage 1: build
FROM python:3.11.8-slim AS build

# Install build deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
 && rm -rf /var/lib/apt/lists/*

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    POETRY_VIRTUALENVS_CREATE=false

# Create app user
RUN useradd --create-home --shell /bin/bash appuser
WORKDIR /home/appuser/app
USER appuser

# Copy only requirements first for caching
COPY --chown=appuser:appuser requirements.txt pyproject.toml uv.lock ./

# Install dependencies
# using pip; if you use poetry or pip-compile, adjust accordingly
RUN python -m pip install --upgrade pip setuptools wheel
RUN python -m pip install -r requirements.txt

# Copy project
COPY --chown=appuser:appuser . .

# Stage 2: runtime
FROM python:3.11.8-slim AS runtime

# minimal runtime deps if any
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
 && rm -rf /var/lib/apt/lists/*

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# create non-root user
RUN useradd --create-home --shell /bin/bash appuser
WORKDIR /home/appuser/app
USER appuser

# copy installed packages from build stage
COPY --from=build /usr/local/lib/python3.11 /usr/local/lib/python3.11
COPY --from=build /usr/local/bin /usr/local/bin

# copy app code
COPY --chown=appuser:appuser --from=build /home/appuser/app /home/appuser/app

# create logs dir and ensure permissions
RUN mkdir -p /home/appuser/app/logs && chmod -R 755 /home/appuser/app/logs

# set env default config (override via docker-compose or env)
ENV PYTHONPATH=/home/appuser/app \
    APP_ENV=production \
    PORT=8000 \
    MONGO_URI=mongodb://mongo:27017/

EXPOSE 8000

# Use uvicorn (assumes FastAPI app object is in app:app)
# Use --proxy-headers if you deploy behind reverse proxy
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--log-level", "info", "--workers", "1"]
