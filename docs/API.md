# API

统一响应：

```json
{ "success": true, "data": {}, "message": "ok" }
```

统一错误：

```json
{ "success": false, "message": "错误信息", "code": "ERROR_CODE", "details": {} }
```

后台接口均需要 `Authorization: Bearer <token>`，公开报名接口无需鉴权。

## Auth

### POST `/api/auth/login`

鉴权：否。

请求：

```json
{ "username": "admin", "password": "admin123456" }
```

响应：返回 `access_token` 和用户信息。错误：用户名或密码错误。

### GET `/api/auth/me`

鉴权：是。响应当前管理员信息。错误：token 无效或用户禁用。

## Activity

### GET `/api/admin/activities`

鉴权：是。参数：`page`, `page_size`, `keyword`, `status`。响应分页活动列表。

### POST `/api/admin/activities`

鉴权：是。请求活动字段：`title`, `slug`, `description`, `status`, `start_time`, `end_time`, `max_registrations`, `need_account`, `auto_generate_account`, `send_confirm_email`, `send_account_email_immediately`, `login_url`。错误：slug 重复。

### GET/PUT/DELETE `/api/admin/activities/{activity_id}`

鉴权：是。读取、更新、删除活动。错误：活动不存在。

### POST `/api/admin/activities/{activity_id}/publish`

鉴权：是。将活动状态改为 `open`。

### POST `/api/admin/activities/{activity_id}/close`

鉴权：是。将活动状态改为 `closed`。

### POST `/api/admin/activities/{activity_id}/duplicate`

鉴权：是。复制活动和表单字段，状态为 `draft`。

### GET `/api/public/activities/{slug}`

鉴权：否。返回公开活动信息和字段列表。`description` 支持保存 Markdown，报名页按富文本方式展示。错误：活动不存在。

## Form

### GET `/api/admin/activities/{activity_id}/form-fields`

鉴权：是。返回活动表单字段。

### PUT `/api/admin/activities/{activity_id}/form-fields`

鉴权：是。请求：

```json
{ "fields": [{ "field_key": "email", "field_label": "邮箱", "field_type": "email", "required": true }] }
```

错误：字段类型不支持、key 重复、缺少 email。

## Registration

### POST `/api/public/activities/{slug}/register`

鉴权：否。请求：

```json
{ "name": "张三", "email": "a@example.com", "phone": "13800000000", "form_data": { "school": "Example" } }
```

响应报名 ID 和状态。错误：活动未开放、时间不允许、人数已满、必填缺失、邮箱重复。

### GET `/api/admin/registrations`

鉴权：是。参数：`activity_id`, `page`, `page_size`, `keyword`, `status`, `has_account`。响应分页报名列表。

### GET/PUT/DELETE `/api/admin/registrations/{registration_id}`

鉴权：是。读取、更新、删除报名记录。

### POST `/api/admin/registrations/batch-update-status`

鉴权：是。请求：

```json
{ "registration_ids": [1, 2], "status": "approved" }
```

## Account

### GET `/api/admin/accounts`

鉴权：是。参数：`activity_id`, `keyword`, `status`, `page`, `page_size`。

### POST `/api/admin/accounts/generate`

鉴权：是。请求：

```json
{
  "activity_id": 1,
  "registration_ids": [1, 2],
  "prefix": "acm2026_",
  "start_number": 1,
  "digits": 4,
  "password_length": 12,
  "avoid_ambiguous_chars": true,
  "overwrite": false
}
```

响应创建数、跳过数、错误列表。

### POST `/api/admin/accounts/import`

鉴权：是。`multipart/form-data`: `file`, `activity_id`, `match_field`, `overwrite`。文件字段：`email`, `username`, `password`。

### POST `/api/admin/accounts/reset-password`

鉴权：是。请求：`account_ids`, `password_length`。

## Email Template

### GET `/api/admin/email-templates`

鉴权：是。参数：`activity_id`, `type`。

### POST `/api/admin/email-templates`

鉴权：是。创建模板：`activity_id`, `name`, `type`, `subject`, `body`, `enabled`。

### PUT/DELETE `/api/admin/email-templates/{template_id}`

鉴权：是。更新或删除模板。

### POST `/api/admin/email-templates/{template_id}/preview`

鉴权：是。请求：`registration_id` 可选。响应渲染后的 `subject`, `body`, `missing_variables`。

## Email Job

### POST `/api/admin/email/send-test`

鉴权：是。请求：`template_id`, `to_email`, `registration_id` 可选。同步发送一封测试邮件。

### POST `/api/admin/email/send-batch`

鉴权：是。请求：

```json
{ "activity_id": 1, "template_id": 1, "registration_ids": [1, 2], "skip_sent": true }
```

响应 `job_id`, `total_count`, `enqueued`。

### GET `/api/admin/email/jobs`

鉴权：是。参数：`activity_id`, `status`, `page`, `page_size`。

### GET `/api/admin/email/jobs/{job_id}`

鉴权：是。返回任务和日志。

### POST `/api/admin/email/jobs/{job_id}/retry-failed`

鉴权：是。将失败日志重置为 `retrying` 并重新入队。

## Settings

### GET `/api/admin/settings/smtp`

鉴权：是。返回当前 SMTP 配置摘要、密码是否已配置，以及配置来源（环境变量或系统设置）。

### PUT `/api/admin/settings/smtp`

鉴权：是。保存 SMTP 设置。请求字段：`host`, `port`, `username`, `password`, `clear_password`, `from_name`, `from_email`, `use_ssl`, `timeout_seconds`。`password` 留空表示不修改已保存密码。

### POST `/api/admin/settings/smtp/test`

鉴权：是。请求：`to_email`, `subject`, `body`。使用当前有效 SMTP 配置发送测试邮件。

## Import

### POST `/api/admin/import/registrations`

鉴权：是。`multipart/form-data`: `file`, `activity_id`, `overwrite`。支持 CSV/XLSX。返回导入数和错误报告。

## Export

### GET `/api/admin/export/registrations`

鉴权：是。参数：`activity_id`, `format=csv|xlsx`, `status`, `keyword`。返回下载文件。
