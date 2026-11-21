import { expect, it } from 'vitest'
import { formatDate, seriesLabel } from './books.js'

it('seriesLabel doda stevilko v seriji, ce jo ima', () => {
  expect(seriesLabel('Mistborn', 1)).toBe('Mistborn #1')
  expect(seriesLabel('Mistborn', null)).toBe('Mistborn')
  expect(seriesLabel(null, 1)).toBeNull()
})

it('formatDate prikaze datum brez pretvorbe v UTC', () => {
  expect(formatDate('2026-11-08')).toBe('8 Nov 2026')
  expect(formatDate(null)).toBeNull()
})
