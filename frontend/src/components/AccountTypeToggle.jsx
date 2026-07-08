const OPTIONS = [
  { value: null, label: 'All' },
  { value: 'bank', label: 'Bank' },
  { value: 'credit_card', label: 'Credit Card' },
]

export default function AccountTypeToggle({ value, onChange }) {
  return (
    <div style={{ display: 'flex', gap: 8, marginBottom: 20 }}>
      {OPTIONS.map((opt) => {
        const active = opt.value === value
        return (
          <div
            key={opt.label}
            onClick={() => onChange(opt.value)}
            style={{
              padding: '7px 16px',
              borderRadius: 20,
              fontSize: 12.5,
              fontFamily: 'var(--font-numeric)',
              cursor: 'pointer',
              transition: 'all 0.15s ease',
              background: active ? 'var(--color-ink-900)' : 'var(--color-surface)',
              color: active ? 'var(--color-bg)' : 'var(--color-warm-600)',
              boxShadow: active ? 'none' : 'inset 0 0 0 1px var(--color-border)',
            }}
          >
            {opt.label}
          </div>
        )
      })}
    </div>
  )
}
