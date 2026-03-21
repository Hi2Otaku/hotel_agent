FROM python:3.12-slim

WORKDIR /app

# Install shared library
COPY shared/ /app/shared/
RUN pip install --no-cache-dir /app/shared

# Install service dependencies
COPY services/booking/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy service code
COPY services/booking/ .

# Make entrypoint executable
RUN chmod +x entrypoint.sh

CMD ["./entrypoint.sh"]
