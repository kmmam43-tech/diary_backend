from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware

from app.config import Settings, get_settings
from app.models import CaseCreateRequest, CaseCreateResponse, ConversationRequest, ConversationResponse
from app.services.agent_service import AgentService, OpenAIAgentService
from app.services.case_repository import CaseRepository, FirestoreCaseRepository


def create_app(
    settings: Settings | None = None,
    agent_service: AgentService | None = None,
    case_repository: CaseRepository | None = None,
) -> FastAPI:
    current_settings = settings or get_settings()
    application = FastAPI(title="도전행동 중재 지원 API", version="1.0.0")
    application.add_middleware(
        CORSMiddleware,
        allow_origins=current_settings.allowed_origins,
        allow_credentials=False,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["Content-Type"],
    )
    application.state.agent_service = agent_service or OpenAIAgentService(
        model=current_settings.openai_model,
        api_key=current_settings.openai_api_key,
    )
    application.state.case_repository = case_repository or FirestoreCaseRepository(
        project_id=current_settings.google_cloud_project,
        collection=current_settings.firestore_collection,
    )

    @application.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    @application.post("/api/v1/conversations/respond", response_model=ConversationResponse)
    async def respond(payload: ConversationRequest, request: Request) -> ConversationResponse:
        try:
            return await request.app.state.agent_service.respond(payload.challenge_behavior, payload.messages)
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Agent 응답을 생성하지 못했습니다. 서버 설정과 로그를 확인하세요.",
            ) from exc

    @application.post(
        "/api/v1/cases",
        response_model=CaseCreateResponse,
        status_code=status.HTTP_201_CREATED,
    )
    async def create_case(payload: CaseCreateRequest, request: Request) -> CaseCreateResponse:
        try:
            return await request.app.state.case_repository.create(payload)
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Firestore에 저장하지 못했습니다. 서버 설정과 로그를 확인하세요.",
            ) from exc

    return application


app = create_app()
