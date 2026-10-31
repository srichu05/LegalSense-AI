/**
 * Centralized LegalSense API Client.
 *
 * Implements all endpoints per docs/API_SPEC.md:
 * - GET /health
 * - POST /api/v1/analyze
 * - POST /api/v1/documents/analyze
 * - POST /api/v1/search
 *
 * Provides runtime URL configuration, timeouts via AbortController,
 * structured ApiException mapping, and client-side pre-validation.
 */

const STORAGE_KEY_BASE_URL = 'legalsense_api_base_url'
export const DEFAULT_API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:5000'

export class ApiException extends Error {
  constructor(message, code = 'API_ERROR', status = 500, details = null) {
    super(message)
    this.name = 'ApiException'
    this.code = code
    this.status = status
    this.details = details
  }
}

/**
 * Get current configured API Base URL.
 */
export function getBaseUrl() {
  try {
    const saved = localStorage.getItem(STORAGE_KEY_BASE_URL)
    if (saved && saved.trim()) {
      return normalizeUrl(saved.trim())
    }
  } catch {
    // Fall back if localStorage is unavailable
  }
  return normalizeUrl(DEFAULT_API_BASE_URL)
}

/**
 * Update and persist API Base URL.
 */
export function setBaseUrl(url) {
  const normalized = normalizeUrl(url)
  try {
    localStorage.setItem(STORAGE_KEY_BASE_URL, normalized)
  } catch (err) {
    console.error('Failed to save API base URL to localStorage:', err)
  }
  return normalized
}

/**
 * Reset API Base URL to default.
 */
export function resetBaseUrl() {
  try {
    localStorage.removeItem(STORAGE_KEY_BASE_URL)
  } catch {
    // Ignore
  }
  return normalizeUrl(DEFAULT_API_BASE_URL)
}

/**
 * Normalize URL string (strip trailing slashes, trim whitespace).
 */
export function normalizeUrl(url) {
  if (!url || !url.trim()) return 'http://127.0.0.1:5000'
  let trimmed = url.trim()
  while (trimmed.endsWith('/')) {
    trimmed = trimmed.slice(0, -1)
  }
  return trimmed
}

/**
 * Execute an HTTP fetch request with timeout and error mapping.
 */
async function request(endpoint, options = {}, timeoutMs = 15000) {
  const baseUrl = getBaseUrl()
  const url = `${baseUrl}${endpoint.startsWith('/') ? endpoint : `/${endpoint}`}`

  const controller = new AbortController()
  const timeoutId = setTimeout(() => controller.abort(), timeoutMs)

  try {
    const response = await fetch(url, {
      ...options,
      signal: controller.signal,
    })

    clearTimeout(timeoutId)

    // Handle 204 No Content
    if (response.status === 204) {
      return null
    }

    let data
    const contentType = response.headers.get('content-type') || ''
    if (contentType.includes('application/json')) {
      try {
        data = await response.json()
      } catch (err) {
        throw new ApiException('Received malformed JSON from backend API.', 'MALFORMED_JSON', response.status)
      }
    } else {
      const text = await response.text()
      if (!response.ok) {
        throw new ApiException(text || `HTTP ${response.status} Error`, 'HTTP_ERROR', response.status)
      }
      return text
    }

    if (!response.ok) {
      const errorCode = data?.error?.code || 'HTTP_ERROR'
      const errorMessage = data?.error?.message || `Request failed with status ${response.status}`
      throw new ApiException(errorMessage, errorCode, response.status, data?.error)
    }

    return data
  } catch (error) {
    clearTimeout(timeoutId)
    if (error.name === 'AbortError') {
      throw new ApiException(`Request timed out after ${timeoutMs / 1000}s. Backend might be offline or busy.`, 'TIMEOUT', 408)
    }
    if (error instanceof ApiException) {
      throw error
    }
    throw new ApiException(
      `Failed to connect to backend server (${error.message || 'Network error'}). Ensure Flask is running.`,
      'NETWORK_FAILURE',
      0
    )
  }
}

/**
 * Check backend health status: GET /health
 */
export async function checkHealth(timeoutMs = 5000) {
  return request('/health', { method: 'GET' }, timeoutMs)
}

/**
 * Disambiguate text and target words: POST /api/v1/analyze
 */
export async function analyzeText(text, targetWord = null, useLlm = false, timeoutMs = 45000) {
  if (!text || typeof text !== 'string' || !text.trim()) {
    throw new ApiException("Field 'text' is required and cannot be empty.", 'MISSING_TEXT', 400)
  }
  if (text.length > 50000) {
    throw new ApiException("Text exceeds maximum allowed length of 50,000 characters.", 'TEXT_TOO_LONG', 400)
  }

  const payload = {
    text: text.trim(),
    use_llm: Boolean(useLlm),
  }
  if (targetWord && targetWord.trim()) {
    payload.target_word = targetWord.trim()
  }

  return request('/api/v1/analyze', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    },
    body: JSON.stringify(payload),
  }, timeoutMs)
}

/**
 * Analyze uploaded document (.txt or .pdf): POST /api/v1/documents/analyze
 */
export async function analyzeDocument(file, useLlm = false, timeoutMs = 45000) {
  if (!file) {
    throw new ApiException('Please select a file to upload.', 'MISSING_FILE', 400)
  }

  const maxBytes = 10 * 1024 * 1024 // 10 MB
  if (file.size > maxBytes) {
    throw new ApiException('File exceeds maximum upload size of 10 MB.', 'FILE_TOO_LARGE', 413)
  }

  const validExts = ['.txt', '.pdf']
  const filename = file.name || ''
  const hasValidExt = validExts.some(ext => filename.toLowerCase().endsWith(ext))
  if (!hasValidExt) {
    throw new ApiException('Unsupported file type. Only .txt and .pdf files are accepted.', 'UNSUPPORTED_FORMAT', 415)
  }

  const formData = new FormData()
  formData.append('file', file)
  formData.append('use_llm', useLlm ? 'true' : 'false')

  return request('/api/v1/documents/analyze', {
    method: 'POST',
    headers: {
      'Accept': 'application/json',
    },
    body: formData,
  }, timeoutMs)
}

/**
 * Search indexed corpus for relevant passages: POST /api/v1/search
 */
export async function searchCorpus(query, topK = 5, timeoutMs = 30000) {
  if (!query || typeof query !== 'string' || !query.trim()) {
    throw new ApiException("Search query cannot be empty.", 'MISSING_QUERY', 400)
  }

  const k = parseInt(topK, 10)
  if (isNaN(k) || k < 1 || k > 100) {
    throw new ApiException("top_k must be an integer between 1 and 100.", 'INVALID_TOP_K', 400)
  }

  const payload = {
    query: query.trim(),
    top_k: k,
  }

  return request('/api/v1/search', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    },
    body: JSON.stringify(payload),
  }, timeoutMs)
}
