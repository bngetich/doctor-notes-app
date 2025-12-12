import faiss
import json
from utils.embeddings import embed_text

INDEX_PATH = "rag/index/faiss.index"
META_PATH = "rag/index/meta.json"

index = faiss.read_index(INDEX_PATH)
metadata = json.load(open(META_PATH))


def rag_lookup(query: str, k: int = 3):
    vec = embed_text([query])
    scores, idxs = index.search(vec, k)

    results = []
    for score, idx in zip(scores[0], idxs[0]):
        item = metadata[idx]
        results.append({
            "system": item["system"],
            "code": item["code"],
            "display": item["display"],
            "score": float(score)
        })
    
    return results
