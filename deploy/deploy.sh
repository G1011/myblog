#!/bin/bash
# =============================================================================
# deploy.sh — 项目一键部署 / 更新脚本（在服务器上运行）
# 用法：
#   首次部署：bash deploy.sh
#   更新部署：bash deploy.sh --update
# =============================================================================
set -e

# ─── 可配置变量 ──────────────────────────────────────────────────────────────
REPO_URL="https://github.com/G1011/myblog.git"
DEPLOY_DIR="/opt/myblog"
BRANCH="main"
# ─────────────────────────────────────────────────────────────────────────────

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; BLUE='\033[0;34m'; NC='\033[0m'
info()    { echo -e "${GREEN}[INFO]${NC}  $1"; }
warn()    { echo -e "${YELLOW}[WARN]${NC}  $1"; }
error()   { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }
section() { echo -e "\n${BLUE}━━━ $1 ━━━${NC}"; }

UPDATE_MODE=false
[ "$1" = "--update" ] && UPDATE_MODE=true

# ─── 前置检查 ─────────────────────────────────────────────────────────────────
command -v docker  &>/dev/null || error "未检测到 Docker，请先运行 server-init.sh"
docker compose version &>/dev/null 2>&1 || error "未检测到 Docker Compose Plugin"

# ─── Step 1: 拉取代码 ─────────────────────────────────────────────────────────
section "Step 1 / 拉取代码"
if [ "$UPDATE_MODE" = true ]; then
    info "更新模式：拉取最新代码"
    cd "$DEPLOY_DIR"
    git fetch origin
    git reset --hard origin/$BRANCH
else
    if [ -d "$DEPLOY_DIR/.git" ]; then
        warn "目录 $DEPLOY_DIR 已存在，切换为更新模式"
        cd "$DEPLOY_DIR"
        git fetch origin
        git reset --hard origin/$BRANCH
    else
        info "克隆仓库到 $DEPLOY_DIR"
        git clone -b "$BRANCH" "$REPO_URL" "$DEPLOY_DIR"
        cd "$DEPLOY_DIR"
    fi
fi
info "当前版本：$(git log --oneline -1)"

# ─── Step 2: 配置环境变量 ──────────────────────────────────────────────────────
section "Step 2 / 配置环境变量"
cd "$DEPLOY_DIR"

if [ ! -f ".env" ]; then
    info "生成 .env 文件"

    # 生成随机 SECRET_KEY
    SECRET_KEY=$(openssl rand -hex 32)

    # 提示用户输入，提供默认值
    read -p "PostgreSQL 数据库名   [myblog]: "    PG_DB;      PG_DB=${PG_DB:-myblog}
    read -p "PostgreSQL 用户名     [myblog]: "    PG_USER;    PG_USER=${PG_USER:-myblog}
    read -p "PostgreSQL 密码       [随机生成]: "  PG_PASS
    [ -z "$PG_PASS" ] && PG_PASS=$(openssl rand -hex 16)

    read -p "管理员邮箱            [admin@example.com]: " ADMIN_EMAIL
    ADMIN_EMAIL=${ADMIN_EMAIL:-admin@example.com}
    read -p "管理员用户名          [admin]: "    ADMIN_USER; ADMIN_USER=${ADMIN_USER:-admin}
    read -s -p "管理员密码           [Admin@123456]: " ADMIN_PASS; echo
    ADMIN_PASS=${ADMIN_PASS:-Admin@123456}

    read -p "Nginx 监听端口        [80]: "       NGINX_PORT; NGINX_PORT=${NGINX_PORT:-80}

    cat > .env <<EOF
# PostgreSQL
POSTGRES_DB=${PG_DB}
POSTGRES_USER=${PG_USER}
POSTGRES_PASSWORD=${PG_PASS}

# Backend
SECRET_KEY=${SECRET_KEY}
FIRST_ADMIN_EMAIL=${ADMIN_EMAIL}
FIRST_ADMIN_USERNAME=${ADMIN_USER}
FIRST_ADMIN_PASSWORD=${ADMIN_PASS}

# Nginx
NGINX_PORT=${NGINX_PORT}
EOF
    info ".env 文件已生成"
    chmod 600 .env
else
    warn ".env 已存在，跳过（如需重置请手动删除后重新运行）"
fi

# ─── Step 3: 构建镜像 ─────────────────────────────────────────────────────────
section "Step 3 / 构建 Docker 镜像"
docker compose build --no-cache
info "镜像构建完成"

# ─── Step 4: 启动服务 ─────────────────────────────────────────────────────────
section "Step 4 / 启动服务"
if [ "$UPDATE_MODE" = true ]; then
    info "滚动更新：重启服务"
    docker compose up -d --remove-orphans
else
    docker compose up -d
fi

# ─── Step 5: 健康检查 ─────────────────────────────────────────────────────────
section "Step 5 / 健康检查"
info "等待服务启动（15s）..."
sleep 15

NGINX_PORT_VAL=$(grep NGINX_PORT .env | cut -d= -f2)
NGINX_PORT_VAL=${NGINX_PORT_VAL:-80}

if curl -sf "http://localhost:${NGINX_PORT_VAL}/health" | grep -q "healthy"; then
    info "✅ 服务健康检查通过"
else
    warn "健康检查未通过，查看日志："
    docker compose logs --tail=30
fi

# ─── Step 6: 设置开机自启 ────────────────────────────────────────────────────
section "Step 6 / 设置开机自启"
cat > /etc/systemd/system/myblog.service <<EOF
[Unit]
Description=MyBlog Docker Compose
Requires=docker.service
After=docker.service network-online.target

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=${DEPLOY_DIR}
ExecStart=/usr/bin/docker compose up -d
ExecStop=/usr/bin/docker compose down
TimeoutStartSec=300

[Install]
WantedBy=multi-user.target
EOF
systemctl daemon-reload
systemctl enable myblog
info "开机自启已配置"

# ─── 完成 ─────────────────────────────────────────────────────────────────────
SERVER_IP=$(curl -sf http://icanhazip.com 2>/dev/null || echo "<your-server-ip>")

echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}  ✅  部署完成！${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "  🌐 访问地址：  ${BLUE}http://${SERVER_IP}${NC}"
echo -e "  📖 API 文档：  ${BLUE}http://${SERVER_IP}/api/docs${NC}"
echo -e "  🔧 管理后台：  ${BLUE}http://${SERVER_IP}/admin/login${NC}"
echo ""
echo -e "  常用命令："
echo -e "    查看日志：  docker compose -f ${DEPLOY_DIR}/docker-compose.yml logs -f"
echo -e "    停止服务：  docker compose -f ${DEPLOY_DIR}/docker-compose.yml down"
echo -e "    更新部署：  bash ${DEPLOY_DIR}/deploy/deploy.sh --update"
echo ""
