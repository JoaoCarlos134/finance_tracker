import { describe, expect, it } from 'vitest'
import { sortTransactions } from './TransactionsCard'

const rows = [
  { id: 1, date: '2026-05-01', category: 'Dining', amount: '-10.00' },
  { id: 2, date: '2026-04-01', category: 'Groceries', amount: '-50.00' },
  { id: 3, date: '2026-06-01', category: null, amount: '100.00' },
]

describe('sortTransactions', () => {
  it('sorts by date ascending and descending', () => {
    expect(sortTransactions(rows, 'date', 'asc').map((r) => r.id)).toEqual([2, 1, 3])
    expect(sortTransactions(rows, 'date', 'desc').map((r) => r.id)).toEqual([3, 1, 2])
  })

  it('sorts by amount numerically, not lexically', () => {
    expect(sortTransactions(rows, 'amount', 'asc').map((r) => r.id)).toEqual([2, 1, 3])
  })

  it('sorts by category, treating a null category as an empty string', () => {
    const asc = sortTransactions(rows, 'category', 'asc').map((r) => r.id)
    // null category ('') sorts before any named category
    expect(asc[0]).toBe(3)
  })

  it('does not mutate the input array', () => {
    const copy = [...rows]
    sortTransactions(rows, 'date', 'asc')
    expect(rows).toEqual(copy)
  })
})
