from fastapi import FastAPI
from routes.summarize_routes import router as summarize_router
from routes.extract_routes import router as extract_router
from routes.fhir_routes import router as fhir_router

app = FastAPI(title="AI Clinical Notes Service")

@app.get("/")
def health_check():
    return {"status": "ok", "message": "AI service running"}

app.include_router(summarize_router)
app.include_router(extract_router)
app.include_router(fhir_router)



