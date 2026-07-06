const API_BASE_URL = 'http://localhost:8000'

export async function fetchTransactions() {
  const res = await fetch(`${API_BASE_URL}/transactions`)
  if (!res.ok) {
    throw new Error(`Failed to fetch transactions: ${res.status}`)
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
