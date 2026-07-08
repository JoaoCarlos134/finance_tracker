import { formatAmount, formatDate, isNegative } from '../utils/summary'

const gridCols = { display: 'grid', gridTemplateColumns: '1.6fr 1fr 0.8fr 0.9fr', alignItems: 'center' }

function SkeletonRow() {
  return (
    <div style={{ ...gridCols, padding: '15px 24px', borderBottom: '1px solid var(--color-border-soft)', gap: 10 }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
        <div className="skeleton" style={{ width: 30, height: 30, borderRadius: 8 }} />
        <div className="skeleton" style={{ height: 13, width: 120 }} />
      </div>
      <div className="skeleton" style={{ height: 13, width: 70 }} />
      <div className="skeleton" style={{ height: 13, width: 50 }} />
      <div className="skeleton" style={{ height: 13, width: 60, marginLeft: 'auto' }} />
    </div>
  )
}

function TransactionRow({ tx }) {
  const negative = isNegative(tx.amount)
  return (
    <div
      style={{ ...gridCols, padding: '15px 24px', borderBottom: '1px solid var(--color-border-soft)' }}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
        <div style={{ width: 30, height: 30, borderRadius: 8, background: 'var(--color-warm-100)', flexShrink: 0 }} />
        <div style={{ fontSize: 14, fontWeight: 500, color: 'var(--color-ink-900)' }}>{tx.description}</div>
      </div>
      <div style={{ fontSize: 13, color: 'var(--color-warm-600)' }}>{tx.category ?? '—'}</div>
      <div style={{ fontSize: 13, fontFamily: 'var(--font-numeric)', color: 'var(--color-warm-600)' }}>{formatDate(tx.date)}</div>
      <div
        style={{
          fontSize: 14.5,
          textAlign: 'right',
          fontFamily: 'var(--font-numeric)',
          fontVariantNumeric: 'tabular-nums',
          color: negative ? 'var(--color-error)' : 'var(--color-success)',
        }}
      >
        {formatAmount(tx.amount)}
      </div>
    </div>
  )
}

function UploadControl({ onFilesSelected, label, directory = false }) {
  const directoryProps = directory ? { webkitdirectory: '', directory: '' } : {}
  return (
    <label
      style={{
        display: 'inline-block',
        padding: '9px 18px',
        background: 'var(--color-ink-900)',
        color: 'var(--color-bg)',
        borderRadius: 8,
        fontSize: 13,
        cursor: 'pointer',
      }}
    >
      {label}
      <input
        type="file"
        accept=".csv"
        multiple
        {...directoryProps}
        onChange={(e) => onFilesSelected(Array.from(e.target.files))}
        style={{ display: 'none' }}
      />
    </label>
  )
}

export default function TransactionsCard({ status, transactions, uploadStatus, onFilesSelected, onRetry }) {
  return (
    <div style={{ background: 'var(--color-surface)', borderRadius: 14, overflow: 'hidden', boxShadow: '0 1px 2px rgba(18,32,46,0.05)' }}>
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '18px 24px',
          borderBottom: '1px solid var(--color-border)',
          gap: 16,
        }}
      >
        <div style={{ fontFamily: 'var(--font-display)', fontWeight: 600, fontSize: 16, color: 'var(--color-ink-900)' }}>
          Recent transactions
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          {uploadStatus && <span style={{ fontSize: 12, color: 'var(--color-warm-500)', fontFamily: 'var(--font-numeric)' }}>{uploadStatus}</span>}
          <UploadControl onFilesSelected={onFilesSelected} label="Upload CSV" />
          <UploadControl onFilesSelected={onFilesSelected} label="Upload folder" directory />
        </div>
      </div>

      {status === 'default' && transactions.length > 0 && (
        <div>
          {transactions.map((tx) => (
            <TransactionRow key={tx.id} tx={tx} />
          ))}
        </div>
      )}

      {status === 'default' && transactions.length === 0 && (
        <div style={{ padding: '56px 24px', textAlign: 'center' }}>
          <div style={{ width: 40, height: 40, borderRadius: 10, background: 'var(--color-warm-100)', margin: '0 auto 14px' }} />
          <div style={{ fontSize: 14.5, color: 'var(--color-ink-900)', fontWeight: 500, marginBottom: 6 }}>No transactions yet</div>
          <div style={{ fontSize: 13, color: 'var(--color-warm-500)' }}>Upload a CSV statement to see activity here.</div>
        </div>
      )}

      {status === 'loading' && (
        <div>
          {[1, 2, 3, 4, 5].map((i) => (
            <SkeletonRow key={i} />
          ))}
        </div>
      )}

      {status === 'error' && (
        <div style={{ padding: '48px 24px', textAlign: 'center' }}>
          <div
            style={{
              width: 36,
              height: 36,
              borderRadius: '50%',
              background: 'var(--color-error-bg)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              margin: '0 auto 14px',
              color: 'var(--color-error)',
              fontFamily: 'var(--font-numeric)',
              fontSize: 16,
            }}
          >
            !
          </div>
          <div style={{ fontSize: 14.5, color: 'var(--color-ink-900)', fontWeight: 500, marginBottom: 6 }}>
            Couldn’t load transactions
          </div>
          <div style={{ fontSize: 13, color: 'var(--color-warm-500)', marginBottom: 16 }}>
            A network error occurred while reaching the backend.
          </div>
          <div
            onClick={onRetry}
            style={{
              display: 'inline-block',
              padding: '9px 18px',
              background: 'var(--color-ink-900)',
              color: 'var(--color-bg)',
              borderRadius: 8,
              fontSize: 13,
              cursor: 'pointer',
            }}
          >
            Retry
          </div>
        </div>
      )}
    </div>
  )
}
