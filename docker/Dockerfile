# Slim base keeps the image small; 3.12 matches the version pinned for reproducibility.
FROM python:3.12-slim

WORKDIR /app

# Install deps first so this layer is cached unless requirements.txt changes.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code.
COPY app ./app

EXPOSE 8000

# uvicorn binds 0.0.0.0 so the port is reachable from outside the container.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
