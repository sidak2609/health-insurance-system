import os

from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from sqlalchemy.orm import Session

from app.rag.embeddings import get_embeddings
from app.db.models import PolicySection, Policy

VECTOR_STORE_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "vector_store")

_vector_store = None


def build_documents_from_db(db: Session) -> list[Document]:
    sections = db.query(PolicySection).join(Policy).filter(Policy.is_active == True).all()
    documents = []
    for section in sections:
        policy = section.policy
        doc = Document(
            page_content=section.section_content,
            metadata={
                "policy_id": policy.id,
                "policy_name": policy.name,
                "plan_type": policy.plan_type,
                "section_id": section.id,
                "section_title": section.section_title,
                "section_number": section.section_number,
                "keywords": section.keywords or "[]",
            },
        )
        documents.append(doc)
    return documents


def build_vector_store(db: Session) -> FAISS:
    global _vector_store
    documents = build_documents_from_db(db)
    if not documents:
        raise ValueError("No policy sections found to index.")
    embeddings = get_embeddings()
    _vector_store = FAISS.from_documents(documents, embeddings)
    _vector_store.save_local(VECTOR_STORE_PATH)
    print(f"Built vector store with {len(documents)} documents at {VECTOR_STORE_PATH}")
    return _vector_store


def load_vector_store() -> FAISS:
    global _vector_store
    embeddings = get_embeddings()
    _vector_store = FAISS.load_local(VECTOR_STORE_PATH, embeddings, allow_dangerous_deserialization=True)
    return _vector_store


def get_vector_store() -> FAISS:
    global _vector_store
    if _vector_store is None:
        _vector_store = load_vector_store()
    return _vector_store


def add_document_to_store(section_content: str, metadata: dict):
    global _vector_store
    if _vector_store is None:
        return
    doc = Document(page_content=section_content, metadata=metadata)
    _vector_store.add_documents([doc])
    _vector_store.save_local(VECTOR_STORE_PATH)
