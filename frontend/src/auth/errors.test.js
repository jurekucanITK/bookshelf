import { expect, it, vi } from 'vitest'
import { ApiError } from '../api.js'
import { authErrorMessage } from './errors.js'

vi.mock('../firebase.js', () => ({ auth: {} }))

it('authErrorMessage prevede napake Firebase in backenda', () => {
  expect(authErrorMessage({ code: 'auth/invalid-email' })).toBe('Invalid email address.')
  expect(authErrorMessage({ code: 'auth/unknown' })).toBe('Something went wrong. Please try again.')
  expect(authErrorMessage(new ApiError(422, [{ msg: 'invalid' }]))).toMatch(/^Username must be 3–30/)
  expect(authErrorMessage(new ApiError(409, 'Username is already taken'))).toBe(
    'Username is already taken',
  )
})
