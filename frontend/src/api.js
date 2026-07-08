// Relative in dev (Vite proxies /api to the backend); override for
// deployments where the API lives on another origin.
const API_BASE_URL = import.meta.env.VITE_API_URL ?? '/api'

async function getJson(path, params = {}) {
  const query = new URLSearchParams(
    Object.fromEntries(Object.entries(params).filter(([, v]) => v != null)),
  ).toString()
  const res = await fetch(`${API_BASE_URL}${path}${query ? `?${query}` : ''}`)
  if (!res.ok) {
    throw new Error(`GET ${path} failed: ${res.status}`)
  }
  return res.json()
}

export function fetchTransactions({ accountType, limit } = {}) {
  return getJson('/transactions', { account_type: accountType, limit })
}

export function fetchAnalyticsSummary({ accountType } = {}) {
  return getJson('/analytics/summary', { account_type: accountType })
}

export function fetchMonthly({ accountType } = {}) {
  return getJson('/analytics/monthly', { account_type: accountType })
}

export function fetchByCategory({ accountType } = {}) {
  return getJson('/analytics/by-category', { account_type: accountType })
}

export function fetchCategories() {
  return getJson('/categories')
}

export async function updateCategory(id, category) {
  const res = await fetch(`${API_BASE_URL}/transactions/${id}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ category }),
  })
  if (!res.ok) {
    throw new Error(`PATCH /transactions/${id} failed: ${res.status}`)
  }
  return res.json()
}

export async function uploadCsv(file) {
  const formData = new FormData()
  formData.append('file', file)

  const res = await fetch(`${API_BASE_URL}/ingest/csv`, {
    method: 'POST',
    body: formData,
  })
  const body = await res.json()
  if (!res.ok) {
    throw new Error(typeof body.detail === 'string' ? body.detail : JSON.stringify(body.detail))
  }
  return body
}
