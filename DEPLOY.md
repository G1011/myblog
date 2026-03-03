# 阿里云部署指南

本文档描述如何将 myblog 部署到阿里云 ECS，使用 Docker Compose 进行容器化部署。

---

## 目录

1. [架构概览](#1-架构概览)
2. [阿里云 ECS 准备](#2-阿里云-ecs-准备)
3. [安全组配置](#3-安全组配置)
4. [一键部署](#4-一键部署)
5. [手动部署步骤](#5-手动部署步骤)
6. [SSL / HTTPS 配置](#6-ssl--https-配置)
7. [域名配置](#7-域名配置)
8. [日常维护](#8-日常维护)
9. [备份与恢复](#9-备份与恢复)
10. [故障排除](#10-故障排除)

---

## 1. 架构概览

```
Internet
    │
    ▼
┌─────────────────────────────────┐
│  阿里云 ECS                      │
│                                  │
│  ┌──────────────────────────┐   │
│  │  Nginx (端口 80/443)      │   │
│  │  · 反向代理               │   │
│  │  · 提供 Vue 前端静态文件   │   │
│  │  · SSL 终止               │   │
│  └────────────┬─────────────┘   │
│               │ /api/*           │
│  ┌────────────▼─────────────┐   │
│  │  FastAPI Backend (8000)  │   │
│  │  · REST API              │   │
│  │  · JWT 认证              │   │
│  │  · 文件上传              │   │
│  └────────────┬─────────────┘   │
│               │                  │
│  ┌────────────▼─────────────┐   │
│  │  PostgreSQL 15           │   │
│  │  · 数据持久化             │   │
│  └──────────────────────────┘   │
│                                  │
└─────────────────────────────────┘
```

**Docker 网络隔离：**
- `internal` 网络：PostgreSQL、Backend、Nginx 内部通信
- `external` 网络：仅 Nginx 暴露至宿主机
- PostgreSQL 不对外暴露端口

---

## 2. 阿里云 ECS 准备

### 2.1 推荐规格

| 项目 | 推荐配置 |
|------|---------|
| 实例规格 | ecs.c6.large（2vCPU / 4GB）或更高 |
| 操作系统 | Ubuntu 22.04 LTS / Alibaba Cloud Linux 3 |
| 系统盘 | SSD 40GB 以上 |
| 数据盘（可选） | SSD 50GB（用于挂载 /data 存放 Docker 数据） |
| 带宽 | 按量付费 1-5 Mbps，或固定带宽 |
| 地域 | 根据目标用户选择最近地域 |

> **最低配置**：1vCPU / 2GB，但构建 Docker 镜像时可能内存不足，建议构建时临时增加 Swap。

### 2.2 操作系统初始化

SSH 登录服务器后执行：

```bash
# 更新系统（Ubuntu）
apt-get update && apt-get upgrade -y

# 设置时区
timedatectl set-timezone Asia/Shanghai

# 开启防火墙（如使用 ufw）
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw enable

# 创建项目用户（可选，避免使用 root）
adduser deploy
usermod -aG docker deploy
```

### 2.3 内存不足时添加 Swap

```bash
# 添加 2GB Swap（1GB 内存时推荐）
fallocate -l 2G /swapfile
chmod 600 /swapfile
mkswap /swapfile
swapon /swapfile
echo '/swapfile none swap sw 0 0' >> /etc/fstab
```

---

## 3. 安全组配置

在阿里云控制台 → ECS → 安全组 → 配置规则，添加以下**入方向**规则：

| 授权策略 | 协议 | 端口 | 来源 | 说明 |
|---------|------|------|------|------|
| 允许 | TCP | 22 | 你的 IP | SSH 管理（建议限制来源 IP） |
| 允许 | TCP | 80 | 0.0.0.0/0 | HTTP |
| 允许 | TCP | 443 | 0.0.0.0/0 | HTTPS（启用 SSL 时） |

> **安全提示**：SSH 端口建议修改为非标准端口，并仅允许特定 IP 访问。

---

## 4. 一键部署

### 4.1 上传项目到服务器

**方式一：通过 Git（推荐）**

```bash
# 在服务器上克隆项目
git clone https://github.com/your-username/myblog.git /opt/myblog
cd /opt/myblog
```

**方式二：通过 scp 上传本地项目**

```bash
# 在本地执行
scp -r /Users/pgg/Tool/claude_code/myblog root@<服务器IP>:/opt/myblog
```

**方式三：通过 rsync（增量同步）**

```bash
# 在本地执行（之后更新也可用这个命令）
rsync -avz --exclude='.git' --exclude='node_modules' --exclude='__pycache__' \
    /Users/pgg/Tool/claude_code/myblog/ root@<服务器IP>:/opt/myblog/
```

### 4.2 执行一键部署脚本

```bash
cd /opt/myblog

# 赋予执行权限
chmod +x deploy.sh

# 执行部署
sudo ./deploy.sh
```

脚本将自动完成：
1. 检测并安装 Docker、Docker Compose
2. 交互式配置域名、管理员账号、密码
3. 生成安全随机密钥
4. 创建生产环境 `.env` 文件
5. 启动所有服务
6. （可选）自动申请 Let's Encrypt SSL 证书

---

## 5. 手动部署步骤

如需手动控制每个步骤：

### 5.1 安装 Docker

```bash
# Ubuntu / Debian
apt-get update
apt-get install -y curl
curl -fsSL https://get.docker.com | sh
systemctl enable docker && systemctl start docker

# Alibaba Cloud Linux / CentOS
yum install -y yum-utils
yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
yum install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
systemctl enable docker && systemctl start docker
```

### 5.2 配置环境变量

```bash
cd /opt/myblog

# 复制模板
cp .env.example .env

# 编辑配置
vi .env
```

`.env` 生产配置示例：

```env
# PostgreSQL
POSTGRES_DB=myblog
POSTGRES_USER=myblog
POSTGRES_PASSWORD=<强随机密码，至少32位>

# Backend
SECRET_KEY=<随机32位十六进制字符串>
FIRST_ADMIN_EMAIL=your-email@example.com
FIRST_ADMIN_USERNAME=admin
FIRST_ADMIN_PASSWORD=<强密码，包含大小写字母数字特殊字符>

# Nginx
NGINX_PORT=80
```

生成随机密钥：
```bash
# 生成 SECRET_KEY
openssl rand -hex 32

# 生成数据库密码
openssl rand -base64 32 | tr -d '=+/'
```

### 5.3 配置 CORS（跨域）

由于 `docker-compose.yml` 中 CORS 地址为硬编码，需创建 override 文件：

```bash
# 将 example.com 替换为你的实际域名或服务器 IP
cat > docker-compose.override.yml << 'EOF'
services:
  backend:
    environment:
      CORS_ORIGINS: '["https://example.com", "http://example.com"]'
EOF
```

### 5.4 构建并启动

```bash
# 首次启动（构建镜像）
docker compose up -d --build

# 查看启动日志
docker compose logs -f

# 查看服务状态
docker compose ps
```

### 5.5 验证部署

```bash
# 检查所有服务是否正常
docker compose ps

# 测试健康检查
curl http://localhost/health

# 测试 API
curl http://localhost/api/v1/articles/
```

---

## 6. SSL / HTTPS 配置

> **前提**：已有域名并完成 DNS 解析（A 记录指向服务器 IP），且服务器 80 端口可访问。

### 6.1 deploy.sh 自动配置（推荐）

在运行 `deploy.sh` 时，输入域名后选择 `y` 即可自动完成 SSL 配置。

### 6.2 手动配置 Let's Encrypt

```bash
# 安装 certbot（Ubuntu）
apt-get install -y certbot

# 停止 nginx（释放 80 端口）
docker compose stop nginx

# 申请证书（standalone 模式）
certbot certonly --standalone \
    --non-interactive --agree-tos \
    -m your-email@example.com \
    -d example.com

# 证书保存位置
ls /etc/letsencrypt/live/example.com/
```

### 6.3 配置 Nginx SSL

创建 SSL nginx 配置文件：

```bash
cat > nginx/nginx.ssl.conf << 'NGINXEOF'
upstream backend {
    server backend:8000;
}

# HTTP → HTTPS 重定向
server {
    listen 80;
    server_name example.com;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name example.com;

    ssl_certificate /etc/letsencrypt/live/example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/example.com/privkey.pem;
    ssl_session_timeout 1d;
    ssl_session_cache shared:MozSSL:10m;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    add_header Strict-Transport-Security "max-age=63072000" always;

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
```

创建 SSL compose override：

```bash
cat > docker-compose.ssl.yml << 'EOF'
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
```

启动（含 SSL）：

```bash
docker compose -f docker-compose.yml -f docker-compose.ssl.yml up -d --build
```

### 6.4 证书自动续期

```bash
# 添加 cron 任务（每天中午检查续期）
cat > /etc/cron.d/certbot-myblog << 'EOF'
0 12 * * * root certbot renew --quiet \
    --pre-hook "cd /opt/myblog && docker compose stop nginx" \
    --post-hook "cd /opt/myblog && docker compose -f docker-compose.yml -f docker-compose.ssl.yml up -d nginx"
EOF
```

---

## 7. 域名配置

### 7.1 DNS 解析

在域名注册商（阿里云万网/DNSPod 等）添加：

| 记录类型 | 主机记录 | 记录值 |
|---------|---------|--------|
| A | @ | `<服务器公网 IP>` |
| A | www | `<服务器公网 IP>` |

### 7.2 验证 DNS 解析

```bash
# 在服务器上验证
ping example.com
nslookup example.com
```

---

## 8. 日常维护

### 查看服务状态

```bash
cd /opt/myblog

# 查看所有容器状态
docker compose ps

# 查看实时日志
docker compose logs -f

# 查看特定服务日志
docker compose logs -f backend
docker compose logs -f nginx
docker compose logs -f postgres
```

### 更新部署

```bash
cd /opt/myblog

# 拉取最新代码（如使用 Git）
git pull

# 重新构建并重启
docker compose up -d --build

# 或仅重启特定服务（不重建）
docker compose restart backend
```

### 停止 / 启动服务

```bash
# 停止所有服务（保留数据卷）
docker compose down

# 启动所有服务
docker compose up -d

# 完全清理（⚠️ 会删除数据库数据）
docker compose down -v
```

### 查看资源占用

```bash
# Docker 容器资源占用
docker stats

# 磁盘使用
docker system df
df -h
```

### 清理 Docker 缓存

```bash
# 清理无用镜像和构建缓存（不影响运行中容器）
docker system prune -f
```

---

## 9. 备份与恢复

### 9.1 备份数据库

```bash
# 备份 PostgreSQL 数据
docker compose exec postgres pg_dump \
    -U myblog myblog | gzip > /backup/myblog_$(date +%Y%m%d_%H%M%S).sql.gz

# 创建每日自动备份 cron
mkdir -p /backup/myblog
cat > /etc/cron.d/myblog-backup << 'EOF'
0 3 * * * root cd /opt/myblog && \
    docker compose exec -T postgres pg_dump -U myblog myblog | \
    gzip > /backup/myblog/db_$(date +\%Y\%m\%d).sql.gz && \
    find /backup/myblog -name "db_*.sql.gz" -mtime +30 -delete
EOF
```

### 9.2 恢复数据库

```bash
# 从备份恢复（⚠️ 会覆盖现有数据）
gunzip -c /backup/myblog/db_20240101.sql.gz | \
    docker compose exec -T postgres psql -U myblog myblog
```

### 9.3 备份上传文件

```bash
# 备份用户上传的文件
docker run --rm \
    -v myblog_backend_uploads:/uploads:ro \
    -v /backup/myblog:/backup \
    alpine tar czf /backup/uploads_$(date +%Y%m%d).tar.gz /uploads
```

### 9.4 恢复上传文件

```bash
docker run --rm \
    -v myblog_backend_uploads:/uploads \
    -v /backup/myblog:/backup \
    alpine tar xzf /backup/uploads_20240101.tar.gz -C /
```

---

## 10. 故障排除

### 容器启动失败

```bash
# 查看容器日志
docker compose logs backend
docker compose logs postgres

# 进入容器调试
docker compose exec backend sh
docker compose exec postgres psql -U myblog
```

### 数据库连接失败

```bash
# 检查 PostgreSQL 是否健康
docker compose exec postgres pg_isready -U myblog

# 检查环境变量
docker compose exec backend env | grep DATABASE_URL
```

### 502 Bad Gateway

说明 Nginx 无法连接 Backend：
```bash
# 检查 backend 是否运行
docker compose ps backend

# 检查 backend 日志
docker compose logs --tail=50 backend
```

### 端口已被占用

```bash
# 查看占用 80 端口的进程
lsof -i :80
# 或
ss -tlnp | grep :80
```

### 磁盘空间不足

```bash
# 查看磁盘使用
df -h

# 清理 Docker 资源
docker system prune -a -f

# 清理旧日志
find /var/lib/docker/containers -name "*.log" -exec truncate -s 0 {} \;
```

### 重置管理员密码

```bash
# 进入 backend 容器，通过 Python 重置密码
docker compose exec backend python3 -c "
import asyncio
from app.db.database import get_db
from app.repositories.user_repository import UserRepository
from app.core.security import get_password_hash

async def reset():
    async for db in get_db():
        repo = UserRepository(db)
        user = await repo.get_by_email('admin@example.com')
        user.hashed_password = get_password_hash('NewPassword@123')
        await db.commit()
        print('Password reset successfully')
        break

asyncio.run(reset())
"
```

---

## 附：部署检查清单

部署完成后，逐项验证：

- [ ] `docker compose ps` 所有服务状态为 `Up`
- [ ] 访问 `http://<域名或IP>` 可以看到博客首页
- [ ] 访问 `http://<域名或IP>/api/v1/articles/` 返回 JSON
- [ ] 使用管理员账号登录后台
- [ ] 创建一篇测试文章
- [ ] 上传图片功能正常
- [ ] （若配置 SSL）`https://` 可正常访问
- [ ] （若配置 SSL）`http://` 自动跳转到 `https://`
- [ ] 数据库备份脚本已配置
- [ ] 证书自动续期已配置
