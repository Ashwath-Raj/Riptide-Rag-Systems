import type { ChunkDetail, Health, QueryResponse, Score } from '../types/api'

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(path, init)
  const payload: unknown = await response.json().catch(() => null)
  if (!response.ok) {
    const body = payload as { message?: string; detail?: string; reason?: string } | null
    throw new Error(body?.message || body?.detail || body?.reason || `Request failed (${response.status})`)
  }
  return payload as T
}

export const api = {
  health: () => request<Health>('/api/health'),
  score: (query: string) => request<Score>('/api/query/score', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ query }) }),
  query: (query: string, source: 'voice' | 'typed') => request<QueryResponse>('/api/query', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ query, source }) }),
  transcribe: (audio: Blob) => { const form = new FormData(); form.append('audio', audio, 'recording.webm'); return request<{ transcript: string; duration_ms: number; provider: string }>('/api/transcribe', { method: 'POST', body: form }) },
  chunk: (id: string) => request<ChunkDetail>(`/api/chunks/${encodeURIComponent(id)}`),
}
