import { request, unwrap, type PageResult } from './request'
import type { Registration } from './types'

export function submitPublicRegistration(slug: string, payload: Record<string, unknown>) {
  return unwrap<{ registration_id: number; status: string }>(
    request.post(`/api/public/activities/${slug}/register`, payload)
  )
}

export function listRegistrations(params: Record<string, unknown>) {
  return unwrap<PageResult<Registration>>(request.get('/api/admin/registrations', { params }))
}

export function getRegistration(id: number) {
  return unwrap<Registration & { activity?: { id: number; title: string; slug: string } }>(
    request.get(`/api/admin/registrations/${id}`)
  )
}

export function updateRegistration(id: number, payload: Partial<Registration>) {
  return unwrap<Registration>(request.put(`/api/admin/registrations/${id}`, payload))
}

export function batchUpdateRegistrationStatus(registration_ids: number[], status: string) {
  return unwrap<{ updated_count: number }>(
    request.post('/api/admin/registrations/batch-update-status', { registration_ids, status })
  )
}

export function deleteRegistration(id: number) {
  return unwrap<{ id: number }>(request.delete(`/api/admin/registrations/${id}`))
}

export function exportRegistrations(params: Record<string, unknown>) {
  return request.get('/api/admin/export/registrations', { params, responseType: 'blob' })
}

