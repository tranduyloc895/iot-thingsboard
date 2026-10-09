FROM python:3.9-slim

# Cài đặt thư viện paho-mqtt
RUN pip install --no-cache-dir paho-mqtt

# Đưa file code vào container
WORKDIR /app
COPY single_device_simulator.py .

# Chạy script khi container khởi động
CMD ["python", "single_device_simulator.py"]
