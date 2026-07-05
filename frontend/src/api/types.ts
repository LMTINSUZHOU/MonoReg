export interface Activity {
  id: number
  title: string
  slug: string
  description?: string
  status: string
  start_time?: string
  end_time?: string
  max_registrations?: number
  need_account: boolean
  auto_generate_account: boolean
  send_confirm_email: boolean
  send_account_email_immediately: boolean
  login_url?: string
  created_at?: string
  updated_at?: string
}

export interface FormField {
  id?: number
  activity_id?: number
  field_key: string
  field_label: string
  field_type: string
  required: boolean
  placeholder?: string
  help_text?: string
  options_json: string[]
  validation_json: Record<string, unknown>
  show_in_table: boolean
  sort_order: number
}

export interface Registration {
  id: number
  activity_id: number
  name?: string
  email: string
  phone?: string
  status: string
  form_data: Record<string, unknown>
  submitted_at: string
  updated_at: string
  account?: {
    id: number
    username: string
    status: string
    sent_at?: string
  } | null
}

export interface Account {
  id: number
  activity_id: number
  registration_id: number
  username: string
  status: string
  sent_at?: string
  registration?: Registration
}

export interface EmailTemplate {
  id: number
  activity_id?: number
  name: string
  type: string
  subject: string
  body: string
  enabled: boolean
  created_at?: string
  updated_at?: string
}

export interface EmailJob {
  id: number
  activity_id: number
  template_id?: number
  job_type: string
  status: string
  total_count: number
  success_count: number
  failed_count: number
  created_at: string
  logs?: EmailLog[]
}

export interface EmailLog {
  id: number
  registration_id?: number
  to_email: string
  subject: string
  body_snapshot?: string
  status: string
  error_message?: string
  retry_count: number
  sent_at?: string
  created_at: string
}

export interface SmtpSettings {
  host: string
  port: number
  username: string
  from_name: string
  from_email: string
  use_ssl: boolean
  timeout_seconds: number
  password_configured: boolean
  source: 'database' | 'environment'
}
