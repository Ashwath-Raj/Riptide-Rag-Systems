from __future__ import annotations

from dataclasses import dataclass
import time
import uuid

from app.core.config import Settings
from app.core.errors import (
    GenerationUnavailable,
    PrivacyGateUnavailable,
    RetrievalUnavailable,
    SecurityGateUnavailable,
)
from app.core.logging import get_logger
from app.schemas.query import QuerySecurity
from app.schemas.retrieval import RetrievalHit, RetrievalStats
from app.schemas.response import QueryResponse
from app.schemas.security import Citation, EvidenceItem, PipelineStage, PrivacyResult
from app.services.corpus import load_corpus_status
from app.services.embeddings import EmbeddingProvider, build_embedding_provider
from app.services.evidence import EvidenceValidator
from app.services.generation import LLMProvider, UnavailableLLM, build_llm_provider, build_prompt
from app.services.injection_guard import InjectionClassifier, LocalInjectionClassifier
from app.services.policy import SecurityPolicy
from app.services.privacy_guard import PrivacyGuard
from app.services.retrieval import Retriever, load_index_status, load_retriever
from app.services.trust import SessionTrust

log = get_logger("riptide.runtime")


@dataclass
class Runtime:
    settings: Settings
    classifier: InjectionClassifier
    embeddings: EmbeddingProvider | None
    embedding_status: str
    embedding_model: str
    retriever: Retriever | None
    llm: LLMProvider
    policy: SecurityPolicy
    privacy: PrivacyGuard
    evidence: EvidenceValidator
    session: SessionTrust

    def refresh_retriever(self) -> None:
        if self.embeddings is None:
            self.retriever = None
            return
        if hasattr(self.embeddings, "reload"):
            self.embeddings.reload()
            self.embedding_status = "ready" if getattr(self.embeddings, "_vectorizer", None) is not None else "waiting"
        self.retriever = load_retriever(self.settings.index_dir, self.embeddings.embed_text)

    def health(self) -> dict:
        corpus = load_corpus_status(self.settings)
        index = load_index_status(self.settings.index_dir)
        dataset_status = "waiting" if corpus.get("status") != "ready" else "ready"
        retrieval_status = "ready" if self.retriever is not None and index.get("status") == "ready" else "waiting"
        classifier_status = "ready" if self.classifier.available else "unavailable"
        llm_status = "ready" if self.llm.available else "unavailable"
        embedding_status = self.embedding_status
        app = "ready"
        overall = "ok"
        if classifier_status != "ready" or dataset_status != "ready" or retrieval_status != "ready" or llm_status != "ready":
            overall = "degraded"
        emails = int(corpus.get("emails") or 0)
        dataset = corpus.get("dataset") if isinstance(corpus.get("dataset"), dict) else {}
        source_emails = int(corpus.get("source_emails") or sum(
            int(item.get("row_count") or 0)
            for item in dataset.get("csv_files", [])
            if item.get("complete")
        ) or emails)
        indexed_emails = int(index.get("emails") or 0) if retrieval_status == "ready" else 0
        return {
            "status": overall,
            "app": app,
            "corpus_emails": emails,
            "source_emails": source_emails,
            "indexed_email_count": indexed_emails,
            "chunk_count": int(index.get("chunks") or 0) if retrieval_status == "ready" else 0,
            "index_status": index.get("status", "waiting") if retrieval_status == "ready" else "waiting",
            "index_ready": retrieval_status == "ready",
            "classifier_ready": classifier_status == "ready",
            "llm_ready": llm_status == "ready",
            "embedding_ready": embedding_status == "ready",
            "dataset": {
                "status": dataset_status,
                "emails": emails,
                "detail": corpus.get("reason") or ("WAITING FOR CORPUS" if dataset_status == "waiting" else None),
            },
            "embedding": {"status": embedding_status, "model": self.embedding_model},
            "classifier": {
                "status": classifier_status,
                "model": getattr(self.classifier, "model_name", None),
                "detail": None if classifier_status == "ready" else "SECURITY MODEL UNAVAILABLE",
            },
            "llm": {
                "status": llm_status,
                "model": self.llm.model_name,
                "detail": None if llm_status == "ready" else "NOT CONFIGURED",
            },
            "retrieval": {
                "status": retrieval_status,
                "detail": None if retrieval_status == "ready" else "VECTOR INDEX NOT BUILT",
            },
            "voice": {"status": "ready" if self.settings.whisper_ready else "unavailable", "model": self.settings.whisper_model},
            "privacy": {"status": "ready", "model": "regex"},
        }

    def run_query(self, query: str, source: str) -> QueryResponse:
        request_id = f"req-{uuid.uuid4().hex[:10]}"
        started = time.perf_counter()
        stages: list[PipelineStage] = [
            PipelineStage(id="stt", label="STT", state="COMPLETE" if source == "voice" else "TYPED", duration_ms=0),
            PipelineStage(id="query_guard", label="QUERY GUARD", state="PENDING"),
            PipelineStage(id="retrieval", label="RETRIEVAL", state="PENDING"),
            PipelineStage(id="chunk_guard", label="CHUNK GUARD", state="PENDING"),
            PipelineStage(id="output_gate", label="OUTPUT GATE", state="PENDING"),
        ]
        if not self.classifier.available:
            self.session.register_high_risk()
            return self._closed(
                request_id,
                query,
                source,
                stages,
                reason="security_gate_unavailable",
                started=started,
            )
        try:
            qscore = self.classifier.score(query)
        except SecurityGateUnavailable:
            return self._closed(
                request_id, query, source, stages, reason="security_gate_unavailable", started=started
            )
        decision = self.policy.evaluate_query(qscore.score)
        stages[1] = PipelineStage(
            id="query_guard",
            label="QUERY GUARD",
            state=decision,
            duration_ms=qscore.latency_ms,
            risk=qscore.score,
        )
        query_security = QuerySecurity(
            risk_score=qscore.score,
            decision=decision.lower(),
            label=qscore.label,
            model=qscore.model,
            latency_ms=qscore.latency_ms,
        )
        if self.policy.query_blocks(decision):
            self.session.register_high_risk()
            if self.session.high_risk_queries > 1:
                self.session.register_repeated_probe()
            total = int((time.perf_counter() - started) * 1000)
            return QueryResponse(
                request_id=request_id,
                status="blocked",
                transcript=query,
                query_security=query_security,
                reason="query_injection_detected",
                risk_score=qscore.score,
                llm_called=False,
                source=source,
                pipeline=stages,
                trace=_trace(request_id, total, qscore.latency_ms, 0, 0, 0, 0, 0, 0, 0),
            )
        if self.retriever is None:
            stages[2] = PipelineStage(id="retrieval", label="RETRIEVAL", state="UNAVAILABLE")
            return self._refused(
                request_id,
                query,
                source,
                stages,
                query_security,
                "retrieval_unavailable",
                started,
                qscore.latency_ms,
            )
        t_ret = time.perf_counter()
        hits = self.retriever.search(query, self.settings.top_k)
        retrieval_ms = int((time.perf_counter() - t_ret) * 1000)
        stages[2] = PipelineStage(
            id="retrieval",
            label="RETRIEVAL",
            state=f"{len(hits)} CANDIDATES",
            duration_ms=retrieval_ms,
            count_label=str(len(hits)),
        )
        if not hits:
            return self._refused(
                request_id,
                query,
                source,
                stages,
                query_security,
                "insufficient_safe_evidence",
                started,
                qscore.latency_ms,
                retrieval_ms,
            )
        t_chunk = time.perf_counter()
        safe: list[RetrievalHit] = []
        evidence_rows: list[EvidenceItem] = []
        quarantined = 0
        chunk_ms_acc = 0
        try:
            for hit in hits:
                cscore = self.classifier.score(hit.text)
                chunk_ms_acc += cscore.latency_ms
                cdec = self.policy.evaluate_chunk(cscore.score)
                blocked = self.policy.chunk_quarantines(cdec)
                if blocked:
                    quarantined += 1
                else:
                    safe.append(hit)
                evidence_rows.append(
                    EvidenceItem(
                        email_id=hit.email_id,
                        chunk_id=hit.chunk_id,
                        parent_id=str(hit.metadata.get("parent_id") or hit.email_id),
                        section=hit.metadata.get("section"),
                        title=_title(hit),
                        preview=self.privacy.redact_preview(hit.text),
                        decision="QUARANTINED" if blocked else cdec,
                        injection_score=cscore.score,
                        boundary_reason=hit.metadata.get("boundary_reason"),
                        char_count=hit.metadata.get("char_count"),
                        token_estimate=hit.metadata.get("token_estimate"),
                        quarantined=blocked,
                    )
                )
        except SecurityGateUnavailable:
            return self._closed(
                request_id, query, source, stages, reason="security_gate_unavailable", started=started
            )
        chunk_ms = int((time.perf_counter() - t_chunk) * 1000)
        stages[3] = PipelineStage(
            id="chunk_guard",
            label="CHUNK GUARD",
            state=f"{len(safe)} SAFE / {quarantined} QUARANTINED",
            duration_ms=chunk_ms,
            count_label=f"{len(safe)}/{quarantined}",
        )
        retrieval_stats = RetrievalStats(
            candidate_count=len(hits),
            quarantined_count=quarantined,
            safe_count=len(safe),
            latency_ms=retrieval_ms,
        )
        if not safe:
            return QueryResponse(
                request_id=request_id,
                status="refused",
                transcript=query,
                query_security=query_security,
                retrieval=retrieval_stats,
                evidence=evidence_rows,
                reason="insufficient_safe_evidence",
                llm_called=False,
                source=source,
                pipeline=stages,
                answer="I couldn't safely answer that from the available evidence.",
                trace=_trace(
                    request_id,
                    int((time.perf_counter() - started) * 1000),
                    qscore.latency_ms,
                    retrieval_ms,
                    chunk_ms_acc,
                    0,
                    0,
                    len(hits),
                    quarantined,
                    0,
                ),
            )
        if not self.llm.available:
            stages[4] = PipelineStage(id="output_gate", label="OUTPUT GATE", state="LLM UNAVAILABLE")
            return QueryResponse(
                request_id=request_id,
                status="refused",
                transcript=query,
                query_security=query_security,
                retrieval=retrieval_stats,
                evidence=evidence_rows,
                reason="generation_unavailable",
                llm_called=False,
                source=source,
                pipeline=stages,
                trace=_trace(
                    request_id,
                    int((time.perf_counter() - started) * 1000),
                    qscore.latency_ms,
                    retrieval_ms,
                    chunk_ms_acc,
                    0,
                    0,
                    len(hits),
                    quarantined,
                    0,
                ),
            )
        prompt = build_prompt(query, safe)
        t_gen = time.perf_counter()
        try:
            raw_answer = self.llm.generate(prompt["system"], prompt["user"])
        except GenerationUnavailable:
            return QueryResponse(
                request_id=request_id,
                status="refused",
                transcript=query,
                query_security=query_security,
                retrieval=retrieval_stats,
                evidence=evidence_rows,
                reason="generation_unavailable",
                llm_called=False,
                source=source,
                pipeline=stages,
            )
        gen_ms = int((time.perf_counter() - t_gen) * 1000)
        verdict = self.evidence.validate(raw_answer, safe)
        if verdict == "INSUFFICIENT":
            stages[4] = PipelineStage(id="output_gate", label="OUTPUT GATE", state="REFUSED")
            return QueryResponse(
                request_id=request_id,
                status="refused",
                transcript=query,
                query_security=query_security,
                retrieval=retrieval_stats,
                evidence=evidence_rows,
                reason="insufficient_safe_evidence",
                llm_called=True,
                grounded=False,
                source=source,
                pipeline=stages,
                answer="I couldn't safely answer that from the available evidence.",
                trace=_trace(
                    request_id,
                    int((time.perf_counter() - started) * 1000),
                    qscore.latency_ms,
                    retrieval_ms,
                    chunk_ms_acc,
                    gen_ms,
                    0,
                    len(hits),
                    quarantined,
                    0,
                ),
            )
        t_pii = time.perf_counter()
        try:
            privacy = self.privacy.redact(raw_answer)
        except PrivacyGateUnavailable:
            return QueryResponse(
                request_id=request_id,
                status="refused",
                transcript=query,
                query_security=query_security,
                retrieval=retrieval_stats,
                evidence=evidence_rows,
                reason="privacy_gate_unavailable",
                llm_called=True,
                source=source,
                pipeline=stages,
            )
        pii_ms = int((time.perf_counter() - t_pii) * 1000)
        stages[4] = PipelineStage(
            id="output_gate",
            label="OUTPUT GATE",
            state=f"{privacy.redaction_count} PII REDACTIONS",
            duration_ms=pii_ms,
            count_label=str(privacy.redaction_count),
        )
        citations = [Citation(email_id=hit.email_id, chunk_id=hit.chunk_id) for hit in safe]
        total = int((time.perf_counter() - started) * 1000)
        return QueryResponse(
            request_id=request_id,
            status="ok",
            transcript=query,
            query_security=query_security,
            retrieval=retrieval_stats,
            answer=privacy.sanitized_text,
            citations=citations,
            privacy=privacy,
            evidence=evidence_rows,
            pipeline=stages,
            llm_called=True,
            grounded=True,
            source=source,
            trace=_trace(
                request_id,
                total,
                qscore.latency_ms,
                retrieval_ms,
                chunk_ms_acc,
                gen_ms,
                pii_ms,
                len(hits),
                quarantined,
                privacy.redaction_count,
            ),
        )

    def _closed(self, request_id, query, source, stages, reason, started) -> QueryResponse:
        stages[1] = PipelineStage(id="query_guard", label="QUERY GUARD", state="UNAVAILABLE")
        return QueryResponse(
            request_id=request_id,
            status="refused",
            transcript=query,
            reason=reason,
            llm_called=False,
            source=source,
            pipeline=stages,
            trace={"request_id": request_id, "total_ms": int((time.perf_counter() - started) * 1000)},
        )

    def _refused(self, request_id, query, source, stages, query_security, reason, started, q_ms=0, r_ms=0) -> QueryResponse:
        return QueryResponse(
            request_id=request_id,
            status="refused",
            transcript=query,
            query_security=query_security,
            reason=reason,
            llm_called=False,
            source=source,
            pipeline=stages,
            answer="I couldn't safely answer that from the available evidence."
            if reason == "insufficient_safe_evidence"
            else None,
            trace=_trace(
                request_id,
                int((time.perf_counter() - started) * 1000),
                q_ms,
                r_ms,
                0,
                0,
                0,
                0,
                0,
                0,
            ),
        )


