import type { Decision, QueryState } from '../types/api'
export const formatScore = (score?: number | null) => score == null ? '—' : score.toFixed(2)
export const statusClass = (value?: string | null) => {
  const normalized = value?.toUpperCase() || ''
  return normalized.includes('BLOCK') || normalized.includes('QUARANTINE') || normalized.includes('ERROR') || normalized.includes('REFUS') ? 'danger' : normalized.includes('REVIEW') || normalized.includes('WARN') ? 'caution' : normalized.includes('ALLOW') || normalized.includes('SAFE') || normalized.includes('OK') || normalized.includes('COMPLETE') || normalized.includes('READY') ? 'safe' : 'neutral'
}
export const labelFor = (d?: Decision | null) => d?.toUpperCase() || 'NOT SCORED'
export const stages = ['STT', 'QUERY GUARD', 'RETRIEVAL', 'CHUNK GUARD', 'OUTPUT GATE']
export const stateLabel: Record<QueryState, string> = { IDLE: 'Ready for a query', LISTENING: 'Listening', TRANSCRIBING: 'Transcribing', QUERY_SCORING: 'Scoring query', RETRIEVING: 'Retrieving evidence', CHUNK_SCORING: 'Scoring chunks', GENERATING: 'Generating answer', VALIDATING: 'Validating answer', REDACTING: 'Applying privacy filter', COMPLETE: 'Complete', BLOCKED: 'Query blocked', REFUSED: 'Request refused', ERROR: 'Request failed' }
