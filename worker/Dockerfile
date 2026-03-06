FROM python:3.12-slim

WORKDIR /app

RUN apt-get update \
  && apt-get install -y --no-install-recommends ca-certificates ffmpeg \
  && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir httpx pydantic-settings

COPY . /app
RUN chmod +x /app/rtsp_grab.sh

CMD ["python", "-u", "worker.py"]
