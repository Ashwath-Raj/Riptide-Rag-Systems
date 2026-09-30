import { useEffect, useState } from 'react'
import { api } from '../api/client'
import type { ChunkDetail, Evidence } from '../types/api'
import { formatScore, labelFor, statusClass } from '../lib/format'

export function Inspector({ item, onClose }: { item: Evidence | null; onClose: () => void }) {
  const [detail, setDetail] = useState<ChunkDetail | null>(null); const [error, setError] = useState(''); const [loading, setLoading] = useState(false)
  useEffect(() => { if (!item) { setDetail(null); setError(''); return }; let live = true; setLoading(true); setError(''); api.chunk(item.chunk_id).then(result => { if (live) setDetail(result) }).catch(e => { if (live) setError(e instanceof Error ? e.message : 'Chunk details unavailable.') }).finally(() => { if (live) setLoading(false) }); return () => { live = false } }, [item])
  useEffect(() => { if (!item) return; const key = (event: KeyboardEvent) => { if (event.key === 'Escape') onClose() }; window.addEventListener('keydown', key); return () => window.removeEventListener('keydown', key) }, [item, onClose])
  if (!item) return null
  const value = detail || item
  const metadata = detail?.metadata
  return <><button className="scrim" aria-label="Close inspector" onClick={onClose} /><aside className="inspector" aria-labelledby="inspector-title"><div className="inspector-header"><div><span className="eyebrow">SOURCE RECORD</span><h2 id="inspector-title">Chunk inspector</h2></div><button className="icon-button" aria-label="Close inspector" onClick={onClose}>×</button></div>{loading && <div className="inline-state">Loading chunk details…</div>}{error && <div className="inline-error">{error}</div>}<dl className="detail-grid"><dt>Email ID</dt><dd className="mono">{value.email_id}</dd><dt>Chunk ID</dt><dd className="mono break">{value.chunk_id}</dd><dt>Section</dt><dd>{value.section || 'Not supplied'}</dd><dt>Boundary</dt><dd>{value.boundary_reason || 'Not supplied'}</dd><dt>Size</dt><dd>{value.char_count != null ? `${value.char_count.toLocaleString()} characters` : 'Not supplied'}</dd><dt>Risk</dt><dd className="mono">{formatScore(value.injection_score)}</dd><dt>Decision</dt><dd><span className={`status ${statusClass(value.decision)}`}><i />{labelFor(value.decision)}</span></dd></dl><div className="preview-block"><div className="eyebrow">SANITIZED SOURCE PREVIEW</div><p>{value.preview || 'No preview supplied.'}</p></div>{metadata && Object.keys(metadata).length > 0 && <details className="metadata-details"><summary>Source metadata</summary><pre>{JSON.stringify(metadata, null, 2)}</pre></details>}</aside></>
}
