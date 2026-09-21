import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

EMBEDDING_MODEL = "text-embedding-3-small"


def create_embeddings(texts: list[str]) -> list[list[float]]:
    if not texts:
        return []

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    response = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=texts,
    )

    ordered_data = sorted(response.data, key=lambda item: item.index)
    return [item.embedding for item in ordered_data]
