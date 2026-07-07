# MonoReg

MonoReg 是一个轻量化竞赛 / 大型活动报名系统，面向程序设计竞赛、训练营、考试、讲座和大型活动。系统支持动态报名表、报名数据管理、账号批量生成 / 导入、邮件模板、批量邮件任务、发送日志、失败重试和 CSV / Excel 导出。

## 功能列表

- 管理员登录、JWT 鉴权、super_admin/admin/viewer 角色预留
- 活动 CRUD、发布、关闭、复制
- 动态报名表配置与公开报名页面
- 报名列表、详情、搜索、筛选、分页、批量状态修改
- 报名数据 CSV / Excel 导出，报名导入接口
- 账号批量生成、随机密码、安全加密保存、导入、重置密码
- 邮件模板 CRUD、变量预览、测试发送
- Redis Queue 批量邮件任务、邮件日志、失败重试
- Docker Compose 一键部署

## 技术栈

- Backend: Python 3.12, FastAPI, SQLAlchemy 2.x, Alembic, PostgreSQL, Redis, RQ
- Frontend: Vue 3, Vite, TypeScript, Pinia, Vue Router, Axios, Element Plus
- Import/Export: openpyxl, CSV
- Security: bcrypt, JWT, Fernet encryption

## 本地开发

后端：

```bash
cd monoreg/backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp ../.env.example ../.env
alembic upgrade head
python -m app.scripts.create_admin
uvicorn app.main:app --reload
```

前端：

```bash
cd monoreg/frontend
npm install
npm run dev
```

## Docker 部署

```bash
cd monoreg
cp .env.example .env
docker compose up --build
```

访问：

- Frontend: <http://localhost:5173>
- Backend API docs: <http://localhost:5173/docs>
- Health: <http://localhost:5173/api/health>

默认 Docker 部署只向宿主机暴露前端端口。Backend、PostgreSQL 和 Redis 仅在 Compose 内部网络访问，避免数据库、队列和后台接口被直接暴露。若本机调试需要直连服务，请使用本地开发命令启动后端，或创建临时 `docker-compose.override.yml` 映射所需端口，调试结束后移除。

## 环境变量说明

核心变量在 `.env.example` 中。生产部署必须修改：

- `SECRET_KEY`
- `PASSWORD_ENCRYPTION_KEY`
- `DATABASE_URL`
- `REDIS_URL`
- `SMTP_*`
- `INIT_ADMIN_*`

## 初始化管理员

Docker 启动时会自动执行：

```bash
python -m app.scripts.create_admin
```

默认账号来自环境变量，示例为 `admin / admin123456`。

## 常见问题

- 登录失败：确认已执行管理员初始化脚本。
- 邮件发送失败：确认 SMTP 主机、端口、账号、密码、SSL 配置正确，并查看邮件任务详情。
- 账号邮件缺少密码：确认账号由系统生成或导入成功，且 `PASSWORD_ENCRYPTION_KEY` 没有变更。
- 数据库连接失败：确认 PostgreSQL 已启动，`DATABASE_URL` 指向正确服务名。

## 项目结构

```text
monoreg/
├── backend/
├── frontend/
├── docs/
├── docker-compose.yml
├── .env.example
└── README.md
```

## 接口文档位置

- Swagger: `/docs`
- Markdown: `docs/API.md`
- Database: `docs/DATABASE.md`
- Deploy: `docs/DEPLOY.md`
- PRD: `docs/PRD.md`
