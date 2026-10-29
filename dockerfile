# syntax=docker/dockerfile:1
FROM python:slim-trixie

WORKDIR /root/main
COPY . .

RUN apt-get update -y && apt-get install -y --no-install-recommends sqlite3 \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir -r requirements.txt

ENV HOST=::
ENV PORT=443

CMD ["python3", "__main__.py"]
