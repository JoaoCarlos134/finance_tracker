import { useEffect, useState } from 'react'
import { fetchTransactions, uploadCsv } from './api'
import TopNav from './components/TopNav'
import SummaryCard from './components/SummaryCard'
import TransactionsCard from './components/TransactionsCard'
import { computeSummary } from './utils/summary'

function App() {
  const [transactions, setTransactions] = useState([])
  const [status, setStatus] = useState('loading') // 'loading' | 'error' | 'default'
  const [uploadStatus, setUploadStatus] = useState(null)

  const loadTransactions = () => {
    setStatus('loading')
    fetchTransactions()
      .then((data) => {
        setTransactions(data)
        setStatus('default')
      })
      .catch(() => setStatus('error'))
  }

  useEffect(() => {
    loadTransactions()
  }, [])

  const handleFileChange = async (event) => {
    const file = event.target.files[0]
    if (!file) return

    setUploadStatus('Uploading...')
    try {
      const result = await uploadCsv(file)
      setUploadStatus(
        `Inserted ${result.rows_inserted} of ${result.rows_parsed} rows` +
          (result.rows_skipped ? ` (${result.rows_skipped} skipped)` : ''),
      )
      loadTransactions()
    } catch (err) {
      setUploadStatus(`Upload failed: ${err.message}`)
    } finally {
      event.target.value = ''
    }
  }

  const summary = computeSummary(transactions)

  return (
    <div style={{ minHeight: '100vh', background: 'var(--color-bg)' }}>
      <TopNav />
      <div style={{ padding: '32px 28px 64px', maxWidth: 1180, margin: '0 auto' }}>
        <SummaryCard {...summary} />
        <TransactionsCard
          status={status}
          transactions={transactions}
          uploadStatus={uploadStatus}
          onFileChange={handleFileChange}
          onRetry={loadTransactions}
        />
      </div>
    </div>
  )
}

export default App
