# Build context is the REPO ROOT (see docker-compose.yml), because some
# services import sibling modules. Build: docker build -f backend/validation/Dockerfile .
FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
RUN useradd --create-home --uid 10001 app
WORKDIR /srv/backend/validation
COPY backend/validation/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/validation/ ./
USER app
EXPOSE 8002
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8002"]
