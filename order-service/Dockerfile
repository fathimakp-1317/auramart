# ─── Base Image ───────────────────────────────
FROM python:3.11-slim

# set environment variables
# prevents Python from writing .pyc files
ENV PYTHONDONTWRITEBYTECODE=1
# prevents Python from buffering stdout/stderr
ENV PYTHONUNBUFFERED=1

# set working directory
WORKDIR /app

# ─── Install System Dependencies ──────────────
RUN apt-get update \
    && apt-get install -y \
        gcc \
        postgresql-client \
        netcat-traditional \
    && rm -rf /var/lib/apt/lists/*

# ─── Install Python Dependencies ──────────────
# copy requirements first
# Docker caches this layer
# so it only reinstalls when
# requirements.txt changes
COPY requirements.txt .
RUN pip install --no-cache-dir \
    -r requirements.txt

# ─── Copy Project Files ───────────────────────
COPY . .

# ─── Make entrypoint executable ───────────────
RUN chmod +x entrypoint.sh

# ─── Expose Port ──────────────────────────────
EXPOSE 5003

# ─── Start Command ────────────────────────────
CMD ["./entrypoint.sh"]