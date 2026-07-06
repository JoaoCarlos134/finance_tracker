// Relative in dev (Vite proxies /api to the backend); override for
// deployments where the API lives on another origin.
const API_BASE_URL = import.meta.env.VITE_API_URL ?? '/api'

async function getJson(path) {
  const res = await fetch(`${API_BASE_URL}${path}`)
  if (!res.ok) {
    throw new Error(`GET ${path} failed: ${res.status}`)
  }
  return res.json()
}

export function fetchTransactions() {
  return getJson('/transactions')
}

export function fetchAnalyticsSummary() {
  return getJson('/analytics/summary')
}

export function fetchMonthly() {
  return getJson('/analytics/monthly')
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
