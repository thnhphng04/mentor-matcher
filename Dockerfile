FROM python:3.12-slim

WORKDIR /app

# Install deps first for layer caching.
COPY requirements.txt pyproject.toml ./
RUN pip install --no-cache-dir -r requirements.txt

# App code + data + committed enrichment cache.
COPY . .
RUN pip install --no-cache-dir -e .

# Render provides $PORT; default to 8501 for local `docker run`.
ENV PORT=8501
EXPOSE 8501

# Shell form so $PORT expands at runtime.
CMD streamlit run app/streamlit_app.py \
    --server.port ${PORT} \
    --server.address 0.0.0.0 \
    --server.headless true
