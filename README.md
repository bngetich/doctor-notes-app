# 🩺 LLM-Powered Clinical Note Structuring App

This is a prototype application that captures doctor-patient encounters, uses a Large Language Model (LLM) to extract clinical entities, maps them to standardized medical codes (e.g., SNOMED CT, ICD-10), and outputs the data as FHIR-compliant resources.

## 🚀 Overview

- **Voice Input**: Doctors can upload voice recordings of clinical notes
- **LLM Processing**: Transcribes and extracts relevant clinical entities
- **Medical Coding**: Maps entities to SNOMED CT, ICD-10, or other coding systems
- **FHIR Output**: Produces structured FHIR resources for interoperability

## 🛠️ Tech Stack

- **Frontend**: React
- **Backend**: FastAPI (Python)
- **LLM/NLP**: (Pluggable, placeholder for Whisper + entity mapping)
- **Data Standardization**: SNOMED CT, ICD-10, FHIR

## 📁 Project Structure

```
doctor-notes-app/
├── ai-service/             # FastAPI backend
│   ├── main.py             # Entry point
│   ├── routes/             # API endpoints (analyze, fhir, audio)
│   ├── services/           # Business logic modules
│   ├── models/             # Pydantic models
│   └── requirements.txt    # Python dependencies
├── frontend/               # React app (planned)
├── docs/                   # Documentation
├── .gitignore
└── README.md
```

## ⚙️ Setup

### 🚀 Backend (FastAPI)

```bash
cd ai-service
python3 -m venv venv
source venv/Scripts/activate    # Windows Git Bash
# Or: venv\Scripts\activate     # Windows CMD/PowerShell
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

**Access:**
-  [http://127.0.0.1:8000](http://127.0.0.1:8000) → Health check  
-  [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) → Interactive API docs (Swagger UI)  
-  [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc) → Alternative API docs (ReDoc)

## 📡 API Endpoints

| Route | Method | Description | Status |
|-------|---------|-------------|---------|
| `/` | GET | Health check | ✅ Ready |
| `/analyze` | POST | Summarize and extract structured text |  Planned |
| `/fhir` | POST | Generate mock FHIR Observation |  Planned |
| `/audio/upload` | POST | Upload audio file (mock transcription) |  Planned |

## 📄 Example Request (Planned)

```bash
POST /analyze
```

**Request Body:**
```json
{
  "text": "Patient with diabetes on metformin."
}
```

**Response:**
```json
{
  "summary": "Clinical summary: Patient with diabetes treated with metformin.",
  "diagnoses": ["Type 2 Diabetes"],
  "symptoms": ["fatigue"],
  "medications": ["Metformin"]
}
```

## 📁 Upload Flow (Future)

1.  Doctor records or uploads an `.mp3`/`.wav` file
2.  Audio sent to `/audio/upload`
3.  Server transcribes and extracts structured clinical data
4. ✅ Returns mapped entities and FHIR resource JSON

## 🚀 Future Enhancements

-  Integrate OpenAI Whisper or WhisperX for real transcription
-  Use scispaCy or MedCAT for medical entity recognition
- ✏️ Add UI for editing structured output
-  Support OAuth2 for secure access
-  Store FHIR bundles in a compatible backend (e.g. HAPI FHIR server)
- ⚛️ Build React frontend for better UX

## 🚀 Development Progress

| Phase | Status | Description |
|-------|--------|-------------|
| Phase 1 |  In Progress | FastAPI backend structure |
| Phase 2 | ⚪ Planned | LLM integration for summarization |
| Phase 3 | ⚪ Planned | FHIR generation & medical coding |
| Phase 4 | ⚪ Planned | Audio input & frontend |

**Current work:** [Design a Service that Summarizes Patient Notes](./docs/plan.md)

## 📄 Documentation

- [Architecture Overview](./docs/architecture.md)
- [Development Plan](./docs/plan.md)
- [Roadmap](./docs/roadmap.md)
