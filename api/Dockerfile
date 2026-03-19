FROM python:3.12-slim

WORKDIR /app

# iproute2 provides `ip` used for local subnet detection
RUN apt-get update && apt-get install -y --no-install-recommends iproute2 ca-certificates curl && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir fastapi uvicorn[standard] sqlmodel httpx pydantic-settings jinja2 python-multipart

COPY . /app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
