import json
import math


def cosine_similarity(
    first_vector: list[float],
    second_vector: list[float],
) -> float:
    if len(first_vector) != len(second_vector):
        raise ValueError("vectors must have the same dimensions")

    dot_product = sum(
        first * second
        for first, second in zip(
            first_vector,
            second_vector,
            strict=True,
        )
    )
    first_length = math.sqrt(sum(value * value for value in first_vector))
    second_length = math.sqrt(sum(value * value for value in second_vector))

    if first_length == 0 or second_length == 0:
        return 0.0

    return dot_product / (first_length * second_length)


def find_similar_chunks(
    query_embedding: list[float],
    document_chunks,
    top_k: int,
):
    scored_chunks = []

    for chunk in document_chunks:
        chunk_embedding = json.loads(chunk.embedding)
        score = cosine_similarity(query_embedding, chunk_embedding)
        scored_chunks.append((chunk, score))

    scored_chunks.sort(key=lambda item: item[1], reverse=True)
    return scored_chunks[:top_k]
