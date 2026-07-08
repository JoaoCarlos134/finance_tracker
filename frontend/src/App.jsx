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

  const handleFilesSelected = async (files) => {
    const csvFiles = files.filter((f) => f.name.toLowerCase().endsWith('.csv'))
    if (csvFiles.length === 0) {
      setUploadStatus('No .csv files found in that selection')
      return
    }

    // Sequential, not Promise.all: each POST commits its own DB session, and
    // running them one at a time keeps per-file failures isolated and the
    // progress message meaningful for folder uploads with many files.
    const results = []
    for (const file of csvFiles) {
      setUploadStatus(`Uploading ${results.length + 1}/${csvFiles.length}: ${file.name}...`)
      try {
        results.push({ file: file.name, ...(await uploadCsv(file)) })
      } catch (err) {
        results.push({ file: file.name, failed: true, message: err.message })
      }
    }

    const inserted = results.reduce((sum, r) => sum + (r.rows_inserted ?? 0), 0)
    const skipped = results.reduce((sum, r) => sum + (r.rows_skipped ?? 0), 0)
    const failed = results.filter((r) => r.failed)
    setUploadStatus(
      `${csvFiles.length} file(s): ${inserted} rows inserted` +
        (skipped ? `, ${skipped} skipped` : '') +
        (failed.length ? `, ${failed.length} failed (${failed.map((f) => f.file).join(', ')})` : ''),
    )
    loadAll()
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
          onFilesSelected={handleFilesSelected}
          onRetry={loadAll}
        />
      </div>
    </div>
  )
}

export default App
