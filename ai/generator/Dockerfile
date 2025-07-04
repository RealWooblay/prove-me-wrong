FROM python:3.11-slim AS base
ENV TRANSFORMERS_CACHE=/models
WORKDIR /app
COPY server.py /app/

RUN pip install --no-cache-dir fastapi "uvicorn[standard]" \
    transformers sentencepiece accelerate bitsandbytes \
    torch --extra-index-url https://download.pytorch.org/whl/cpu

CMD ["uvicorn","server:app","--host","0.0.0.0","--port","8000"]
DOCK