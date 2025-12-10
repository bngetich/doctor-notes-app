import numpy as np
from typing import List
from config import client


EMBEDDING_MODEL = "text-embedding-3-small"


def embed_text(texts: List[str]) -> np.ndarray:
    """
    Embed a list of strings using OpenAI embeddings.
    Returns a NumPy matrix of shape (N, 1536).
    """

    if isinstance(texts, str):
        texts = [texts]

    response = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=texts
    )

    vectors = [item.embedding for item in response.data]
    return np.array(vectors, dtype=np.float32)