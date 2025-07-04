FROM python:3.11-slim
ENV TRANSFORMERS_CACHE=/models
WORKDIR /app
COPY server.py /app/
RUN pip install --no-cache-dir fastapi "uvicorn[standard]" transformers \
    sentencepiece accelerate httpx

CMD ["uvicorn","server:app","--host","0.0.0.0","--port","8001"]
DOCK