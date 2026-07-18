FROM python:3.12-slim

# WeasyPrint system dependencies (Pango, Cairo, GDK-PixBuf, fonts)
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    libcairo2 \
    libgdk-pixbuf-2.0-0 \
    libffi-dev \
    libjpeg62-turbo \
    fontconfig \
    fonts-liberation \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# Install all Python dependencies (TradingAgents-Funds from GitHub + runner deps).
# Doing this before copying source maximises Docker layer cache reuse.
COPY pyproject.toml .
RUN uv pip install --system --no-cache .

# Copy runner source — config.py is intentionally excluded; it is always
# mounted at runtime so the image does not need to be rebuilt on config changes.
COPY runner/ runner/

RUN mkdir -p /app/reports

CMD ["python", "-m", "runner.main"]
