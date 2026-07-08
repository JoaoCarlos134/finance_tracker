const SORT_FIELDS = [
  { value: 'date', label: 'Date' },
  { value: 'category', label: 'Category' },
  { value: 'amount', label: 'Value' },
]

function Pill({ active, onClick, children }) {
  return (
    <div
      onClick={onClick}
      style={{
        padding: '6px 14px',
        borderRadius: 20,
        fontSize: 12.5,
        fontFamily: 'var(--font-numeric)',
        cursor: 'pointer',
        whiteSpace: 'nowrap',
        transition: 'all 0.15s ease',
        background: active ? 'var(--color-ink-900)' : 'var(--color-surface)',
        color: active ? 'var(--color-bg)' : 'var(--color-warm-600)',
        boxShadow: active ? 'none' : 'inset 0 0 0 1px var(--color-border)',
      }}
    >
      {children}
    </div>
  )
}

function Label({ children }) {
  return (
    <span style={{ fontSize: 12, color: 'var(--color-warm-500)', fontFamily: 'var(--font-body)' }}>
      {children}
    </span>
  )
}

export default function TransactionControls({
  sortField,
  sortDirection,
  onSortFieldChange,
  onSortDirectionToggle,
  months,
  selectedMonth,
  onMonthChange,
}) {
  return (
    <div
      style={{
        display: 'flex',
        flexWrap: 'wrap',
        alignItems: 'center',
        gap: 8,
        padding: '14px 24px',
        borderBottom: '1px solid var(--color-border)',
      }}
    >
      <Label>Sort by</Label>
      {SORT_FIELDS.map((f) => (
        <Pill key={f.value} active={sortField === f.value} onClick={() => onSortFieldChange(f.value)}>
          {f.label}
        </Pill>
      ))}
      <div
        onClick={onSortDirectionToggle}
        title={sortDirection === 'asc' ? 'Ascending' : 'Descending'}
        style={{
          padding: '6px 14px',
          borderRadius: 20,
          fontSize: 12.5,
          fontFamily: 'var(--font-numeric)',
          cursor: 'pointer',
          color: 'var(--color-warm-600)',
          boxShadow: 'inset 0 0 0 1px var(--color-border)',
        }}
      >
        {sortDirection === 'asc' ? '↑ Ascending' : '↓ Descending'}
      </div>

      {months.length > 0 && (
        <>
          <Label>· Month</Label>
          <Pill active={selectedMonth === null} onClick={() => onMonthChange(null)}>
            All
          </Pill>
          {months.map((m) => (
            <Pill key={m.key} active={selectedMonth === m.key} onClick={() => onMonthChange(m.key)}>
              {m.label}
            </Pill>
          ))}
        </>
      )}
    </div>
  )
}
