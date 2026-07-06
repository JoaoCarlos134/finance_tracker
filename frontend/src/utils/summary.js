const currencyFormatter = new Intl.NumberFormat("pt-BR", {
  style: "currency",
  currency: "BRL",
})

export function formatAmount(amount) {
  return currencyFormatter.format(amount)
}

const dateFormatter = new Intl.DateTimeFormat("pt-BR", { day: "2-digit", month: "short" })

export function formatDate(dateStr) {
  return dateFormatter.format(new Date(`${dateStr}T00:00:00`))
}

function monthKey(dateStr) {
  return dateStr.slice(0, 7) // "YYYY-MM"
}

export function computeSummary(transactions) {
  const balance = transactions.reduce((sum, t) => sum + t.amount, 0)
  const income = transactions.reduce((sum, t) => (t.amount > 0 ? sum + t.amount : sum), 0)
  const spending = transactions.reduce((sum, t) => (t.amount < 0 ? sum + t.amount : sum), 0)

  // Only show a month-over-month trend when there's enough history to
  // compute one honestly — never fabricate a trend from a single month.
  const byMonth = new Map()
  for (const t of transactions) {
    const key = monthKey(t.date)
    byMonth.set(key, (byMonth.get(key) || 0) + t.amount)
  }
  const months = [...byMonth.keys()].sort()

  let monthOverMonthChange = null
  if (months.length >= 2) {
    const latestMonth = months[months.length - 1]
    const previousMonth = months[months.length - 2]

    const balanceThrough = (monthKey_) =>
      transactions
        .filter((t) => monthKey(t.date) <= monthKey_)
        .reduce((sum, t) => sum + t.amount, 0)

    const previousBalance = balanceThrough(previousMonth)
    const latestBalance = balanceThrough(latestMonth)
    if (previousBalance !== 0) {
      monthOverMonthChange = ((latestBalance - previousBalance) / Math.abs(previousBalance)) * 100
    }
  }

  return { balance, income, spending, monthOverMonthChange }
}
