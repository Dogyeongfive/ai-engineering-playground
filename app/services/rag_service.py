from sqlalchemy.orm import Session

from app.services import document_service, generation_service

NO_CONTEXT_ANSWER = "관련 문서를 찾지 못했습니다."


def answer_question(
    db: Session,
    question: str,
    top_k: int,
    min_score: float,
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

    context_parts = []
    for source in sources:
        page_label = (
            f" / {source['page_number']}페이지"
            if source["page_number"] is not None
            else ""
        )
        context_parts.append(
            f"[문서 {source['document_id']} / "
            f"청크 {source['chunk_index']}{page_label}]\n"
            f"{source['content']}"
        )
    context = "\n\n".join(context_parts)
    answer = generation_service.generate_answer(question, context)

    return {
        "question": question,
        "answer": answer,
        "sources": sources,
        "model": generation_service.GENERATION_MODEL,
    }
