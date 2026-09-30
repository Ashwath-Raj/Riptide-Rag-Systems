import type { PipelineStage, QueryState } from '../types/api'
import { stages } from '../lib/format'

const stageIds = ['stt', 'query_guard', 'retrieval', 'chunk_guard', 'output_gate']
const fallback: Record<QueryState, number> = { IDLE: -1, LISTENING: 0, TRANSCRIBING: 0, QUERY_SCORING: 1, RETRIEVING: 2, CHUNK_SCORING: 3, GENERATING: 4, VALIDATING: 4, REDACTING: 4, COMPLETE: 4, BLOCKED: 1, REFUSED: 4, ERROR: -1 }
export function Pipeline({ state, data = [] }: { state: QueryState; data?: PipelineStage[] }) {
  const getStage = (id: string) => data.find(item => item.id.toLowerCase().replace(/-/g, '_') === id || item.label.toLowerCase().replace(/ /g, '_') === id)
  return <section className="panel pipeline-panel"><div className="section-heading"><div><span className="eyebrow">TRUST PIPELINE</span><h2>Every boundary is inspected</h2></div><span className="mono muted">5 GATES</span></div><div className="pipeline">
    {stages.map((name, i) => { const item = getStage(stageIds[i]); const current = fallback[state]; const finished = state === 'COMPLETE' || i < current || Boolean(item && /complete|allow|safe|pass/i.test(item.state)); const blocked = (state === 'BLOCKED' && i === 1) || Boolean(item && /block|quarantine|refus|error/i.test(item.state)); const active = current === i && !finished && !blocked
      return <div className={`pipe-stage ${finished ? 'done' : ''} ${active ? 'active' : ''} ${blocked ? 'blocked' : ''}`} key={name}><div className="pipe-top"><span className="pipe-node">{finished ? '✓' : blocked ? '!' : String(i + 1).padStart(2, '0')}</span><span className="pipe-state">{item?.state || (blocked ? 'BLOCKED' : finished ? 'COMPLETE' : active ? 'IN PROGRESS' : 'WAITING')}</span></div><strong>{name}</strong><span className="pipe-meta">{item?.duration_ms != null ? `${item.duration_ms} ms` : item?.count_label || (i === 1 && state === 'BLOCKED' ? 'LLM not called' : '—')}{item?.risk != null ? ` · ${item.risk.toFixed(2)}` : ''}</span></div>
    })}
  </div></section>
}
