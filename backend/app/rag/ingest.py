import json
import re

from sqlalchemy.orm import Session

from app.db.models import PolicySection, Policy


class SimpleDoc:
    """Lightweight document with page_content and metadata — replaces LangChain Document."""
    def __init__(self, page_content: str, metadata: dict):
        self.page_content = page_content
        self.metadata = metadata


def keyword_search(db: Session, query: str, k: int = 8) -> list[SimpleDoc]:
    """
    DB-based keyword search over policy sections.
    Scores each section by word frequency in content, title, and keyword tags.
    No ML models or embeddings required — runs in ~1MB RAM.
    """
    query_words = set(re.findall(r'\b\w{3,}\b', query.lower()))

    sections = (
        db.query(PolicySection)
        .join(Policy)
        .filter(Policy.is_active == True)
        .all()
    )

    if not sections:
        return []

    # If no meaningful query words, return first k sections
    if not query_words:
        return [
            SimpleDoc(
                page_content=s.section_content,
                metadata={
                    "policy_id": s.policy_id,
                    "policy_name": s.policy.name,
                    "section_title": s.section_title,
                    "section_number": s.section_number,
                },
            )
            for s in sections[:k]
        ]

    scored = []
    for section in sections:
        score = 0
        content_lower = section.section_content.lower()
        title_lower = section.section_title.lower()
        try:
            keywords = json.loads(section.keywords or "[]")
        except Exception:
            keywords = []

        for word in query_words:
            score += content_lower.count(word)
            if word in title_lower:
                score += 5  # title match weighted higher
            if any(word in kw.lower() for kw in keywords):
                score += 3  # keyword tag match

        if score > 0:
            scored.append((score, section))

    scored.sort(key=lambda x: x[0], reverse=True)

    results = []
    for _, section in scored[:k]:
        results.append(SimpleDoc(
            page_content=section.section_content,
            metadata={
                "policy_id": section.policy_id,
                "policy_name": section.policy.name,
                "section_title": section.section_title,
                "section_number": section.section_number,
            },
        ))
    return results
