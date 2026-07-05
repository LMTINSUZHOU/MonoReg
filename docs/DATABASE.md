# Database

数据库使用 PostgreSQL。迁移文件位于 `backend/alembic/versions/0001_initial.py`。

## 表说明

### `admin_users`

管理员表。字段：`username`, `email`, `password_hash`, `role`, `status`, `last_login_at`。索引：`username`, `email` 唯一。

### `activities`

活动表。字段包含标题、slug、描述、状态、报名时间、人数上限、账号和邮件策略、登录地址、创建人。索引：`slug` 唯一、`status`。

状态枚举：`draft`, `open`, `paused`, `closed`, `archived`。

### `form_fields`

动态表单字段表。每个活动拥有多条字段配置。唯一约束：`activity_id + field_key`。字段类型：`text`, `textarea`, `email`, `phone`, `number`, `select`, `multi_select`, `radio`, `checkbox`, `date`。

### `registrations`

报名记录表。核心字段 `name`, `email`, `phone` 单独存储，其他动态字段存储在 `form_data` JSONB。唯一约束：`activity_id + email`。索引：`activity_id`, `email`, `status`, `form_data` GIN。

状态枚举：`pending`, `approved`, `rejected`, `cancelled`, `account_pending`, `account_ready`, `account_sent`, `mail_failed`。

### `accounts`

账号表。密码存储在 `password_encrypted`，不可明文保存。唯一约束：`activity_id + username`、`registration_id`。状态：`pending`, `ready`, `sent`, `disabled`。

### `email_templates`

邮件模板表。支持活动级模板和类型字段。类型：`registration_confirm`, `account_info`, `approval_notice`, `rejection_notice`, `custom_notice`。

### `email_jobs`

批量邮件任务表。记录任务状态、总数、成功数、失败数、创建人和开始/结束时间。状态：`pending`, `running`, `completed`, `failed`, `cancelled`。

### `email_logs`

每封邮件日志。记录收件人、主题、正文快照、状态、错误、重试次数、发送时间。状态：`pending`, `sending`, `sent`, `failed`, `skipped`, `retrying`。

### `audit_logs`

后台操作审计日志。记录管理员、动作、资源、详情 JSON、IP 和时间。

## 关系说明

- `activities.created_by -> admin_users.id`
- `form_fields.activity_id -> activities.id`
- `registrations.activity_id -> activities.id`
- `accounts.registration_id -> registrations.id`
- `accounts.activity_id -> activities.id`
- `email_templates.activity_id -> activities.id`
- `email_jobs.template_id -> email_templates.id`
- `email_logs.job_id -> email_jobs.id`
- `email_logs.registration_id -> registrations.id`

## 索引说明

高频查询字段均建索引：活动状态、报名活动 ID、报名邮箱、报名状态、账号状态、邮件任务状态、邮件日志状态。`registrations.form_data` 使用 GIN 索引便于后续 JSONB 查询扩展。

