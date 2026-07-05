# Deploy

## Docker Compose 部署

```bash
cd monoreg
cp .env.example .env
docker compose up --build
```

服务：

- `postgres`: PostgreSQL 16
- `redis`: Redis 7
- `backend`: FastAPI
- `worker`: RQ 邮件 worker
- `frontend`: Nginx 托管 Vue 静态文件

## 环境变量配置

生产环境必须修改：

- `SECRET_KEY`: JWT 签名密钥
- `PASSWORD_ENCRYPTION_KEY`: 账号密码加密密钥，部署后不要变更
- `DATABASE_URL`: PostgreSQL 连接
- `REDIS_URL`: Redis 连接
- `SMTP_HOST`, `SMTP_PORT`, `SMTP_USERNAME`, `SMTP_PASSWORD`, `SMTP_FROM_EMAIL`
- `BACKEND_CORS_ORIGINS`

## SMTP 配置

SSL 端口通常为 465，STARTTLS 通常为 587。对应设置：

```env
SMTP_USE_SSL=true
SMTP_PORT=465
```

测试模板发送失败时，先查看后台邮件任务详情，再查看 worker 日志。

## 数据库迁移

Docker 启动时 backend 会执行：

```bash
alembic upgrade head
```

手动执行：

```bash
docker compose run --rm backend alembic upgrade head
```

## 初始化管理员

Docker 启动时 backend 会执行：

```bash
python -m app.scripts.create_admin
```

手动执行：

```bash
docker compose run --rm backend python -m app.scripts.create_admin
```

默认值来自：

```env
INIT_ADMIN_USERNAME=admin
INIT_ADMIN_EMAIL=admin@example.com
INIT_ADMIN_PASSWORD=admin123456
```

## 启动 Worker

Compose 中的 `worker` 服务命令：

```bash
python -m app.workers.email_worker
```

本地开发时需要 Redis 正常运行。

## 常见故障排查

- `database connection refused`: 检查 `DATABASE_URL` 的主机名。Compose 内应使用 `postgres`。
- `redis connection refused`: 检查 `REDIS_URL`，Compose 内应使用 `redis`。
- 邮件任务一直 pending: 检查 worker 是否启动，检查 Redis 队列是否可连接。
- 账号邮件变量为空: 确认已给报名记录生成或导入账号。
- 加密密码无法解密: `PASSWORD_ENCRYPTION_KEY` 必须与生成账号时一致。

