import { request, unwrap } from './request'
import type { SmtpSettings } from './types'

export interface SmtpSettingsPayload {
  host: string
  port: number
  username: string
  password?: string
  clear_password: boolean
  from_name: string
  from_email: string
  use_ssl: boolean
  timeout_seconds: number
}

export function getSmtpSettings() {
  return unwrap<SmtpSettings>(request.get('/api/admin/settings/smtp'))
}

export function updateSmtpSettings(payload: SmtpSettingsPayload) {
  return unwrap<SmtpSettings>(request.put('/api/admin/settings/smtp', payload))
}

export function sendSmtpTest(payload: { to_email: string; subject: string; body: string }) {
  return unwrap<{ to_email: string }>(request.post('/api/admin/settings/smtp/test', payload))
}
