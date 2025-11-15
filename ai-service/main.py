from fastapi import FastAPI
from pydantic import BaseModel


class NoteRequest(BaseModel):
    text: str

app = FastAPI(title="AI Clinical Notes Service")

@app.get("/")
def health_check():
    return {"status": "ok", "message": "AI service running"}

@app.post("/analyze")
def analyze_text(request: NoteRequest):
    text = request.text

    #Mock "AI" logic
    summary = f"Clinical summary: {text}"
    response = {
        "summary": summary,
        "diagnoses": ["Type 2 Diabetes"],
        "symptoms": ["fatigue"],
        "medications": ["Metformin"]
    }
    return response

