# Build context is the REPO ROOT (see docker-compose.yml), because some
# services import sibling modules. Build: docker build -f backend/auth/Dockerfile .
FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
RUN useradd --create-home --uid 10001 app
WORKDIR /srv/backend/auth
COPY backend/auth/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/auth/ ./
USER app
EXPOSE 8001
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
