import { describe, expect, it } from 'vitest'
import { formatAmount, formatDate, formatMonth, isNegative, monthOverMonthChange } from './summary'

describe('formatAmount', () => {
  it('formats positive and negative decimal strings as BRL', () => {
    expect(formatAmount('1234.56')).toBe('R$ 1.234,56')
    expect(formatAmount('-99.90')).toBe('-R$ 99,90')
  })
})

describe('isNegative', () => {
  it('reads sign from a decimal string', () => {
    expect(isNegative('-10.00')).toBe(true)
    expect(isNegative('10.00')).toBe(false)
    expect(isNegative('0')).toBe(false)
  })
})

describe('formatDate', () => {
  it('formats an ISO date as day + short month in pt-BR', () => {
    // month is locale-short and can vary in punctuation across ICU versions,
    // so just check the day number is present and unambiguous.
    expect(formatDate('2026-04-13')).toMatch(/^13/)
  })
})

describe('formatMonth', () => {
  it('formats a YYYY-MM key as short month + 2-digit year', () => {
    expect(formatMonth('2026-04')).toMatch(/26$/)
  })
})

describe('monthOverMonthChange', () => {
  it('returns null with fewer than two months of history', () => {
    expect(monthOverMonthChange([])).toBeNull()
    expect(monthOverMonthChange([{ net: '100.00' }])).toBeNull()
  })

  it('computes percentage change between the last two cumulative balances', () => {
    // cumulative: 100 -> 150, a 50% increase
    const points = [{ net: '100.00' }, { net: '50.00' }]
    expect(monthOverMonthChange(points)).toBeCloseTo(50, 5)
  })

  it('hides the indicator when the previous balance is near zero', () => {
    // cumulative: -4.99 -> anything — base is within the |x| < 10 guard
    const points = [{ net: '-4.99' }, { net: '100.00' }]
    expect(monthOverMonthChange(points)).toBeNull()
  })
})
