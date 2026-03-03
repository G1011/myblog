#!/bin/bash
# =============================================================================
# myblog 一键部署脚本 - 阿里云 ECS
# 支持系统：Ubuntu 20.04+、Alibaba Cloud Linux 2/3、CentOS 7/8
# 用法：sudo ./deploy.sh
# =============================================================================

set -euo pipefail

# ─────────────────────────────────────────────────────────────────────────────
# 颜色与日志
# ─────────────────────────────────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

log_info()  { echo -e "${GREEN}[INFO]${NC}  $*"; }
log_warn()  { echo -e "${YELLOW}[WARN]${NC}  $*"; }
log_error() { echo -e "${RED}[ERROR]${NC} $*"; }
log_step()  { echo -e "\n${BOLD}${BLUE}▶ $*${NC}"; }
log_done()  { echo -e "${GREEN}✔${NC}  $*"; }

# ─────────────────────────────────────────────────────────────────────────────
# 全局变量（由用户输入或自动生成）
# ─────────────────────────────────────────────────────────────────────────────
DOMAIN=""
ADMIN_EMAIL=""
ADMIN_USERNAME=""
ADMIN_PASSWORD=""
POSTGRES_PASSWORD=""
SECRET_KEY=""
SETUP_SSL=false
OS_TYPE=""          # ubuntu | centos | alibaba
PKG_MANAGER=""      # apt | yum | dnf
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# ─────────────────────────────────────────────────────────────────────────────
# 横幅
# ─────────────────────────────────────────────────────────────────────────────
print_banner() {
    echo -e "${CYAN}"
    echo "╔══════════════════════════════════════════════════════╗"
    echo "║          myblog 阿里云一键部署脚本                   ║"
    echo "║          Docker Compose · FastAPI · Vue3             ║"
    echo "╚══════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

# ─────────────────────────────────────────────────────────────────────────────
# 环境检查
# ─────────────────────────────────────────────────────────────────────────────
check_root() {
    if [[ $EUID -ne 0 ]]; then
        log_error "请使用 root 或 sudo 运行此脚本"
        log_error "示例: sudo ./deploy.sh"
        exit 1
    fi
}

check_project_dir() {
    if [[ ! -f "$PROJECT_DIR/docker-compose.yml" ]]; then
        log_error "未找到 docker-compose.yml，请在项目根目录运行此脚本"
        exit 1
    fi
    log_info "项目目录: $PROJECT_DIR"
    cd "$PROJECT_DIR"
}

detect_os() {
    log_step "检测操作系统"
    if [[ -f /etc/os-release ]]; then
        # shellcheck disable=SC1091
        source /etc/os-release
        local os_name="${NAME:-unknown}"

        if [[ "$os_name" == *"Ubuntu"* ]] || [[ "$os_name" == *"Debian"* ]]; then
            OS_TYPE="ubuntu"
            PKG_MANAGER="apt"
        elif [[ "$os_name" == *"Alibaba Cloud Linux"* ]] || [[ "$os_name" == *"Aliyun"* ]]; then
            # Alibaba Cloud Linux 3 (RHEL8-based) 用 dnf，2 用 yum
            OS_TYPE="alibaba"
            if command -v dnf &>/dev/null; then
                PKG_MANAGER="dnf"
            else
                PKG_MANAGER="yum"
            fi
        elif [[ "$os_name" == *"CentOS"* ]] || [[ "$os_name" == *"Red Hat"* ]]; then
            OS_TYPE="centos"
            if command -v dnf &>/dev/null; then
                PKG_MANAGER="dnf"
            else
                PKG_MANAGER="yum"
            fi
        else
            log_warn "未识别的系统: $os_name，尝试使用 apt"
            OS_TYPE="ubuntu"
            PKG_MANAGER="apt"
        fi
        log_done "系统: $os_name | 包管理器: $PKG_MANAGER"
    else
        log_error "无法读取 /etc/os-release，无法检测操作系统"
        exit 1
    fi
}

# ─────────────────────────────────────────────────────────────────────────────
# 安装依赖
# ─────────────────────────────────────────────────────────────────────────────
install_base_deps() {
    log_step "安装基础依赖 (git, curl, openssl)"
    if [[ "$PKG_MANAGER" == "apt" ]]; then
        apt-get update -qq
        apt-get install -y -qq git curl openssl ca-certificates gnupg lsb-release
    else
        $PKG_MANAGER install -y -q git curl openssl
    fi
    log_done "基础依赖安装完成"
}

install_docker() {
    log_step "检查并安装 Docker"
    if command -v docker &>/dev/null; then
        log_done "Docker 已安装: $(docker --version)"
        return
    fi

    log_info "安装 Docker..."
    if [[ "$PKG_MANAGER" == "apt" ]]; then
        install -m 0755 -d /etc/apt/keyrings
        curl -fsSL https://download.docker.com/linux/ubuntu/gpg \
            | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
        chmod a+r /etc/apt/keyrings/docker.gpg
        echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
            https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" \
            > /etc/apt/sources.list.d/docker.list
        apt-get update -qq
        apt-get install -y -qq docker-ce docker-ce-cli containerd.io docker-compose-plugin
    else
        # CentOS / Alibaba Cloud Linux
        $PKG_MANAGER install -y -q yum-utils 2>/dev/null || true
        yum-config-manager --add-repo \
            https://download.docker.com/linux/centos/docker-ce.repo 2>/dev/null || \
        $PKG_MANAGER config-manager --add-repo \
            https://download.docker.com/linux/centos/docker-ce.repo
        $PKG_MANAGER install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
    fi

    systemctl enable docker
    systemctl start docker
    log_done "Docker 安装完成: $(docker --version)"
}

install_docker_compose() {
    log_step "检查 Docker Compose"
    if docker compose version &>/dev/null; then
        log_done "Docker Compose 已可用: $(docker compose version)"
        return
    fi

    # 尝试安装 plugin（适用于旧版 apt 安装方式）
    log_info "安装 Docker Compose plugin..."
    if [[ "$PKG_MANAGER" == "apt" ]]; then
        apt-get install -y -qq docker-compose-plugin
    else
        # 手动安装 compose plugin
        local compose_version="2.27.0"
        local plugin_dir="/usr/local/lib/docker/cli-plugins"
        mkdir -p "$plugin_dir"
        curl -SL "https://github.com/docker/compose/releases/download/v${compose_version}/docker-compose-linux-$(uname -m)" \
            -o "$plugin_dir/docker-compose"
        chmod +x "$plugin_dir/docker-compose"
    fi
    log_done "Docker Compose 安装完成: $(docker compose version)"
}

install_certbot() {
    if command -v certbot &>/dev/null; then
        log_done "certbot 已安装"
        return
    fi
    log_info "安装 certbot..."
    if [[ "$PKG_MANAGER" == "apt" ]]; then
        apt-get install -y -qq certbot
    else
        $PKG_MANAGER install -y certbot || \
            $PKG_MANAGER install -y python3-certbot
    fi
    log_done "certbot 安装完成"
}

# ─────────────────────────────────────────────────────────────────────────────
# 交互式配置
# ─────────────────────────────────────────────────────────────────────────────
configure_interactively() {
    log_step "配置部署参数"

    # 域名
    echo ""
    read -rp "  域名（例: example.com）留空则使用服务器 IP: " DOMAIN

    # 管理员邮箱
    read -rp "  管理员邮箱 [admin@example.com]: " ADMIN_EMAIL
    ADMIN_EMAIL="${ADMIN_EMAIL:-admin@example.com}"

    # 管理员用户名
    read -rp "  管理员用户名 [admin]: " ADMIN_USERNAME
    ADMIN_USERNAME="${ADMIN_USERNAME:-admin}"

    # 管理员密码
    echo -n "  管理员密码（留空自动生成）: "
    read -rs ADMIN_PASSWORD
    echo ""
    if [[ -z "$ADMIN_PASSWORD" ]]; then
        ADMIN_PASSWORD="$(openssl rand -base64 12 | tr -d '=+/')@Aa1"
        log_info "自动生成管理员密码: ${YELLOW}${ADMIN_PASSWORD}${NC}（请记录！）"
    fi

    # SSL
    if [[ -n "$DOMAIN" ]]; then
        echo -n "  为 $DOMAIN 申请 Let's Encrypt SSL 证书？(y/n) [y]: "
        read -r ssl_choice
        ssl_choice="${ssl_choice:-y}"
        [[ "$ssl_choice" == "y" ]] && SETUP_SSL=true
    fi

    # 生成安全随机值
    POSTGRES_PASSWORD="$(openssl rand -base64 32 | tr -d '=+/')"
    SECRET_KEY="$(openssl rand -hex 32)"
}

# ─────────────────────────────────────────────────────────────────────────────
# 写入配置文件
# ─────────────────────────────────────────────────────────────────────────────
write_env_file() {
    log_step "生成 .env 文件"

    cat > "$PROJECT_DIR/.env" << EOF
# PostgreSQL
POSTGRES_DB=myblog
POSTGRES_USER=myblog
POSTGRES_PASSWORD=${POSTGRES_PASSWORD}

# Backend
SECRET_KEY=${SECRET_KEY}
FIRST_ADMIN_EMAIL=${ADMIN_EMAIL}
FIRST_ADMIN_USERNAME=${ADMIN_USERNAME}
FIRST_ADMIN_PASSWORD=${ADMIN_PASSWORD}

# Nginx
NGINX_PORT=80
EOF

    chmod 600 "$PROJECT_DIR/.env"
    log_done ".env 已生成（权限 600）"
}

write_cors_override() {
    log_step "配置 CORS 跨域设置"

    local cors_origins
    if [[ -n "$DOMAIN" ]]; then
        if [[ "$SETUP_SSL" == true ]]; then
            cors_origins="[\"https://${DOMAIN}\", \"http://${DOMAIN}\"]"
        else
            cors_origins="[\"http://${DOMAIN}\"]"
        fi
    else
        local server_ip
        server_ip="$(curl -s --max-time 5 ifconfig.me 2>/dev/null \
            || hostname -I | awk '{print $1}')"
        cors_origins="[\"http://${server_ip}\"]"
        log_info "服务器 IP: $server_ip"
    fi

    cat > "$PROJECT_DIR/docker-compose.override.yml" << EOF
# 自动生成 - 生产环境 CORS 配置
services:
  backend:
    environment:
      CORS_ORIGINS: '${cors_origins}'
EOF

    log_done "CORS 配置: $cors_origins"
}

# ─────────────────────────────────────────────────────────────────────────────
# SSL 相关
# ─────────────────────────────────────────────────────────────────────────────
obtain_ssl_cert() {
    local domain="$1"
    log_step "申请 Let's Encrypt SSL 证书"

    # 如果 nginx 在运行，先停止以释放 80 端口
    if docker compose ps nginx 2>/dev/null | grep -q "Up"; then
        log_info "临时停止 nginx 以释放 80 端口..."
        docker compose stop nginx
    fi

    certbot certonly \
        --standalone \
        --non-interactive \
        --agree-tos \
        --email "$ADMIN_EMAIL" \
        -d "$domain"

    log_done "SSL 证书申请成功: /etc/letsencrypt/live/$domain/"
}

write_ssl_nginx_conf() {
    local domain="$1"
    log_info "生成 SSL nginx 配置..."

    # 使用 cat + 转义，避免 $变量被 shell 展开
    cat > "$PROJECT_DIR/nginx/nginx.ssl.conf" << 'NGINXEOF'
upstream backend {
    server backend:8000;
}

# HTTP → HTTPS 重定向
server {
    listen 80;
    server_name DOMAIN_PLACEHOLDER;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name DOMAIN_PLACEHOLDER;

    ssl_certificate /etc/letsencrypt/live/DOMAIN_PLACEHOLDER/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/DOMAIN_PLACEHOLDER/privkey.pem;
    ssl_session_timeout 1d;
    ssl_session_cache shared:MozSSL:10m;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    add_header Strict-Transport-Security "max-age=63072000" always;
    add_header X-Content-Type-Options nosniff always;
    add_header X-Frame-Options DENY always;

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
        add_header X-Content-Type-Options nosniff;
    }

    location /api/ {
        proxy_pass http://backend;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        client_max_body_size 15M;
        proxy_read_timeout 60s;
    }

    location /health {
        proxy_pass http://backend;
        proxy_set_header Host $host;
    }

    location / {
        root /usr/share/nginx/html;
        index index.html;
        try_files $uri $uri/ /index.html;

        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }
}
NGINXEOF

    # 将占位符替换为真实域名
    sed -i "s/DOMAIN_PLACEHOLDER/${domain}/g" "$PROJECT_DIR/nginx/nginx.ssl.conf"
    log_done "nginx SSL 配置已生成: nginx/nginx.ssl.conf"
}

