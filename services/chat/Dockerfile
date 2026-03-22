FROM python:3.12-slim

WORKDIR /app
ENV PYTHONPATH=/app

# Install shared library
COPY shared/ /app/shared/
RUN pip install --no-cache-dir /app/shared

# Install service dependencies
COPY services/chat/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy service code
COPY services/chat/ .

# Make entrypoint executable
RUN chmod +x entrypoint.sh

CMD ["./entrypoint.sh"]
