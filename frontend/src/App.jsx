import { useEffect, useState } from 'react'
import {
  fetchAnalyticsSummary,
  fetchByCategory,
  fetchCategories,
  fetchMonthly,
  fetchTransactions,
  updateCategory,
  uploadCsv,
} from './api'
import TopNav from './components/TopNav'
import SummaryCard from './components/SummaryCard'
import TransactionsCard from './components/TransactionsCard'
import AccountTypeToggle from './components/AccountTypeToggle'
import MonthlyChart from './components/MonthlyChart'
import CategoryBreakdownChart from './components/CategoryBreakdownChart'
import { monthOverMonthChange } from './utils/summary'

const EMPTY_SUMMARY = { balance: 0, income: 0, spending: 0 }

const chartCard = {
  background: 'var(--color-surface)',
  borderRadius: 14,
  padding: '20px 24px',
  marginBottom: 28,
  boxShadow: '0 1px 2px rgba(18,32,46,0.05)',
}

const chartTitle = {
  fontFamily: 'var(--font-display)',
  fontWeight: 600,
  fontSize: 16,
  color: 'var(--color-ink-900)',
  marginBottom: 12,
}

function App() {
  const [transactions, setTransactions] = useState([])
  const [summary, setSummary] = useState(EMPTY_SUMMARY)
  const [monthly, setMonthly] = useState([])
  const [byCategory, setByCategory] = useState([])
  const [categories, setCategories] = useState([])
  const [accountType, setAccountType] = useState(null) // null | 'bank' | 'credit_card'
  const [status, setStatus] = useState('loading') // 'loading' | 'error' | 'default'
  const [uploadStatus, setUploadStatus] = useState(null)

  const loadAll = () => {
    setStatus('loading')
    Promise.all([
      fetchTransactions({ accountType, limit: 500 }),
      fetchAnalyticsSummary({ accountType }),
      fetchMonthly({ accountType }),
      fetchByCategory({ accountType }),
      fetchCategories(),
    ])
      .then(([txs, summaryData, monthlyData, byCategoryData, categoryData]) => {
        setTransactions(txs)
        setSummary(summaryData)
        setMonthly(monthlyData)
        setByCategory(byCategoryData)
        setCategories(categoryData)
        setStatus('default')
      })
      .catch(() => setStatus('error'))
  }

  useEffect(() => {
    loadAll()
  }, [accountType])

  const handleCategoryChange = async (id, category) => {
    // Optimistic: the row updates instantly, reverted only if the PATCH
    // fails. category_source flips server-side too, but no need to refetch
    // it here since nothing in this view displays that field.
    const previous = transactions
    setTransactions((txs) => txs.map((t) => (t.id === id ? { ...t, category } : t)))
    try {
      await updateCategory(id, category)
    } catch {
      setTransactions(previous)
    }
  }

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
    const duplicate = results.reduce((sum, r) => sum + (r.rows_duplicate ?? 0), 0)
    const skipped = results.reduce((sum, r) => sum + (r.rows_skipped ?? 0), 0)
    const failed = results.filter((r) => r.failed)
    setUploadStatus(
      `${csvFiles.length} file(s): ${inserted} rows inserted` +
        (duplicate ? `, ${duplicate} duplicate` : '') +
        (skipped ? `, ${skipped} skipped` : '') +
        (failed.length ? `, ${failed.length} failed (${failed.map((f) => f.file).join(', ')})` : ''),
    )
    loadAll()
  }

  return (
    <div style={{ minHeight: '100vh', background: 'var(--color-bg)' }}>
      <TopNav />
      <div style={{ padding: '32px 28px 64px', maxWidth: 1180, margin: '0 auto' }}>
        <AccountTypeToggle value={accountType} onChange={setAccountType} />
        <SummaryCard
          balance={summary.balance}
          income={summary.income}
          spending={summary.spending}
          monthOverMonthChange={monthOverMonthChange(monthly)}
        />
        <div style={{ display: 'grid', gridTemplateColumns: '1.3fr 1fr', gap: 20 }}>
          <div style={chartCard}>
            <div style={chartTitle}>Income vs. spending by month</div>
            <MonthlyChart monthly={monthly} />
          </div>
          <div style={chartCard}>
            <div style={chartTitle}>Spending by category</div>
            <CategoryBreakdownChart categories={byCategory} />
          </div>
        </div>
        <TransactionsCard
          status={status}
          transactions={transactions}
          categories={categories}
          uploadStatus={uploadStatus}
          onFilesSelected={handleFilesSelected}
          onCategoryChange={handleCategoryChange}
          onRetry={loadAll}
        />
      </div>
    </div>
  )
}

export default App
