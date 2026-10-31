FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

ENV PYTHONUNBUFFERED=1
ENV DATABASE_URL=sqlite:////data/products.db
RUN mkdir -p /data
VOLUME ["/data"]

EXPOSE 5000
CMD ["python", "app.py"]

