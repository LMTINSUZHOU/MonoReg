import { request, unwrap, type PageResult } from './request'
import type { Activity, FormField } from './types'

export function listActivities(params: Record<string, unknown>) {
  return unwrap<PageResult<Activity>>(request.get('/api/admin/activities', { params }))
}

export function getActivity(id: number) {
  return unwrap<Activity>(request.get(`/api/admin/activities/${id}`))
}

export function createActivity(payload: Partial<Activity>) {
  return unwrap<Activity>(request.post('/api/admin/activities', payload))
}

export function updateActivity(id: number, payload: Partial<Activity>) {
  return unwrap<Activity>(request.put(`/api/admin/activities/${id}`, payload))
}

export function deleteActivity(id: number) {
  return unwrap<{ id: number }>(request.delete(`/api/admin/activities/${id}`))
}

export function publishActivity(id: number) {
  return unwrap<Activity>(request.post(`/api/admin/activities/${id}/publish`))
}

export function closeActivity(id: number) {
  return unwrap<Activity>(request.post(`/api/admin/activities/${id}/close`))
}

export function duplicateActivity(id: number) {
  return unwrap<Activity>(request.post(`/api/admin/activities/${id}/duplicate`))
}

export function getPublicActivity(slug: string) {
  return unwrap<{ activity: Activity; fields: Array<FormField & { key?: string; label?: string; type?: string; options?: string[] }> }>(
    request.get(`/api/public/activities/${slug}`)
  )
}

export function listFormFields(activityId: number) {
  return unwrap<FormField[]>(request.get(`/api/admin/activities/${activityId}/form-fields`))
}

export function saveFormFields(activityId: number, fields: FormField[]) {
  return unwrap<FormField[]>(request.put(`/api/admin/activities/${activityId}/form-fields`, { fields }))
}

