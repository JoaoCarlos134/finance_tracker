import { formatAmount } from '../utils/summary'

export default function SummaryCard({ balance, income, spending, monthOverMonthChange }) {
  return (
    <div
      style={{
        background: 'var(--color-ink-900)',
        borderRadius: 14,
        padding: '28px 32px',
        marginBottom: 28,
        position: 'relative',
        overflow: 'hidden',
      }}
    >
      <div
        style={{
          position: 'absolute',
          inset: 0,
          background: 'radial-gradient(circle at 90% 0%, rgba(201,117,47,0.18), transparent 55%)',
        }}
      />
      <div
        style={{
          position: 'relative',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'flex-start',
          flexWrap: 'wrap',
          gap: 24,
        }}
      >
        <div>
          <div
            style={{
              fontSize: 12,
              color: '#8fa0ae',
              fontFamily: 'var(--font-numeric)',
              letterSpacing: '0.06em',
              textTransform: 'uppercase',
              marginBottom: 10,
            }}
          >
            Total balance
          </div>
          <div
            style={{
              fontFamily: 'var(--font-numeric)',
              fontWeight: 500,
              fontSize: 38,
              color: 'var(--color-bg)',
              fontVariantNumeric: 'tabular-nums',
            }}
          >
            {formatAmount(balance)}
          </div>
          {monthOverMonthChange !== null && (
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: 6,
                marginTop: 10,
                fontSize: 13,
                color: monthOverMonthChange >= 0 ? 'var(--color-success-soft)' : 'var(--color-error-soft)',
              }}
            >
              <span>{monthOverMonthChange >= 0 ? '▲' : '▼'}</span>
              <span style={{ fontFamily: 'var(--font-numeric)' }}>
                {monthOverMonthChange >= 0 ? '+' : ''}
                {monthOverMonthChange.toFixed(1)}%
              </span>
              <span style={{ color: '#7c8e9c' }}>vs last month</span>
            </div>
          )}
        </div>
        <div style={{ display: 'flex', gap: 28 }}>
          <div>
            <div style={{ fontSize: 12, color: '#8fa0ae', marginBottom: 6 }}>Income</div>
            <div style={{ fontFamily: 'var(--font-numeric)', fontSize: 18, color: 'var(--color-success-soft)' }}>
              {formatAmount(income)}
            </div>
          </div>
          <div>
            <div style={{ fontSize: 12, color: '#8fa0ae', marginBottom: 6 }}>Spending</div>
            <div style={{ fontFamily: 'var(--font-numeric)', fontSize: 18, color: 'var(--color-error-soft)' }}>
              {formatAmount(spending)}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
