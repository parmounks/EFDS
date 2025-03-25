FROM python:3.10-slim

WORKDIR /app
COPY . /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


EXPOSE 6000
CMD ["python", "urt_data.py"]