write_ssl_compose_override() {
    log_info "生成 SSL compose override..."
    cat > "$PROJECT_DIR/docker-compose.ssl.yml" << EOF
# 自动生成 - SSL 端口与证书挂载
services:
  nginx:
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - backend_uploads:/var/www/uploads:ro
      - /etc/letsencrypt:/etc/letsencrypt:ro
      - ./nginx/nginx.ssl.conf:/etc/nginx/conf.d/default.conf:ro
EOF
    log_done "docker-compose.ssl.yml 已生成"
}

setup_certbot_renew_cron() {
    local domain="$1"
    log_info "配置 SSL 证书自动续期..."
    cat > /etc/cron.d/myblog-certbot-renew << EOF
# myblog SSL 证书自动续期（每天 12:00 检查）
0 12 * * * root certbot renew --quiet \\
    --pre-hook "cd ${PROJECT_DIR} && docker compose stop nginx" \\
    --post-hook "cd ${PROJECT_DIR} && docker compose -f docker-compose.yml -f docker-compose.ssl.yml up -d nginx"
EOF
    log_done "自动续期 cron 已配置: /etc/cron.d/myblog-certbot-renew"
}

setup_db_backup_cron() {
    log_step "配置数据库自动备份"
    mkdir -p /backup/myblog

    cat > /etc/cron.d/myblog-backup << EOF
# myblog 数据库每日备份（凌晨 3:00）
0 3 * * * root cd ${PROJECT_DIR} && \\
    docker compose exec -T postgres pg_dump -U myblog myblog | \\
    gzip > /backup/myblog/db_\$(date +\\%Y\\%m\\%d).sql.gz && \\
    find /backup/myblog -name "db_*.sql.gz" -mtime +30 -delete
EOF
    log_done "数据库备份 cron 已配置（保留最近 30 天）"
}

