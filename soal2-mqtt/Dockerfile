FROM python:3.12-slim
WORKDIR /app
RUN pip install --no-cache-dir paho-mqtt
COPY publisher.py subscriber.py ./
CMD ["python", "publisher.py"]
