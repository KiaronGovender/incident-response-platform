import re
from typing import Dict, Any, List, Optional
from sqlmodel import Session, select

from app.models.knowledge import Runbook, PastIncident


def calculate_relevance(query: str, text: str, tags: List[str] = None) -> float:
    """Calculates relevance score using token matching, n-gram overlap, and tag boosts."""
    query_tokens = set(re.findall(r"\w+", query.lower()))
    if not query_tokens:
        return 0.0

    text_tokens = set(re.findall(r"\w+", text.lower()))
    overlap = query_tokens.intersection(text_tokens)
    base_score = len(overlap) / len(query_tokens)

    # Tag boost
    tag_boost = 0.0
    if tags:
        for t in tags:
            if t.lower() in query_tokens:
                tag_boost += 0.25

    return min(1.0, base_score + tag_boost)


class RAGKnowledgeService:
    def __init__(self, session: Session):
        self.session = session

    def search_runbooks(self, query: str, service: Optional[str] = None, top_k: int = 3) -> List[Dict[str, Any]]:
        runbooks = self.session.exec(select(Runbook)).all()
        scored = []

        for rb in runbooks:
            # Score against title, content, and trigger patterns
            combined_text = f"{rb.title} {rb.content} {' '.join(rb.trigger_patterns)}"
            score = calculate_relevance(query, combined_text, rb.tags)

            # Bonus for matching service
            if service and rb.service.lower() in [service.lower(), "general"]:
                score = min(1.0, score + 0.15)

            if score > 0.1:
                scored.append((score, rb))

        scored.sort(key=lambda x: x[0], reverse=True)
        results = []
        for score, rb in scored[:top_k]:
            results.append({
                "id": rb.id,
                "title": rb.title,
                "service": rb.service,
                "relevance_score": round(score, 3),
                "remediation_actions": rb.remediation_actions,
                "diagnosis_steps": rb.diagnosis_steps,
                "risk_level": rb.risk_level,
                "content_preview": rb.content[:300] + "...",
            })

        return results

    def search_past_incidents(self, query: str, service: Optional[str] = None, top_k: int = 2) -> List[Dict[str, Any]]:
        past_incidents = self.session.exec(select(PastIncident)).all()
        scored = []

        for pi in past_incidents:
            combined_text = f"{pi.title} {pi.root_cause} {pi.resolution} {' '.join(pi.symptoms)}"
            score = calculate_relevance(query, combined_text)

            if service and pi.service.lower() == service.lower():
                score = min(1.0, score + 0.2)

            if score > 0.1:
                scored.append((score, pi))

        scored.sort(key=lambda x: x[0], reverse=True)
        results = []
        for score, pi in scored[:top_k]:
            results.append({
                "id": pi.id,
                "title": pi.title,
                "service": pi.service,
                "relevance_score": round(score, 3),
                "root_cause": pi.root_cause,
                "resolution": pi.resolution,
                "symptoms": pi.symptoms,
                "postmortem_url": pi.postmortem_url,
            })

        return results

    def unified_search(self, query: str, service: Optional[str] = None) -> Dict[str, Any]:
        return {
            "query": query,
            "service": service,
            "runbooks": self.search_runbooks(query, service),
            "past_incidents": self.search_past_incidents(query, service),
        }