# ─────────────────────────────────────────────────────────────────────────────
# 启动服务
# ─────────────────────────────────────────────────────────────────────────────
deploy_services() {
    local use_ssl="$1"
    log_step "构建并启动 Docker 服务"

    log_info "拉取基础镜像..."
    docker compose pull postgres 2>/dev/null || true

    log_info "构建应用镜像（首次较慢，约 3-10 分钟）..."
    if [[ "$use_ssl" == "true" ]]; then
        docker compose \
            -f docker-compose.yml \
            -f docker-compose.ssl.yml \
            up -d --build
    else
        docker compose up -d --build
    fi
    log_done "Docker 服务已启动"
}

wait_for_healthy() {
    log_step "等待服务就绪"
    local max_retries=36   # 最多等 3 分钟
    local retry=0
    local check_url="http://localhost/health"

    log_info "轮询健康检查（最多等待 3 分钟）..."
    while [[ $retry -lt $max_retries ]]; do
        if curl -sf "$check_url" &>/dev/null; then
            log_done "服务健康检查通过！"
            return 0
        fi
        retry=$((retry + 1))
        echo -ne "  等待中... ($retry/$max_retries)\r"
        sleep 5
    done

    echo ""
    log_error "服务在 3 分钟内未就绪，请检查日志:"
    log_error "  docker compose logs --tail=50 backend"
    log_error "  docker compose logs --tail=50 postgres"
    exit 1
}

