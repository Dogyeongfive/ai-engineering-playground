from sqlalchemy.orm import Session

from app.services import document_service, generation_service

NO_CONTEXT_ANSWER = "관련 문서를 찾지 못했습니다."
AMBIGUOUS_CONTEXT_ANSWER = "검색 결과를 하나로 확정하기 어렵습니다."


def answer_question(
    db: Session,
    question: str,
    top_k: int,
    min_score: float,
    min_margin: float,
):
    search_response = document_service.search_document_chunks(
        db,
        question,
        top_k,
    )
    sources = [
        result
        for result in search_response["results"]
        if result["score"] >= min_score
    ]

    if not sources:
        return {
            "question": question,
            "answer": NO_CONTEXT_ANSWER,
            "sources": [],
            "model": None,
        }

    if len(sources) >= 2:
        margin = sources[0]["score"] - sources[1]["score"]
        if margin < min_margin:
            return {
                "question": question,
                "answer": AMBIGUOUS_CONTEXT_ANSWER,
                "sources": sources[:2],
                "model": None,
            }

    context = "\n\n".join(
        (
            f"[문서 {source['document_id']} / "
            f"청크 {source['chunk_index']}]\n"
            f"{source['content']}"
        )
        for source in sources
    )
    answer = generation_service.generate_answer(question, context)

    return {
        "question": question,
        "answer": answer,
        "sources": sources,
        "model": generation_service.GENERATION_MODEL,
    }
