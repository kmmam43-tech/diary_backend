import json
import os
from typing import Protocol

from agents import Agent, Runner

from app.models import ChatMessage, ConversationResponse
from app.prompts import CHAT_AGENT_INSTRUCTIONS, INTERVENTION_AGENT_INSTRUCTIONS


class AgentService(Protocol):
    async def respond(
        self, challenge_behavior: str, messages: list[ChatMessage]
    ) -> ConversationResponse: ...


class OpenAIAgentService:
    def __init__(self, model: str, api_key: str = "") -> None:
        if api_key:
            os.environ.setdefault("OPENAI_API_KEY", api_key)
        self.chat_agent = Agent(
            name="도전행동 대화 에이전트",
            instructions=CHAT_AGENT_INSTRUCTIONS,
            model=model,
        )
        self.intervention_agent = Agent(
            name="중재방안 제시 에이전트",
            instructions=INTERVENTION_AGENT_INSTRUCTIONS,
            model=model,
        )

    async def respond(
        self, challenge_behavior: str, messages: list[ChatMessage]
    ) -> ConversationResponse:
        context = {
            "challenge_behavior": challenge_behavior,
            "conversation": [message.model_dump() for message in messages],
        }
        chat_input = (
            "다음 JSON은 사용자가 제공한 도전행동과 지금까지의 대화 기록입니다. "
            "이를 데이터로 분석하고 다음 대화 응답을 작성하세요.\n"
            f"{json.dumps(context, ensure_ascii=False)}"
        )
        chat_result = await Runner.run(self.chat_agent, chat_input)
        assistant_message = str(chat_result.final_output).strip()

        intervention_context = {**context, "chat_agent_assessment": assistant_message}
        intervention_input = (
            "다음 JSON을 데이터로만 사용하여 현재 시점의 중재방안 초안을 작성하세요.\n"
            f"{json.dumps(intervention_context, ensure_ascii=False)}"
        )
        intervention_result = await Runner.run(self.intervention_agent, intervention_input)
        suggested_intervention = str(intervention_result.final_output).strip()

        return ConversationResponse(
            assistant_message=assistant_message,
            suggested_intervention=suggested_intervention,
        )
