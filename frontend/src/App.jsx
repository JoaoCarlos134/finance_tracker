import { useEffect, useState } from 'react'
import { fetchAnalyticsSummary, fetchMonthly, fetchTransactions, uploadCsv } from './api'
import TopNav from './components/TopNav'
import SummaryCard from './components/SummaryCard'
import TransactionsCard from './components/TransactionsCard'
import { monthOverMonthChange } from './utils/summary'

const EMPTY_SUMMARY = { balance: 0, income: 0, spending: 0 }

function App() {
  const [transactions, setTransactions] = useState([])
  const [summary, setSummary] = useState(EMPTY_SUMMARY)
  const [monthly, setMonthly] = useState([])
  const [status, setStatus] = useState('loading') // 'loading' | 'error' | 'default'
  const [uploadStatus, setUploadStatus] = useState(null)

  const loadAll = () => {
    setStatus('loading')
    Promise.all([fetchTransactions(), fetchAnalyticsSummary(), fetchMonthly()])
      .then(([txs, summaryData, monthlyData]) => {
        setTransactions(txs)
        setSummary(summaryData)
        setMonthly(monthlyData)
        setStatus('default')
      })
      .catch(() => setStatus('error'))
  }

  useEffect(() => {
    loadAll()
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
      loadAll()
    } catch (err) {
      setUploadStatus(`Upload failed: ${err.message}`)
    } finally {
      event.target.value = ''
    }
  }

  return (
    <div style={{ minHeight: '100vh', background: 'var(--color-bg)' }}>
      <TopNav />
      <div style={{ padding: '32px 28px 64px', maxWidth: 1180, margin: '0 auto' }}>
        <SummaryCard
          balance={summary.balance}
          income={summary.income}
          spending={summary.spending}
          monthOverMonthChange={monthOverMonthChange(monthly)}
        />
        <TransactionsCard
          status={status}
          transactions={transactions}
          uploadStatus={uploadStatus}
          onFileChange={handleFileChange}
          onRetry={loadAll}
        />
      </div>
    </div>
  )
}

export default App
