import { Bar, BarChart, CartesianGrid, Legend, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import { formatAmount } from '../utils/summary'

const monthLabelFormatter = new Intl.DateTimeFormat('pt-BR', { month: 'short', year: '2-digit' })

function monthLabel(monthKey) {
  const [year, month] = monthKey.split('-').map(Number)
  return monthLabelFormatter.format(new Date(year, month - 1, 1))
}

function CustomTooltip({ active, payload, label }) {
  if (!active || !payload?.length) return null
  return (
    <div
      style={{
        background: 'var(--color-ink-900)',
        color: 'var(--color-bg)',
        padding: '8px 12px',
        borderRadius: 8,
        fontSize: 12.5,
        fontFamily: 'var(--font-body)',
      }}
    >
      <div style={{ fontWeight: 500, marginBottom: 4 }}>{label}</div>
      {payload.map((p) => (
        <div key={p.dataKey} style={{ fontFamily: 'var(--font-numeric)', color: p.color }}>
          {p.name}: {formatAmount(p.value)}
        </div>
      ))}
    </div>
  )
}

export default function MonthlyChart({ monthly }) {
  if (monthly.length === 0) {
    return (
      <div style={{ padding: '32px 24px', textAlign: 'center', color: 'var(--color-warm-500)', fontSize: 13.5 }}>
        No monthly data yet.
      </div>
    )
  }

  const data = monthly.map((m) => ({
    month: monthLabel(m.month),
    Income: Number(m.income),
    Spending: Number(m.spending),
  }))

  return (
    <div style={{ height: 260 }}>
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data} margin={{ top: 8, right: 8, left: 8, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#f0ebe1" vertical={false} />
          <XAxis
            dataKey="month"
            tick={{ fontSize: 12, fontFamily: 'IBM Plex Sans, sans-serif', fill: '#8a8072' }}
            axisLine={{ stroke: '#f0ebe1' }}
            tickLine={false}
          />
          <YAxis
            tick={{ fontSize: 11, fontFamily: 'Archivo, sans-serif', fill: '#8a8072' }}
            axisLine={false}
            tickLine={false}
            width={70}
          />
          <Tooltip content={<CustomTooltip />} />
          <Legend wrapperStyle={{ fontSize: 12.5, fontFamily: 'IBM Plex Sans, sans-serif' }} />
          <Bar dataKey="Income" fill="#2f6844" radius={[4, 4, 0, 0]} isAnimationActive={false} />
          <Bar dataKey="Spending" fill="#b23b3b" radius={[4, 4, 0, 0]} isAnimationActive={false} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}
