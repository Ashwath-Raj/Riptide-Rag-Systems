import type { Evidence as EvidenceItem } from '../types/api'
import { formatScore, labelFor, statusClass } from '../lib/format'

export function Evidence({ items, onInspect }: { items: EvidenceItem[]; onInspect: (item: EvidenceItem) => void }) {
  return <section className="panel evidence-panel"><div className="section-heading"><div><span className="eyebrow">RETRIEVED RECORDS</span><h2>Evidence</h2></div><span className="count-tag">{items.length} {items.length === 1 ? 'RECORD' : 'RECORDS'}</span></div>
    {!items.length ? <div className="empty-state">Evidence will appear here after a query completes.</div> : <div className="evidence-list">{items.map(item => <article key={item.chunk_id} className={`evidence-row ${item.quarantined || /quarantine/i.test(item.decision) ? 'quarantined' : ''}`}><div className="record-icon" aria-hidden="true">▤</div><div className="evidence-main"><div className="evidence-title"><strong>{item.title || `Email ${item.email_id}`}</strong><code>{item.email_id}</code></div><p>{item.quarantined || /quarantine/i.test(item.decision) ? 'Content isolated by the chunk guard.' : item.preview || 'No preview provided by the API.'}</p><div className="evidence-meta"><span className={`status ${statusClass(item.decision)}`}><i />{labelFor(item.decision)}</span><span className="mono">RISK {formatScore(item.injection_score)}</span>{item.section && <span>{item.section}</span>}</div></div><button className="button secondary compact" onClick={() => onInspect(item)}>Inspect</button></article>)}</div>}
  </section>
}
