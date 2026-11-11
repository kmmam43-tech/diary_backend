import asyncio
from datetime import datetime, timezone
from typing import Protocol

from app.models import CaseCreateRequest, CaseCreateResponse


class CaseRepository(Protocol):
    async def create(self, case: CaseCreateRequest) -> CaseCreateResponse: ...


class FirestoreCaseRepository:
    def __init__(self, project_id: str, collection: str) -> None:
        self.project_id = project_id or None
        self.collection = collection

    def _create_sync(self, case: CaseCreateRequest) -> CaseCreateResponse:
        import firebase_admin
        from firebase_admin import firestore

        if not firebase_admin._apps:
            options = {"projectId": self.project_id} if self.project_id else None
            firebase_admin.initialize_app(options=options)

        client = firestore.client()
        document = client.collection(self.collection).document()
        created_at = datetime.now(timezone.utc)
        document.set(
            {
                "challenge_behavior": case.challenge_behavior,
                "intervention": case.intervention,
                "messages": [message.model_dump() for message in case.messages],
                "created_at": created_at,
            }
        )
        return CaseCreateResponse(id=document.id, created_at=created_at)

    async def create(self, case: CaseCreateRequest) -> CaseCreateResponse:
        return await asyncio.to_thread(self._create_sync, case)
