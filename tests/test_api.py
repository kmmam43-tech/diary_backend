from datetime import datetime, timezone

from fastapi.testclient import TestClient

from app.config import Settings
from app.main import create_app
from app.models import CaseCreateResponse, ConversationResponse


class FakeAgentService:
    def __init__(self) -> None:
        self.calls = []

    async def respond(self, challenge_behavior, messages):
        self.calls.append((challenge_behavior, messages))
        return ConversationResponse(
            assistant_message="언제 주로 발생하는지 알려주세요.",
            suggested_intervention="- 발생 전 환경을 확인합니다.",
        )


class FakeCaseRepository:
    def __init__(self) -> None:
        self.saved = []

    async def create(self, case):
        self.saved.append(case)
        return CaseCreateResponse(id="case-1", created_at=datetime(2026, 1, 1, tzinfo=timezone.utc))


def make_client():
    agents = FakeAgentService()
    repository = FakeCaseRepository()
    app = create_app(
        settings=Settings(cors_origins="http://localhost:8080"),
        agent_service=agents,
        case_repository=repository,
    )
    return TestClient(app), agents, repository


def test_health():
    client, _, _ = make_client()
    assert client.get("/health").json() == {"status": "ok"}


def test_conversation_calls_agent_service():
    client, agents, _ = make_client()
    response = client.post(
        "/api/v1/conversations/respond",
        json={"challenge_behavior": "수업 중 자리에서 반복해서 일어난다.", "messages": []},
    )
    assert response.status_code == 200
    assert response.json()["suggested_intervention"].startswith("-")
    assert agents.calls[0][0] == "수업 중 자리에서 반복해서 일어난다."


def test_case_is_saved_through_repository():
    client, _, repository = make_client()
    response = client.post(
        "/api/v1/cases",
        json={
            "challenge_behavior": "수업 중 자리에서 반복해서 일어난다.",
            "intervention": "시각 일정표를 제공한다.",
            "messages": [],
        },
    )
    assert response.status_code == 201
    assert response.json()["id"] == "case-1"
    assert repository.saved[0].intervention == "시각 일정표를 제공한다."


def test_too_short_behavior_is_rejected():
    client, _, _ = make_client()
    response = client.post(
        "/api/v1/conversations/respond",
        json={"challenge_behavior": "x", "messages": []},
    )
    assert response.status_code == 422
