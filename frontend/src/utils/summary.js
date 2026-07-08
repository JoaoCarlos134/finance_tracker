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

const monthFormatter = new Intl.DateTimeFormat("pt-BR", { month: "short", year: "2-digit" })

// monthKey is "YYYY-MM" (from a transaction's date or /analytics/monthly)
export function formatMonth(monthKey) {
  const [year, month] = monthKey.split("-").map(Number)
  return monthFormatter.format(new Date(year, month - 1, 1))
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
  // A near-zero baseline (the running balance happens to cross ~0 that
  // month) makes any percentage change relative to it explode into a
  // meaningless number (e.g. -17117%) — hide it rather than show nonsense.
  if (Math.abs(previous) < 10) return null
  return ((latest - previous) / Math.abs(previous)) * 100
}
