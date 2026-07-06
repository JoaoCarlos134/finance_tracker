const currencyFormatter = new Intl.NumberFormat("pt-BR", {
  style: "currency",
  currency: "BRL",
})

// The API serializes money as exact decimal strings; Number() here is
// display-only (formatting/sign checks), never accounting math — the backend
// owns all aggregation.
export function formatAmount(amount) {
  return currencyFormatter.format(Number(amount))
}

export function isNegative(amount) {
  return Number(amount) < 0
}

const dateFormatter = new Intl.DateTimeFormat("pt-BR", { day: "2-digit", month: "short" })

export function formatDate(dateStr) {
  return dateFormatter.format(new Date(`${dateStr}T00:00:00`))
}

// Percentage change of cumulative balance between the last two months of
// /analytics/monthly. Null when there's under two months of history — never
// fabricate a trend from a single month.
export function monthOverMonthChange(monthlyPoints) {
  if (monthlyPoints.length < 2) return null

  let cumulative = 0
  const balances = monthlyPoints.map((point) => (cumulative += Number(point.net)))
  const previous = balances[balances.length - 2]
  const latest = balances[balances.length - 1]
  if (previous === 0) return null
  return ((latest - previous) / Math.abs(previous)) * 100
}
