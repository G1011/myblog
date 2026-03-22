#!/bin/bash
# =============================================================================
# server-init.sh — 服务器首次初始化脚本（仅需执行一次）
# 适用系统：Ubuntu 22.04 / 20.04
# 用法：bash server-init.sh
# =============================================================================
set -e

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; NC='\033[0m'
info()  { echo -e "${GREEN}[INFO]${NC}  $1"; }
warn()  { echo -e "${YELLOW}[WARN]${NC}  $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }

[ "$(id -u)" -eq 0 ] || error "请以 root 用户运行此脚本（sudo bash server-init.sh）"

info "===== 1. 更新系统软件包 ====="
apt-get update -y && apt-get upgrade -y

info "===== 2. 安装基础工具 ====="
apt-get install -y curl git vim ufw fail2ban unzip

info "===== 3. 安装 Docker ====="
if command -v docker &>/dev/null; then
    warn "Docker 已安装，跳过"
else
    curl -fsSL https://get.docker.com | bash
    systemctl enable docker
    systemctl start docker
    info "Docker 安装完成：$(docker --version)"
fi

info "===== 4. 安装 Docker Compose Plugin ====="
if docker compose version &>/dev/null 2>&1; then
    warn "Docker Compose 已安装，跳过"
else
    apt-get install -y docker-compose-plugin
    info "Docker Compose 安装完成：$(docker compose version)"
fi

info "===== 5. 配置防火墙 ====="
ufw --force reset
ufw default deny incoming
ufw default allow outgoing
ufw allow 22/tcp    # SSH
ufw allow 80/tcp    # HTTP
ufw allow 443/tcp   # HTTPS
ufw --force enable
info "防火墙已配置（开放 22/80/443）"

info "===== 6. 优化系统参数 ====="
cat >> /etc/sysctl.conf <<'EOF'
# TCP 优化
net.core.somaxconn = 65535
net.ipv4.tcp_max_syn_backlog = 65535
net.ipv4.ip_local_port_range = 1024 65535
EOF
sysctl -p

info "===== 7. 安装 Certbot（用于 HTTPS）====="
apt-get install -y certbot

info "===== 初始化完成 ====="
echo ""
echo -e "${GREEN}下一步：运行 deploy.sh 部署项目${NC}"
echo "  bash /opt/myblog/deploy/deploy.sh"
