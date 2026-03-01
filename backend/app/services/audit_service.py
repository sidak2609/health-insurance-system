import json
from sqlalchemy.orm import Session
from app.db.models import AuditLog


def log_action(
    db: Session,
    action: str,
    user_id: int = None,
    entity_type: str = None,
    entity_id: int = None,
    details: dict = None,
):
    audit = AuditLog(
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        details=json.dumps(details or {}),
    )
    db.add(audit)
    db.commit()
