def summarize(text: str):
    """
    Mock summarization logic.
    Later this will call an actual LLM or RAG pipeline.
    """
    return {
        "summary": f"Clinical summary: {text}",
        "diagnoses": ["Type 2 Diabetes"],
        "symptoms": ["fatigue"],
        "medications": ["Metformin"]
    }
