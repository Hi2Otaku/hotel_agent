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

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
