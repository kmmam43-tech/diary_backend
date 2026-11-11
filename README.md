# API

도전행동 대화와 중재방안 제안을 처리하는 FastAPI 백엔드입니다. 브라우저는 이 API에만 연결되고, OpenAI 및 Firestore 자격 증명은 백엔드에서만 사용합니다.

## 로컬 실행

Python 3.11 이상이 필요합니다.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
Copy-Item .env.example .env
uvicorn app.main:app --reload --port 8000
```

`.env`에 `OPENAI_API_KEY`를 설정하고, Firestore용 Google Application Default Credentials를 구성해야 실제 Agent 호출과 저장이 동작합니다.

## 환경 변수

- `OPENAI_API_KEY`: OpenAI API 키
- `OPENAI_MODEL`: 두 에이전트가 사용할 모델(기본값 `gpt-4.1-mini`)
- `GOOGLE_CLOUD_PROJECT`: Firestore 프로젝트 ID
- `FIRESTORE_COLLECTION`: 저장할 컬렉션(기본값 `intervention_cases`)
- `CORS_ORIGINS`: 허용할 프론트엔드 출처의 쉼표 구분 목록

로컬 Firestore Emulator를 사용할 때는 `FIRESTORE_EMULATOR_HOST`도 설정합니다.

## API

- `GET /health`: 서버 상태 확인
- `POST /api/v1/conversations/respond`: 도전행동과 대화 기록을 받아 대화 Agent와 중재방안 Agent를 호출
- `POST /api/v1/cases`: 확정한 도전행동과 중재방안을 Firestore에 저장

## 테스트

```powershell
pytest
```

테스트는 OpenAI 및 Firestore 가짜 구현을 주입하므로 외부 서비스나 비밀 키가 필요하지 않습니다.
