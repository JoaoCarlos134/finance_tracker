import { Cell, Legend, Pie, PieChart, ResponsiveContainer, Tooltip } from 'recharts'
import { formatAmount } from '../utils/summary'

// Cycles through the design system's accent + semantic palette rather than
// an arbitrary rainbow, so the chart reads as part of the same visual
// system. Literal hex values (mirroring theme.css) because SVG fill
// attributes don't reliably resolve CSS custom properties across renderers.
const SLICE_COLORS = [
  '#c9752f', // --color-accent
  '#3e4a56', // --color-ink-700
  '#2f6844', // --color-success
  '#a8791a', // --color-warning
  '#b23b3b', // --color-error
  '#8a8072', // --color-warm-500
  '#a85e22', // --color-accent-dark
  '#b8ad9c', // --color-warm-300
]

function CustomTooltip({ active, payload }) {
  if (!active || !payload?.length) return null
  const { category, total, percentage } = payload[0].payload
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
      <div style={{ fontWeight: 500, marginBottom: 2 }}>{category}</div>
      <div style={{ fontFamily: 'var(--font-numeric)' }}>
        {formatAmount(total)} ({percentage.toFixed(1)}%)
      </div>
    </div>
  )
}

export default function CategoryBreakdownChart({ categories }) {
  // Only categories that represent real spending (negative net) are shown —
  // Income/Transfers would otherwise dwarf the discretionary-spending
  // slices this chart exists to surface.
  const spending = categories.filter((c) => Number(c.total) < 0)
  const totalSpending = spending.reduce((sum, c) => sum + Math.abs(Number(c.total)), 0)

  if (spending.length === 0 || totalSpending === 0) {
    return (
      <div style={{ padding: '32px 24px', textAlign: 'center', color: 'var(--color-warm-500)', fontSize: 13.5 }}>
        No spending yet to break down by category.
      </div>
    )
  }

  const data = spending
    .map((c) => ({
      category: c.category,
      total: Number(c.total),
      value: Math.abs(Number(c.total)),
      percentage: (Math.abs(Number(c.total)) / totalSpending) * 100,
    }))
    .sort((a, b) => a.total - b.total)

  return (
    <div style={{ height: 280 }}>
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie
            data={data}
            dataKey="value"
            nameKey="category"
            innerRadius={60}
            outerRadius={95}
            paddingAngle={2}
            isAnimationActive={false}
          >
            {data.map((entry, i) => (
              <Cell key={entry.category} fill={SLICE_COLORS[i % SLICE_COLORS.length]} />
            ))}
          </Pie>
          <Tooltip content={<CustomTooltip />} />
          <Legend
            layout="vertical"
            align="right"
            verticalAlign="middle"
            formatter={(value, entry) => (
              <span style={{ fontSize: 12.5, color: 'var(--color-warm-600)', fontFamily: 'var(--font-body)' }}>
                {value} <span style={{ color: 'var(--color-warm-500)' }}>({entry.payload.percentage.toFixed(0)}%)</span>
              </span>
            )}
          />
        </PieChart>
      </ResponsiveContainer>
    </div>
  )
}
