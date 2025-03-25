FROM python:3.10-slim

WORKDIR /app
COPY . /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Optional: force CPU mode
ENV CUDA_VISIBLE_DEVICES=""

EXPOSE 8080
CMD ["python", "model_detect.py"]
