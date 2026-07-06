import { useEffect, useState } from 'react'
import { fetchTransactions, uploadCsv } from './api'
import './App.css'

function App() {
  const [transactions, setTransactions] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [uploadStatus, setUploadStatus] = useState(null)

  const loadTransactions = () => {
    setLoading(true)
    fetchTransactions()
      .then(setTransactions)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false))
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

  return (
    <div className="app">
      <h1>Finance Tracker</h1>

      <section className="upload-section">
        <label htmlFor="csv-upload">Upload brokerage CSV statement:</label>
        <input id="csv-upload" type="file" accept=".csv" onChange={handleFileChange} />
        {uploadStatus && <p>{uploadStatus}</p>}
      </section>

      <section>
        <h2>Transactions</h2>
        {loading && <p>Loading...</p>}
        {error && <p className="error">Error: {error}</p>}
        {!loading && !error && transactions.length === 0 && <p>No transactions yet.</p>}
        {!loading && !error && transactions.length > 0 && (
          <table>
            <thead>
              <tr>
                <th>Date</th>
                <th>Description</th>
                <th>Amount</th>
                <th>Category</th>
                <th>Source File</th>
              </tr>
            </thead>
            <tbody>
              {transactions.map((tx) => (
                <tr key={tx.id}>
                  <td>{tx.date}</td>
                  <td>{tx.description}</td>
                  <td>{tx.amount.toFixed(2)}</td>
                  <td>{tx.category ?? '—'}</td>
                  <td>{tx.raw_source_file}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </section>
    </div>
  )
}

export default App
