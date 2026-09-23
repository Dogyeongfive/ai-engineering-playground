import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

GENERATION_MODEL = os.getenv("OPENAI_CHAT_MODEL", "gpt-5-mini")


def generate_answer(question: str, context: str) -> str:
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    response = client.responses.create(
        model=GENERATION_MODEL,
        instructions=(
            "당신은 문서 기반 질의응답 도우미입니다. "
            "제공된 참고 문서만 근거로 한국어로 답하세요. "
            "참고 문서에 없는 내용은 추측하지 마세요."
        ),
        input=(
            f"[참고 문서]\n{context}\n\n"
            f"[사용자 질문]\n{question}"
        ),
        store=False,
    )
    return response.output_text
