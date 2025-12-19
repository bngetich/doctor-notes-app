# LLM-Powered Clinical Note App

This application converts unstructured clinical text into **structured, interoperable medical data** using a full LLM pipeline:

**summarization → extraction → normalization → terminology coding (RAG + CSV) → FHIR**

It is designed for doctor-patient encounter documentation, EHR integration, and AI-assisted clinical workflows.

## Overview

 - **Text Input**: Clinicians input free-text notes  
 - **Summarization**: LLM rewrites text into a concise clinical summary  
 - **Extraction**: LLM extracts structured medical entities  
 - **Normalization**: Cleans and standardizes noisy LLM output  
 - **Terminology Coding**:  
   - RAG semantic search over SNOMED / ICD-10 / RxNorm / LOINC  
   - CSV-backed validation so codes are grounded in real vocabularies  
 - **FHIR Conversion**: Creates interoperable FHIR Bundles  
 - **Pipeline Mode**: One endpoint performs all steps sequentially  

The core pattern follows modern clinical NLP work:

> **Extract entities → Normalize → Code with standard vocabularies → Convert to FHIR**

---

## Tech Stack

- **Backend**: FastAPI (Python)  
- **LLM Provider**: OpenAI API (pluggable for local models later)  
- **Standards**: FHIR R4, SNOMED CT, ICD-10, LOINC, RxNorm  
- **Retrieval**: FAISS + embeddings (RAG) over local CSV vocabularies  
- **Frontend**: React (planned)  

---

## Project Structure

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
│   │   ├── schema_normalization.py
│   │   ├── knowledge_service.py      # CSV-backed terminology lookups
│   │   ├── fhir_service.py           # FHIR + coding (uses RAG + CSV)
│   │   └── pipeline_service.py
│   ├── rag/
│   │   ├── build_index.py            # build FAISS index from CSVs
│   │   └── rag_search.py             # semantic lookup (rag_lookup)
│   ├── models/              
│   │   ├── note_models.py
│   │   ├── extract_models.py
│   │   ├── fhir_models.py
│   │   └── pipeline_models.py
│   ├── data/
│   │   ├── snomed.csv
│   │   ├── icd10.csv
│   │   ├── rxnorm.csv
│   │   └── loinc.csv
│   └── requirements.txt      
├── frontend/                
├── docs/                    
└── README.md
```

---

## API Endpoints

| Route | Method | Description | Status |
|-------|--------|-------------|--------|
| `/` | GET | Health check | ✅ Ready |
| `/summarize` | POST | Generate clinical summary | ✅ Ready |
| `/extract` | POST | Extract structured clinical entities | ✅ Ready |
| `/normalize` | POST | Normalize LLM entities | ✅ Ready |
| `/fhir` | POST | Convert entities into a FHIR Bundle | ✅ Ready |
| `/pipeline` | POST | summarize → extract → normalize → FHIR | ✅ Ready |
| `/audio/upload` | POST | Audio upload for transcription (future) | ◻️ Planned |

---

## Setup (Backend)

```bash
cd ai-service
python3 -m venv venv
source venv/Scripts/activate   # Windows Git Bash
# or: venv\Scripts\activate    # CMD/PowerShell

pip install -r requirements.txt

# Run FastAPI
uvicorn main:app --reload --port 8000
```

Access:

- GET `/` → Health check
- GET `/docs` → Swagger UI
- GET `/redoc` → ReDoc

---

## Normalization Layer

The normalization component performs:

- Trim whitespace; normalize empty strings → `null`  
- Lowercase categories (e.g., gender, severity, “daily”)  
- Filter out invalid/empty entities  
- Normalize vitals like `"88 bpm"` → value + unit  
- Convert numeric strings → float when possible  
- Drop empty social history objects  

This makes downstream FHIR generation stable, even if the LLM output is messy.

---

## Terminology Coding (RAG + CSV)

For conditions, labs, and medications, the system uses both:

1. RAG Semantic Search  
Build a FAISS index over:

- snomed.csv  
- icd10.csv  
- rxnorm.csv  
- loinc.csv  

`rag_search.rag_lookup(term)` returns top candidate coding dict(s):

```json
{
  "system": "http://snomed.info/sct",
  "code": "44054006",
  "display": "Type 2 diabetes mellitus"
}
```

This helps with synonyms and “messy” text (e.g., “sugar disease”, “adult-onset diabetes”).

2. CSV Validation (Ground Truth)  
The app does not trust RAG blindly.

For conditions:

- Take RAG candidate { system, code, display }  
- Validate it against `knowledge_service` (CSV lookups):  
  `lookup_snomed(display)` / `lookup_icd10(display)`  
- Only accept RAG coding if the code matches what the CSV says.  
- Otherwise, fall back to `lookup_snomed(term)` + `lookup_icd10(term)`.

This gives you:  
Semantic retrieval for synonyms + deterministic codes from local vocabularies.

Exactly the pattern:  
User term → embeddings → RAG search → validate against CSV → FHIR coding

---

## FHIR Generation

The FHIR service outputs:

- Patient  
- Condition (conditions + assessment summary)  
- Observation  
  - symptoms  
  - vitals  
  - labs  
  - physical exam  
  - social history  
- MedicationStatement (RxNorm coding)  
- Procedure  
- AllergyIntolerance  
- DiagnosticReport (imaging)  
- FamilyMemberHistory  
- CarePlan  

All resources:  
- Get a random UUID (`id`)  
- Reference the Patient via `subject: { "reference": "Patient/<uuid>" }`  
- Use coding when available:  
  - SNOMED / ICD-10 for conditions  
  - RxNorm for meds  
  - LOINC for labs  

All wrapped in a FHIR **Bundle (type=collection)**.

---

## Full Pipeline (`POST /pipeline`)

Input:

```json
{
  "text": "54-year-old male with type 2 diabetes on metformin daily. Recent HbA1c is 7.4%."
}
```

Response (shape):

```json
{
  "summary": "A 54-year-old male with type 2 diabetes on metformin daily. Recent HbA1c is 7.4%.",
  "entities": { "...": "..." },
  "normalized_entities": { "...": "..." },
  "fhir": {
    "resourceType": "Bundle",
    "type": "collection",
    "entry": [
      { "resource": { "resourceType": "Patient" } },
      { "resource": { "resourceType": "Condition" } },
      { "resource": { "resourceType": "Observation" } },
      { "resource": { "resourceType": "MedicationStatement" } }
    ]
  }
}
```

---

## Future Enhancements

- Audio: integrate Whisper / WhisperX for `/audio/upload`  
- Deeper RAG: expand to labs and medications; per-vocabulary FAISS indexes  
- FHIR validation: `/validate` endpoint using official schemas / HAPI FHIR  
- Agentic workflows: multi-step reasoning; clarification prompts for ambiguity  
- UI: React clinician UI with side-by-side text/FHIR view; patient timeline  

---

## Development Progress

| Phase | Status |
|--------|--------|
| Backend architecture | ✅ Complete |
| Summarization | 🔄 In Progress |
| Extraction | 🔄 In Progress |
| Normalization | 🔄 In Progress |
| Terminology coding (RAG + CSV) | 🔄 In Progress |
| FHIR Bundle generation | ✅ Complete |
| Audio + frontend | ◻️ Planned |

---

## Documentation

- [Architecture Overview](./docs/architecture.md)
- [Development Plan](./docs/plan.md)
- [Roadmap](./docs/roadmap.md)
