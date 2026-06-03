FROM python:3.12-slim AS base

WORKDIR /app

# System dependencies
# - curl: healthcheck
# - libpango / libpangocairo / libgdk-pixbuf / libffi-dev: WeasyPrint runtime (renders the Locandina A6 cards to PDF)
# - poppler-utils: ships pdftoppm, used to rasterise the WeasyPrint PDF to PNG for the mobile-friendly preview
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf2.0-0 \
    libffi-dev \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Application code
COPY . .

# Health check
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health || exit 1

EXPOSE 8000

# --proxy-headers makes uvicorn trust Caddy's X-Forwarded-Proto / -For / -Host,
# so request.url.scheme is "https" (not "http"). Without this, FastAPI's 307
# trailing-slash redirects emit Location: http://... which the browser blocks
# as mixed content -- silently killing any fetch hitting a no-slash collection
# route (see lesson-trailing-slash-mixed-content-redirect). Only the proxy can
# reach this container on the internal Docker network, so '*' = "trust Caddy."
# (The rate limiter already parses X-Forwarded-For itself; behavior unchanged.)
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers", "--forwarded-allow-ips", "*"]
