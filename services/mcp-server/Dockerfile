FROM python:3.12-slim

WORKDIR /app
ENV PYTHONPATH=/app

# Install service dependencies
COPY services/mcp-server/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy service code
COPY services/mcp-server/app/ ./app/

CMD ["python", "-m", "app.server"]