def _title(hit: RetrievalHit) -> str:
    meta = hit.metadata.get("source_metadata") or {}
    subject = meta.get("subject")
    if subject:
        return str(subject)
    preview = hit.text.strip().split("\n")[0][:80]
    return preview or "Untitled evidence"


def _trace(request_id, total, q, r, c, g, p, cand, quar, red):
    return {
        "request_id": request_id,
        "total_latency_ms": total,
        "stt_latency_ms": 0,
        "query_classifier_latency_ms": q,
        "retrieval_latency_ms": r,
        "chunk_classifier_latency_ms": c,
        "generation_latency_ms": g,
        "privacy_scan_latency_ms": p,
        "candidate_count": cand,
        "quarantined_count": quar,
        "final_redaction_count": red,
    }


def create_runtime(settings: Settings) -> Runtime:
    classifier = LocalInjectionClassifier(settings)
    embeddings, embedding_status, embedding_model = build_embedding_provider(settings)
    retriever = None
    if embeddings is not None:
        retriever = load_retriever(settings.index_dir, embeddings.embed_text)
    runtime = Runtime(
        settings=settings,
        classifier=classifier,
        embeddings=embeddings,
        embedding_status=embedding_status,
        embedding_model=embedding_model,
        retriever=retriever,
        llm=build_llm_provider(settings),
        policy=SecurityPolicy(settings),
        privacy=PrivacyGuard(),
        evidence=EvidenceValidator(),
        session=SessionTrust(),
    )
    log.info(
        "runtime_started classifier=%s embedding=%s llm=%s retriever=%s",
        classifier.available,
        embedding_status,
        runtime.llm.available,
        runtime.retriever is not None,
    )
    return runtime
