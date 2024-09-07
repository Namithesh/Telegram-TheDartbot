FROM python:3.12.4-slim-bullseye
WORKDIR /dart
COPY . ./
RUN pip install --no-cache-dir -r requirements.txt
CMD ["python3", "dart.py"]
VOLUME /data
