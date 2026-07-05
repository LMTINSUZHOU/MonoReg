import { request, unwrap, type PageResult } from './request'
import type { Account } from './types'

export function listAccounts(params: Record<string, unknown>) {
  return unwrap<PageResult<Account>>(request.get('/api/admin/accounts', { params }))
}

export function generateAccounts(payload: Record<string, unknown>) {
  return unwrap<{ created_count: number; skipped_count: number; errors: unknown[] }>(
    request.post('/api/admin/accounts/generate', payload)
  )
}

export function importAccounts(form: FormData) {
  return unwrap<{ imported_count: number; failed_count: number; errors: unknown[] }>(
    request.post('/api/admin/accounts/import', form)
  )
}

export function resetPasswords(account_ids: number[], password_length = 12) {
  return unwrap<{ updated_count: number }>(
    request.post('/api/admin/accounts/reset-password', { account_ids, password_length })
  )
}

