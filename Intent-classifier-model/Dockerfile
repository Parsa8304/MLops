FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .

RUN apt-get update \
 && apt-get install -y --no-install-recommends gcc libc-dev \
 && pip install --no-cache-dir -r requirements.txt \
 && apt-get remove -y gcc libc-dev \
 && apt-get autoremove -y \
 && rm -rf /var/lib/apt/lists/*


COPY . .

RUN python3 model/train.py 

EXPOSE 6000


CMD [ "gunicorn", "--workers", "4", "--bind", "0.0.0.0:6000", "wsgi:app" ]
