from sqlmodel import Session
from app.db.database import engine
from app.services.investigation.rag import RAGKnowledgeService


def test_rag_knowledge_search():
    with Session(engine) as session:
        rag = RAGKnowledgeService(session)

        # 1. Search Runbooks for database pool exhaustion
        rb_results = rag.search_runbooks("connection pool exhausted QueuePool timeout", service="payment-api")
        assert len(rb_results) >= 1
        top_rb = rb_results[0]
        assert "Database Connection Pool" in top_rb["title"]
        assert top_rb["relevance_score"] > 0.3

        # 2. Search Past Incidents
        past_results = rag.search_past_incidents("connection leak", service="payment-api")
        assert len(past_results) >= 1
        assert "payment-api" in past_results[0]["service"]

        # 3. Unified Search
        unified = rag.unified_search("OutOfMemoryError memory leak order buffer", service="order-service")
        assert len(unified["runbooks"]) >= 1
