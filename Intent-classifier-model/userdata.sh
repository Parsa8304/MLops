#!/bin/bash
#
# STAGE 6: Deployment.
# EC2 "user data" script: paste this into the instance launch wizard (or run it
# on a fresh Ubuntu box) to provision the app as a systemd service behind Nginx.
#
#   Internet  ->  Nginx :80  ->  Gunicorn :6000  ->  Flask app (wsgi:app)
#
set -e

# --- Directory ---
export APP_DIR=/opt/intent-app
mkdir -p "$APP_DIR"
cd "$APP_DIR"

# --- Update packages ---
apt update -y
apt install -y git python3 python3-venv python3-pip nginx

# --- Git clone (download the app) ---
git clone https://github.com/Parsa8304/Intent-classifier-model.git .

# --- Python virtual environment + train the model ---
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
python3 model/train.py

# --- Gunicorn WSGI server as a systemd service ---
cat >/etc/systemd/system/intent_gunicorn.service <<'EOF'
[Unit]
Description=Gunicorn instance for Intent Classifier
After=network.target

[Service]
User=ubuntu
Group=ubuntu
WorkingDirectory=/opt/intent-app
Environment="PATH=/opt/intent-app/venv/bin"
ExecStart=/opt/intent-app/venv/bin/gunicorn --workers 3 --bind 0.0.0.0:6000 wsgi:app
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# --- Nginx reverse proxy in front of Gunicorn ---
cat >/etc/nginx/conf.d/intent_app.conf <<'EOF'
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:6000/predict;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_connect_timeout 60s;
        proxy_read_timeout 360s;
    }
}
EOF

# --- Enable & start services ---
systemctl daemon-reload
systemctl enable intent_gunicorn
systemctl start intent_gunicorn
systemctl enable nginx
systemctl restart nginx
