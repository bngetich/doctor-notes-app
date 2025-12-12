# 🏗️ System Architecture

This file explains how all components in the backend work together.

---

# ⚙️ High-Level Architecture

The backend is composed of four cooperating subsystems:

1. **Summarizer Service** → LLM converts raw text → concise structured summary  
2. **Extractor Service** → LLM extracts structured medical entities in strict JSON  
3. **Normalization Service** → cleans the extracted data and ensures consistency  
4. **FHIR Service** → converts normalized entities → HL7 FHIR Bundle  

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

        User->>Backend: POST /pipeline
        Backend->>Sum: summarize(text)
        Sum->>LLM: Summarization prompt
        LLM-->>Sum: summary
        Sum-->>Backend: { summary }

        Backend->>Ext: extract(text)
        Ext->>LLM: Extraction schema
        LLM-->>Ext: JSON entities
        Ext-->>Backend: structured entities

        Backend->>Norm: normalize_entities(raw)
        Norm-->>Backend: cleaned entities

        Backend->>FHIR: generate_fhir_bundle(cleaned)
        FHIR-->>Backend: FHIR Bundle

        Backend-->>User: Full pipeline output
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
- Converts raw text → summary  
- Extracts high-level details  

### **Extractor**
- Uses strict JSON schema  
- Normalizes missing fields  
- Repairs invalid JSON  

### **Normalization**
- Ensures stable formatting  
- Prepares safe input for FHIR  

### **FHIR Generator**
- Generates HL7-compliant resources  
- Includes SNOMED / ICD-10 / RxNorm / LOINC support  
- Supports RAG semantic coding lookup  

---

# 📍 Design Principles

- LLM → noisy; Normalizer → stable; FHIR → strict
- Keep services modular & testable
- Allow local or cloud LLMs

---

# ✔️ End of architecture.md

