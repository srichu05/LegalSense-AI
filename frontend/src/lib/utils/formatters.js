/**
 * Format bytes into human-readable string (KB, MB, etc.).
 */
export function formatBytes(bytes, decimals = 1) {
  if (!bytes || bytes === 0) return '0 B'
  const k = 1024
  const dm = decimals < 0 ? 0 : decimals
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(dm))} ${sizes[i]}`
}

/**
 * Format algorithmic relevance score (4 decimals).
 */
export function formatScore(score) {
  if (typeof score !== 'number' || isNaN(score)) return '0.0000'
  return score.toFixed(4)
}

/**
 * Clean and format WordNet synset ID for readable badges.
 */
export function formatSynsetId(synsetId) {
  if (!synsetId) return 'None'
  return synsetId.replace(/\.(n|v|a|r)\./, ' ($1) ')
}

/**
 * Truncate long text strings cleanly at word boundaries.
 */
export function truncate(text, maxLength = 120) {
  if (!text || text.length <= maxLength) return text || ''
  return text.slice(0, maxLength).trim() + '...'
}