# ─────────────────────────────────────────────────────────────────────────────
# 部署摘要
# ─────────────────────────────────────────────────────────────────────────────
print_summary() {
    local use_ssl="$1"
    local access_url

    if [[ -n "$DOMAIN" ]]; then
        if [[ "$use_ssl" == "true" ]]; then
            access_url="https://${DOMAIN}"
        else
            access_url="http://${DOMAIN}"
        fi
    else
        local server_ip
        server_ip="$(curl -s --max-time 5 ifconfig.me 2>/dev/null \
            || hostname -I | awk '{print $1}')"
        access_url="http://${server_ip}"
    fi

    echo ""
    echo -e "${BOLD}${GREEN}╔══════════════════════════════════════════════════════╗${NC}"
    echo -e "${BOLD}${GREEN}║              🎉 部署成功！                           ║${NC}"
    echo -e "${BOLD}${GREEN}╚══════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "  ${BOLD}访问地址${NC}     $access_url"
    echo -e "  ${BOLD}管理后台${NC}     ${access_url}/admin"
    echo -e "  ${BOLD}管理员邮箱${NC}   $ADMIN_EMAIL"
    echo -e "  ${BOLD}管理员密码${NC}   ${YELLOW}${ADMIN_PASSWORD}${NC}"
    echo ""
    echo -e "  ${BOLD}常用命令：${NC}"
    echo    "    查看日志     docker compose logs -f"
    echo    "    查看状态     docker compose ps"
    echo    "    停止服务     docker compose down"
    if [[ "$use_ssl" == "true" ]]; then
        echo "    重启服务     docker compose -f docker-compose.yml -f docker-compose.ssl.yml up -d"
    else
        echo "    重启服务     docker compose up -d"
    fi
    echo    "    更新部署     git pull && docker compose up -d --build"
    echo ""
    echo -e "  ${BOLD}备份目录：${NC}   /backup/myblog/"
    echo ""
    echo -e "${YELLOW}  ⚠️  请妥善保管管理员密码，它不会再次显示！${NC}"
    echo ""
}

# ─────────────────────────────────────────────────────────────────────────────
# 主流程
# ─────────────────────────────────────────────────────────────────────────────
main() {
    print_banner
    check_root
    check_project_dir

    # ── 1. 系统检测与依赖安装
    detect_os
    install_base_deps
    install_docker
    install_docker_compose

    # ── 2. 交互配置
    configure_interactively

    # ── 3. 写入配置文件
    write_env_file
    write_cors_override

    # ── 4. SSL 准备
    local use_ssl_flag=false
    if [[ "$SETUP_SSL" == "true" ]]; then
        install_certbot
        obtain_ssl_cert "$DOMAIN"
        write_ssl_nginx_conf "$DOMAIN"
        write_ssl_compose_override
        setup_certbot_renew_cron "$DOMAIN"
        use_ssl_flag=true
    fi

    # ── 5. 启动服务
    deploy_services "$use_ssl_flag"

    # ── 6. 健康检查
    wait_for_healthy

    # ── 7. 备份 cron
    setup_db_backup_cron

    # ── 8. 摘要
    print_summary "$use_ssl_flag"
}

main "$@"
