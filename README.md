# 🩺 LLM-Powered Clinical Note App

This application converts unstructured clinical text into structured medical data using a full LLM pipeline (summarization → extraction → FHIR). It is designed to power doctor‑patient encounter documentation, EHR integration, and AI-assisted clinical workflows.

## 🚀 Overview

- **Text Input**: Clinicians enter or upload clinical text  
- **Summarization**: LLM generates a human-readable clinical summary  
- **Entity Extraction**: Structured entities (conditions, symptoms, medications, procedures) are extracted  
- **FHIR Conversion**: Extracted entities are transformed into a valid FHIR Bundle  
- **Pipeline Mode**: Single endpoint that performs the full sequence in one call  

This architecture follows the method validated in recent clinical NLP research:  
✔ Step 1 — Extract clinical entities  
✔ Step 2 — Convert to FHIR resources  

## 🛠️ Tech Stack

- **Backend**: FastAPI (Python)  
- **LLM/NLP**: Placeholder for OpenAI / local LLMs  
- **Data Standards**: SNOMED CT, ICD-10, HL7 FHIR  
- **Frontend**: React (planned)  

## 📁 Project Structure

```
doctor-notes-app/
├── ai-service/              
│   ├── main.py              
│   ├── routes/              
│   │   ├── summarize_routes.py
│   │   ├── extract_routes.py
│   │   ├── fhir_routes.py
│   │   └── pipeline_routes.py
│   ├── services/            
│   │   ├── summarizer_service.py
│   │   ├── extractor_service.py
│   │   ├── fhir_service.py
│   │   └── pipeline_service.py
│   ├── models/              
│   │   ├── note_models.py
│   │   ├── extract_models.py
│   │   ├── fhir_models.py
│   │   └── pipeline_models.py
│   └── requirements.txt      
├── frontend/                
├── docs/                    
└── README.md
```

## ⚙️ Setup

### Backend (FastAPI)

```bash
cd ai-service
python3 -m venv venv
source venv/Scripts/activate    # Windows Git Bash
# or: venv\Scripts\activate   # CMD/PowerShell
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

**Access:**  
- **/** → Health check  
- **/docs** → Swagger UI  
- **/redoc** → ReDoc  

## 📡 API Endpoints

| Route | Method | Description | Status |
|-------|--------|-------------|--------|
| `/` | GET | Health check | ✅ Ready |
| `/summarize` | POST | Generate clinical summary from free text | ✅ Ready |
| `/extract` | POST | Extract structured clinical entities | ✅ Ready |
| `/fhir` | POST | Convert entities into a FHIR Bundle | ✅ Ready |
| `/pipeline` | POST | Full pipeline: summarize → extract → FHIR | ✅ Ready |
| `/audio/upload` | POST | Upload audio for transcription | ◻️ Planned |

## 📄 Example Requests

### 📝 Summarization (`POST /summarize`)

```json
{
  "text": "Patient with diabetes on metformin."
}
```

### 🔍 Extraction (`POST /extract`)

```json
{
  "conditions": ["Type 2 Diabetes"],
  "symptoms": [{ "name": "fatigue", "duration": "3 weeks" }],
  "medications": [{ "name": "Metformin", "dose": "500mg", "frequency": "daily" }],
  "procedures": []
}
```

### 🏥 FHIR Generation (`POST /fhir`)

Produces a **FHIR Bundle** containing Condition, Observation, MedicationStatement, and Procedure resources.

### 🔗 Full Pipeline (`POST /pipeline`)

```json
{
  "text": "Patient reports fatigue for 3 weeks and takes Metformin 500mg daily."
}
```

Response includes:

- `summary`
- `entities`
- `fhir`

## 📁 Planned Upload Flow

1. Doctor uploads audio  
2. `/audio/upload` → Whisper (future)  
3. System extracts entities  
4. System returns summary + extracted entities + FHIR Bundle  

## 🚀 Future Enhancements

- Integrate OpenAI Whisper or WhisperX  
- Use MedCAT or scispaCy for medical NER  
- Auto-map to SNOMED CT + ICD-10  
- Build a React clinician UI  
- Expand `/pipeline` with additional reasoning steps  
- Add OAuth2 + JWT authentication  
- Support export to FHIR servers (HAPI, Google FHIR, Firely)  

## 📈 Development Progress

| Phase | Status | Description |
|-------|--------|-------------|
| Phase 1 | ✅ Complete | Backend architecture + routing |
| Phase 2 | 🔄 In Progress | LLM summarization + extraction |
| Phase 3 | 🔄 In Progress | FHIR Bundle generation |
| Phase 4 | ⚪ Planned | Audio input + frontend |

## 📚 Documentation

- [Architecture Overview](./docs/architecture.md)
- [Development Plan](./docs/plan.md)
- [Roadmap](./docs/roadmap.md)
