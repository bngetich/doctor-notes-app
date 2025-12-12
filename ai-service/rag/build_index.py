# ai-service/rag/build_index.py

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


import faiss
import json
from typing import List
from openai import OpenAI
from utils.llm_client import client
from services.knowledge_service import (
    SNOMED_DATA, ICD10_DATA, RXNORM_DATA, LOINC_DATA
)
from utils.embeddings import embed_text

INDEX_PATH = "rag/index/faiss.index"
META_PATH = "rag/index/meta.json"


def build_passages() -> List[dict]:
    passages = []

    # SNOMED
    for row in SNOMED_DATA:
        passages.append({
            "text": f"SNOMED term: {row['term']} | synonyms: {row.get('synonyms')} | code: {row['code']}",
            "system": "snomed",
            "code": row["code"],
            "display": row["preferred"]
        })

    # ICD-10
    for row in ICD10_DATA:
        passages.append({
            "text": f"ICD10 term: {row['term']} | code: {row['code']}",
            "system": "icd10",
            "code": row["code"],
            "display": row["term"]
        })

    # RxNorm
    for row in RXNORM_DATA:
        passages.append({
            "text": f"RxNorm medication: {row['name']} | synonyms: {row.get('synonyms')} | code: {row['rxnorm']}",
            "system": "rxnorm",
            "code": row["rxnorm"],
            "display": row["name"]
        })

    # LOINC
    for row in LOINC_DATA:
        passages.append({
            "text": f"LOINC test: {row['test']} | code: {row['code']}",
            "system": "loinc",
            "code": row["code"],
            "display": row["component"]
        })

    return passages


def build_index():
    passages = build_passages()
    texts = [p["text"] for p in passages]

    # Embed
    vectors = embed_text(texts)  # (N, 1536)

    dim = vectors.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(vectors)

    # Save
    faiss.write_index(index, INDEX_PATH)

    with open(META_PATH, "w") as f:
        json.dump(passages, f, indent=2)

    print(f"Built FAISS index with {len(passages)} entries.")


if __name__ == "__main__":
    build_index()
