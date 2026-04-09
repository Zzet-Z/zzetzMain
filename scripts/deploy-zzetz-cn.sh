#!/usr/bin/env bash

set -euo pipefail

REPO_URL="${REPO_URL:-https://github.com/Zzet-Z/zzetzMain.git}"
BRANCH="${BRANCH:-main}"
APP_DIR="${APP_DIR:-/opt/zzetzMain}"
WEB_ROOT="${WEB_ROOT:-/var/www/zzetz.cn}"
SERVICE_NAME="${SERVICE_NAME:-zzetz-backend}"
DOMAIN="${DOMAIN:-zzetz.cn}"
WWW_DOMAIN="${WWW_DOMAIN:-www.zzetz.cn}"
BACKEND_PORT="${BACKEND_PORT:-5050}"
PIP_INDEX_URL="${PIP_INDEX_URL:-https://pypi.org/simple}"

require_cmd() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "missing required command: $1" >&2
    exit 1
  fi
}

upsert_env_var() {
  local file="$1"
  local key="$2"
  local value="$3"

  if grep -q "^${key}=" "$file"; then
    python3 - "$file" "$key" "$value" <<'PY'
from pathlib import Path
import sys

path = Path(sys.argv[1])
key = sys.argv[2]
value = sys.argv[3]
lines = path.read_text().splitlines()
updated = []
for line in lines:
    if line.startswith(f"{key}="):
        updated.append(f"{key}={value}")
    else:
        updated.append(line)
path.write_text("\n".join(updated) + "\n")
PY
  else
    printf '%s=%s\n' "$key" "$value" >>"$file"
  fi
}

require_cmd git
require_cmd python3
require_cmd npm
require_cmd nginx
require_cmd systemctl
require_cmd curl

if [[ ! -d "$APP_DIR/.git" ]]; then
  git clone "$REPO_URL" "$APP_DIR"
fi

cd "$APP_DIR"
git fetch origin "$BRANCH"
git checkout "$BRANCH"
git pull --ff-only origin "$BRANCH"

if [[ ! -f "$APP_DIR/backend/.env" ]]; then
  if [[ -f "$APP_DIR/.env.local" ]]; then
    cp "$APP_DIR/.env.local" "$APP_DIR/backend/.env"
  else
    echo "missing backend/.env; copy your API key config to $APP_DIR/backend/.env first" >&2
    exit 1
  fi
fi

upsert_env_var "$APP_DIR/backend/.env" "FLASK_ENV" "production"
upsert_env_var "$APP_DIR/backend/.env" "FLASK_PORT" "$BACKEND_PORT"
upsert_env_var "$APP_DIR/backend/.env" "OPENAI_TIMEOUT" "120"
upsert_env_var "$APP_DIR/backend/.env" "UPLOAD_FOLDER" "uploads"

mkdir -p "$APP_DIR/backend/uploads"
mkdir -p "$WEB_ROOT"

cd "$APP_DIR/frontend"
if [[ -f package-lock.json ]]; then
  npm ci
else
  npm install
fi
VITE_API_BASE_URL= npm run build

rm -rf "${WEB_ROOT:?}/"*
cp -a "$APP_DIR/frontend/dist/." "$WEB_ROOT/"

cd "$APP_DIR/backend"
python3 -m venv .venv
. .venv/bin/activate
PIP_INDEX_URL="$PIP_INDEX_URL" pip install -U pip setuptools wheel
PIP_INDEX_URL="$PIP_INDEX_URL" pip install -e . gunicorn

cat >"/etc/systemd/system/${SERVICE_NAME}.service" <<EOF
[Unit]
Description=zzetzMain backend
After=network.target

[Service]
Type=simple
WorkingDirectory=$APP_DIR/backend
EnvironmentFile=$APP_DIR/backend/.env
Environment=FLASK_ENV=production
ExecStart=$APP_DIR/backend/.venv/bin/gunicorn --workers 2 --timeout 420 --graceful-timeout 30 --bind 127.0.0.1:${BACKEND_PORT} 'app:create_app()'
Restart=always
RestartSec=5
TimeoutStopSec=30

[Install]
WantedBy=multi-user.target
EOF

cat >"/etc/nginx/conf.d/${DOMAIN}.conf" <<EOF
server {
    server_name $DOMAIN $WWW_DOMAIN;
    root $WEB_ROOT;
    index index.html;

    location ^~ /.well-known/acme-challenge/ {
        default_type text/plain;
        allow all;
    }

    location /api/ {
        proxy_pass http://127.0.0.1:${BACKEND_PORT};
        proxy_http_version 1.1;
        proxy_connect_timeout 420s;
        proxy_send_timeout 420s;
        proxy_read_timeout 420s;
        send_timeout 420s;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location / {
        try_files \$uri \$uri/ /index.html;
    }

    location ~ /\. {
        deny all;
    }

    listen [::]:443 ssl ipv6only=on;
    listen 443 ssl;
    ssl_certificate /etc/letsencrypt/live/$DOMAIN/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/$DOMAIN/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;
}

server {
    if (\$host = $WWW_DOMAIN) {
        return 301 https://\$host\$request_uri;
    }

    if (\$host = $DOMAIN) {
        return 301 https://\$host\$request_uri;
    }

    listen 80;
    listen [::]:80;
    server_name $DOMAIN $WWW_DOMAIN;
    return 404;
}
EOF

systemctl daemon-reload
systemctl enable --now "$SERVICE_NAME"
nginx -t
systemctl reload nginx

APP_DIR="$APP_DIR" python3 -m app.db_migrations "$APP_DIR/backend/app.db"

APP_DIR="$APP_DIR" python3 - <<'PY'
import os
import sqlite3

conn = sqlite3.connect(f"{os.environ['APP_DIR']}/backend/app.db")
cur = conn.cursor()
cur.execute("update sessions set status='in_progress', queued_at=NULL where status in ('active','queued')")
conn.commit()
conn.close()
PY

echo "health:"
curl -sS "http://127.0.0.1:${BACKEND_PORT}/api/health"
echo
echo "public health:"
curl -sS "https://${DOMAIN}/api/health"
echo
