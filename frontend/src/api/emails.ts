import { request, unwrap, type PageResult } from './request'
import type { EmailJob, EmailTemplate } from './types'

export function listTemplates(params: Record<string, unknown>) {
  return unwrap<EmailTemplate[]>(request.get('/api/admin/email-templates', { params }))
}

export function createTemplate(payload: Partial<EmailTemplate>) {
  return unwrap<EmailTemplate>(request.post('/api/admin/email-templates', payload))
}

export function updateTemplate(id: number, payload: Partial<EmailTemplate>) {
  return unwrap<EmailTemplate>(request.put(`/api/admin/email-templates/${id}`, payload))
}

export function deleteTemplate(id: number) {
  return unwrap<{ id: number }>(request.delete(`/api/admin/email-templates/${id}`))
}

export function previewTemplate(id: number, registration_id?: number) {
  return unwrap<{ subject: string; body: string; missing_variables: string[] }>(
    request.post(`/api/admin/email-templates/${id}/preview`, { registration_id })
  )
}

export function sendTestEmail(payload: Record<string, unknown>) {
  return unwrap<Record<string, unknown>>(request.post('/api/admin/email/send-test', payload))
}

export function sendBatchEmail(payload: Record<string, unknown>) {
  return unwrap<{ job_id: number; total_count: number; enqueued: boolean }>(
    request.post('/api/admin/email/send-batch', payload)
  )
}

export function listEmailJobs(params: Record<string, unknown>) {
  return unwrap<PageResult<EmailJob>>(request.get('/api/admin/email/jobs', { params }))
}

export function getEmailJob(id: number) {
  return unwrap<EmailJob>(request.get(`/api/admin/email/jobs/${id}`))
}

export function retryFailedJob(id: number) {
  return unwrap<{ job_id: number; enqueued: boolean }>(request.post(`/api/admin/email/jobs/${id}/retry-failed`))
}

