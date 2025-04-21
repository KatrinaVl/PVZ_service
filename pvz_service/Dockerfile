FROM python:3.12-slim

WORKDIR /pvz_service
    
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENTRYPOINT ["python", "-m", "app"]