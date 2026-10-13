
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

# Install the system library required by LightGBM
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

RUN useradd --create-home --uid 10001 app

WORKDIR /srv/backend/synthesis

COPY backend/synthesis/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY ml/models/ /srv/ml/models/
COPY ml/routing/ /srv/ml/routing/
COPY ml/federated/uci_heart.py /srv/ml/federated/uci_heart.py
COPY ml/federated/datasets/ /srv/ml/federated/datasets/
COPY backend/synthesis/ ./

USER app

EXPOSE 8006

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8006"]
