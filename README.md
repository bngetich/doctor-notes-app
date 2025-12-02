# 🩺 LLM-Powered Clinical Note App

This application converts unstructured clinical text into structured medical data using a full LLM pipeline (summarization → extraction → normalization → FHIR). It is designed to power doctor-patient encounter documentation, EHR integration, and AI-assisted clinical workflows.

## 🚀 Overview

- **Text Input**: Clinicians enter or upload clinical text  
- **Summarization**: LLM generates a human-readable clinical summary  
- **Entity Extraction**: LLM produces structured medical entities  
- **Normalization**: Cleans and standardizes noisy LLM output  
- **FHIR Conversion**: Creates interoperable FHIR Bundles  
- **Pipeline Mode**: One endpoint performs all steps in sequence  

This follows the method validated in recent clinical NLP research:
✔ Extract entities  
✔ Standardize  
✔ Convert to FHIR  

---

## 🛠️ Tech Stack

- **Backend**: FastAPI (Python)  
- **LLM Provider**: OpenAI API (pluggable for local models)  
- **Data Standards**: SNOMED CT, ICD-10, HL7 FHIR  
- **Frontend**: React (planned)  

---

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
│   │   ├── normalization_service.py
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

---

## 📡 API Endpoints

| Route | Method | Description | Status |
|-------|--------|-------------|--------|
| `/` | GET | Health check | ✅ Ready |
| `/summarize` | POST | Generate clinical summary | ✅ Ready |
| `/extract` | POST | Extract structured clinical entities | ✅ Ready |
| `/normalize` | POST | Normalize LLM output | ✅ Ready |
| `/fhir` | POST | Convert entities into a FHIR Bundle | ✅ Ready |
| `/pipeline` | POST | summarize → extract → normalize → FHIR | ✅ Ready |
| `/audio/upload` | POST | Upload audio for transcription | ◻️ Planned |

---

## 🧼 Normalization Layer

The normalization component performs:

- whitespace trimming  
- lowercasing clinical categories  
- filtering invalid entries  
- standardizing vitals like `"88 bpm"`  
- converting number strings → floats  
- removing empty or null objects  

This makes FHIR generation **reliable and predictable**, regardless of LLM noise.

---

## 🏥 FHIR Generation

The FHIR service outputs:

- Patient  
- Condition  
- Observation (symptoms, vitals, labs, physical exam, social history)  
- MedicationStatement  
- Procedure  
- AllergyIntolerance  
- DiagnosticReport  
- FamilyMemberHistory  
- CarePlan  

All wrapped in a FHIR **Bundle (type=collection)**.

---

## 🔗 Full Pipeline (`POST /pipeline`)

Input:

```json
{
  "text": "Patient reports fatigue for 3 weeks and takes Metformin 500mg daily."
}
```

Output includes:

- `summary`  
- `entities`  
- `normalized_entities`  
- `fhir`  

---

## 🚀 Future Enhancements

- Integrate Whisper for audio  
- Add SNOMED CT / ICD-10 / LOINC mapping  
- Add validation against HL7 schemas  
- Full React clinician UI  
- Agentic workflow for multi-step reasoning  
- Deployable container setup  

---

## 📈 Development Progress

| Phase | Status |
|--------|--------|
| Backend architecture | ✅ Complete |
| Summarization | 🔄 In Progress |
| Extraction | 🔄 In Progress |
| Normalization | 🔄 In Progress |
| FHIR Bundle generation | 🔄 In Progress |
| Audio + frontend | ◻️ Planned |

---

## 📚 Documentation

- [Architecture Overview](./docs/architecture.md)
- [Development Plan](./docs/plan.md)
- [Roadmap](./docs/roadmap.md)
