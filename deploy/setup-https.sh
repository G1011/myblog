#!/bin/bash
# =============================================================================
# setup-https.sh — HTTPS 配置脚本（需已有域名并解析到服务器）
# 用法：bash setup-https.sh your-domain.com admin@your-domain.com
# =============================================================================
set -e

DEPLOY_DIR="/opt/myblog"
DOMAIN="${1}"
EMAIL="${2}"

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; NC='\033[0m'
info()  { echo -e "${GREEN}[INFO]${NC}  $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }

[ -z "$DOMAIN" ] && error "用法: bash setup-https.sh <域名> <邮箱>\n  例如: bash setup-https.sh blog.example.com admin@example.com"
[ -z "$EMAIL"  ] && error "请提供邮箱地址用于 Let's Encrypt 证书通知"

# ─── 1. 申请证书（临时停止 Nginx 释放 80 端口）─────────────────────────────
info "临时停止 Nginx 以申请证书..."
cd "$DEPLOY_DIR"
docker compose stop nginx

info "申请 Let's Encrypt 证书（域名: $DOMAIN）..."
certbot certonly --standalone \
    --non-interactive \
    --agree-tos \
    --email "$EMAIL" \
    -d "$DOMAIN"

CERT_DIR="/etc/letsencrypt/live/$DOMAIN"
info "证书已申请：$CERT_DIR"

# ─── 2. 更新 Nginx 配置以支持 HTTPS ─────────────────────────────────────────
info "更新 Nginx 配置..."
mkdir -p "$DEPLOY_DIR/nginx/certs"

# 软链证书到项目目录（方便 Docker 挂载）
ln -sf "$CERT_DIR/fullchain.pem" "$DEPLOY_DIR/nginx/certs/fullchain.pem"
ln -sf "$CERT_DIR/privkey.pem"   "$DEPLOY_DIR/nginx/certs/privkey.pem"

cat > "$DEPLOY_DIR/nginx/nginx.conf" <<EOF
upstream backend {
    server backend:8000;
}

# HTTP → HTTPS 重定向
server {
    listen 80;
    server_name ${DOMAIN};
    return 301 https://\$host\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name ${DOMAIN};

    ssl_certificate     /etc/nginx/certs/fullchain.pem;
    ssl_certificate_key /etc/nginx/certs/privkey.pem;
    ssl_protocols       TLSv1.2 TLSv1.3;
    ssl_ciphers         HIGH:!aNULL:!MD5;
    ssl_session_cache   shared:SSL:10m;

    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript
               application/javascript application/json application/xml
               image/svg+xml font/woff2;

    location /uploads/ {
        alias /var/www/uploads/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location /api/ {
        proxy_pass http://backend;
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto https;
        client_max_body_size 15M;
        proxy_read_timeout 60s;
    }

    location /health {
        proxy_pass http://backend;
        proxy_set_header Host \$host;
    }

    location / {
        root /usr/share/nginx/html;
        index index.html;
        try_files \$uri \$uri/ /index.html;

        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }
}
EOF

# ─── 3. 更新 docker-compose.yml 挂载证书目录 ─────────────────────────────────
info "更新 docker-compose.yml 挂载 HTTPS 证书..."
# 追加证书 volume 挂载到 nginx 服务（使用 sed 插入）
if ! grep -q "nginx/certs" "$DEPLOY_DIR/docker-compose.yml"; then
    sed -i '/volumes:\s*$/,/networks:/{
        /- backend_uploads/a\      - ./nginx/certs:/etc/nginx/certs:ro
    }' "$DEPLOY_DIR/docker-compose.yml"
fi

# ─── 4. 重新构建并启动 ────────────────────────────────────────────────────────
info "重新构建 Nginx 镜像..."
docker compose build nginx
docker compose up -d

# ─── 5. 配置证书自动续期 ──────────────────────────────────────────────────────
info "配置证书自动续期（cron）..."
RENEW_CMD="certbot renew --quiet --pre-hook 'docker compose -f ${DEPLOY_DIR}/docker-compose.yml stop nginx' --post-hook 'docker compose -f ${DEPLOY_DIR}/docker-compose.yml start nginx'"
(crontab -l 2>/dev/null | grep -v certbot; echo "0 3 * * * $RENEW_CMD") | crontab -
info "自动续期已配置（每天凌晨 3 点检查）"

echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}  ✅  HTTPS 配置完成！${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "  🔒 访问地址：https://${DOMAIN}"
echo ""
