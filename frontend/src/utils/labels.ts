export interface LabelOption {
  label: string
  value: string
}

export const activityStatusOptions: LabelOption[] = [
  { label: '草稿', value: 'draft' },
  { label: '开放报名', value: 'open' },
  { label: '暂停报名', value: 'paused' },
  { label: '已关闭', value: 'closed' },
  { label: '已归档', value: 'archived' }
]

export const registrationStatusOptions: LabelOption[] = [
  { label: '待处理', value: 'pending' },
  { label: '已通过', value: 'approved' },
  { label: '已拒绝', value: 'rejected' },
  { label: '已取消', value: 'cancelled' },
  { label: '待生成账号', value: 'account_pending' },
  { label: '账号已就绪', value: 'account_ready' },
  { label: '账号已发送', value: 'account_sent' },
  { label: '邮件发送失败', value: 'mail_failed' }
]

export const accountStatusOptions: LabelOption[] = [
  { label: '待处理', value: 'pending' },
  { label: '已就绪', value: 'ready' },
  { label: '已发送', value: 'sent' },
  { label: '已禁用', value: 'disabled' }
]

export const emailJobStatusOptions: LabelOption[] = [
  { label: '待发送', value: 'pending' },
  { label: '发送中', value: 'running' },
  { label: '已完成', value: 'completed' },
  { label: '失败', value: 'failed' },
  { label: '已取消', value: 'cancelled' },
  { label: '重试中', value: 'retrying' },
  { label: '发送中', value: 'sending' },
  { label: '已跳过', value: 'skipped' }
]

export const fieldTypeOptions: LabelOption[] = [
  { label: '单行文本', value: 'text' },
  { label: '多行文本', value: 'textarea' },
  { label: '邮箱', value: 'email' },
  { label: '手机号', value: 'phone' },
  { label: '数字', value: 'number' },
  { label: '下拉单选', value: 'select' },
  { label: '下拉多选', value: 'multi_select' },
  { label: '单选按钮', value: 'radio' },
  { label: '勾选确认', value: 'checkbox' },
  { label: '日期', value: 'date' }
]

export const templateTypeOptions: LabelOption[] = [
  { label: '报名确认', value: 'registration_confirm' },
  { label: '账号信息', value: 'account_info' },
  { label: '通过通知', value: 'approval_notice' },
  { label: '拒绝通知', value: 'rejection_notice' },
  { label: '自定义通知', value: 'custom_notice' }
]

function labelFrom(options: LabelOption[], value: string) {
  return options.find((item) => item.value === value)?.label || value
}

export function statusLabel(value: string) {
  const labels: Record<string, string> = {
    ...Object.fromEntries(activityStatusOptions.map((item) => [item.value, item.label])),
    pending: '待处理',
    approved: '已通过',
    rejected: '已拒绝',
    cancelled: '已取消',
    account_pending: '待生成账号',
    account_ready: '账号已就绪',
    account_sent: '账号已发送',
    mail_failed: '邮件发送失败',
    ready: '已就绪',
    sent: '已发送',
    disabled: '已禁用',
    running: '发送中',
    completed: '已完成',
    failed: '失败',
    retrying: '重试中',
    sending: '发送中',
    skipped: '已跳过'
  }
  return labels[value] || value
}

export function emailJobStatusLabel(value: string) {
  return labelFrom(emailJobStatusOptions, value)
}

export function fieldTypeLabel(value: string) {
  return labelFrom(fieldTypeOptions, value)
}

export function templateTypeLabel(value: string) {
  return labelFrom(templateTypeOptions, value)
}
