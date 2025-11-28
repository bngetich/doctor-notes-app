# 🏗️ System Architecture

This document describes how all components in the Doctor Notes App work together.

---

# ⚙️ High-Level Architecture

The backend is composed of four cooperating subsystems:

1. **Summarizer Service** → rewrites raw text into EMR-style summary  
2. **Extractor Service** → extracts structured entities  
3. **Normalization Service** → cleans & standardizes extracted data  
4. **FHIR Service** → generates a FHIR Bundle  

These are orchestrated by `pipeline_service.py`.

---

# 🚦 Pipeline Sequence Diagram

```mermaid
sequenceDiagram
    participant User
    participant Backend as FastAPI Backend
    participant Sum as Summarizer Service
    participant Ext as Extractor Service
    participant Norm as Normalization Service
    participant FHIR as FHIR Service
    participant LLM as OpenAI / Local LLM

    User->>Backend: POST /pipeline (text)
    Backend->>Sum: summarize(text)
    Sum->>LLM: Summarization Prompt
    LLM-->>Sum: { summary }
    Sum-->>Backend: summary

    Backend->>Ext: extract(text)
    Ext->>LLM: Extraction Prompt (JSON schema)
    LLM-->>Ext: { entities }
    Ext-->>Backend: ExtractResponse

    Backend->>Norm: normalize_entities(raw_entities)
    Norm-->>Backend: Cleaned entities

    Backend->>FHIR: generate_fhir_bundle(normalized_entities)
    FHIR-->>Backend: FHIR Bundle

    Backend-->>User: { summary, entities, normalized, fhir }
```

---

# 🧱 Backend Layered Architecture

```mermaid
graph TD
    subgraph Routes
        R1[summarize_routes.py]
        R2[extract_routes.py]
        R3[normalize_routes.py]
        R4[fhir_routes.py]
        R5[pipeline_routes.py]
    end

    subgraph Services
        S1[summarizer_service.py]
        S2[extractor_service.py]
        S3[normalization_service.py]
        S4[fhir_service.py]
        S5[pipeline_service.py]
    end

    subgraph Models
        M1[note_models.py]
        M2[extract_models.py]
        M3[fhir_models.py]
        M4[pipeline_models.py]
    end

    R1 --> S1
    R2 --> S2
    R3 --> S3
    R4 --> S4
    R5 --> S5

    S1 --> M1
    S2 --> M2
    S3 --> M2
    S4 --> M2
    S5 --> M1
    S5 --> M2
    S5 --> M3
```

---

# 🧩 Component Responsibilities

### **Summarizer**
- Converts text → EMR-style summary  
- Extracts basic diagnoses, symptoms, medications  

### **Extractor**
- Runs strict JSON schema extraction  
- Produces deeply structured clinical entities  

### **Normalization**
- Removes noise  
- Ensures entity shape matches Pydantic models  
- Prepares data for FHIR stability  

### **FHIR Generator**
- Creates real, structured, interoperable FHIR resources  
- Outputs full Bundle  

---

# 📍 Design Principles

- **LLM variability → normalization → stable FHIR output**
- Keep services modular & testable
- Allow local or cloud LLMs

---

# ✔️ End of architecture.md
