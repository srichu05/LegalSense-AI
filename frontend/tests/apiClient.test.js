import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import {
  getBaseUrl,
  setBaseUrl,
  resetBaseUrl,
  normalizeUrl,
  ApiException,
  checkHealth,
  analyzeText,
  analyzeDocument,
  searchCorpus,
} from '../src/lib/api/client'

describe('API Client & URL Configuration', () => {
  beforeEach(() => {
    localStorage.clear()
    vi.restoreAllMocks()
  })

  it('normalizes base URLs by stripping trailing slashes and whitespace', () => {
    expect(normalizeUrl('  http://127.0.0.1:5000/// ')).toBe('http://127.0.0.1:5000')
    expect(normalizeUrl('https://api.example.com/')).toBe('https://api.example.com')
    expect(normalizeUrl('')).toBe('http://127.0.0.1:5000')
  })

  it('persists and retrieves custom base URL in localStorage', () => {
    setBaseUrl('https://custom-service.onrender.com')
    expect(getBaseUrl()).toBe('https://custom-service.onrender.com')
    resetBaseUrl()
    expect(getBaseUrl()).toBe('http://127.0.0.1:5000')
  })

  it('validates text input prior to network request in analyzeText', async () => {
    await expect(analyzeText('')).rejects.toThrow(ApiException)
    await expect(analyzeText('   ')).rejects.toThrow(/cannot be empty/)
    await expect(analyzeText('A'.repeat(50001))).rejects.toThrow(/exceeds maximum allowed length/)
  })

  it('validates document upload parameters in analyzeDocument', async () => {
    await expect(analyzeDocument(null)).rejects.toThrow(/select a file/)

    const invalidFile = new File(['text'], 'test.docx', { type: 'application/docx' })
    await expect(analyzeDocument(invalidFile)).rejects.toThrow(/Unsupported file type/)

    const hugeFile = new File([new ArrayBuffer(11 * 1024 * 1024)], 'huge.txt', { type: 'text/plain' })
    await expect(analyzeDocument(hugeFile)).rejects.toThrow(/exceeds maximum upload size/)
  })

  it('validates search query and top_k bounds in searchCorpus', async () => {
    await expect(searchCorpus('')).rejects.toThrow(/Search query cannot be empty/)
    await expect(searchCorpus('valid', 0)).rejects.toThrow(/top_k must be an integer/)
    await expect(searchCorpus('valid', 101)).rejects.toThrow(/top_k must be an integer/)
  })

  it('executes checkHealth against /health successfully', async () => {
    const mockHealth = {
      status: 'ok',
      service: 'legalsense-api',
      wsd_ready: true,
      llm_enabled: false,
    }

    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      headers: new Headers({ 'content-type': 'application/json' }),
      json: async () => mockHealth,
    })

    const data = await checkHealth()
    expect(data.status).toBe('ok')
    expect(data.wsd_ready).toBe(true)
    expect(global.fetch).toHaveBeenCalledWith(
      expect.stringContaining('/health'),
      expect.objectContaining({ method: 'GET' })
    )
  })

  it('handles backend error responses and maps to ApiException with code and status', async () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: false,
      status: 400,
      headers: new Headers({ 'content-type': 'application/json' }),
      json: async () => ({
        error: {
          code: 'INVALID_TARGET_WORD',
          message: 'Target word cannot be empty.',
        },
      }),
    })

    await expect(analyzeText('Valid sentence', '  ')).rejects.toThrow(ApiException)
  })

  it('handles network failure and returns descriptive message', async () => {
    global.fetch = vi.fn().mockRejectedValue(new Error('Failed to fetch'))

    await expect(checkHealth()).rejects.toThrow(/Failed to connect to backend server/)
  })
})
