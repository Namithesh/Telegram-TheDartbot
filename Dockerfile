FROM amd64/pypy:latest
WORKDIR /dart
COPY . ./
RUN pip install --no-cache-dir -r requirements.txt
CMD ["python3", "dart.py"]
VOLUME /data
