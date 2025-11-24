# 🏗️ System Architecture

This document describes the architecture of the **LLM-Powered Clinical Note App**, including backend structure, pipeline design, and how LLMs integrate into the system.

---

## 🧩 High-Level System Components

### **1. Frontend (React – planned)**
- Clinician enters text or uploads audio
- Displays summary, structured entities, and FHIR output

### **2. Backend (FastAPI + Python)**
- `/summarize` — LLM summarization  
- `/extract` — LLM entity extraction  
- `/fhir` — FHIR bundle generation  
- `/pipeline` — summarize → extract → fhir in one call

### **3. External LLM Provider**
- Currently OpenAI API
- Can later support:
  - NVIDIA NIM
  - vLLM
  - Ollama
  - Local models

---

## 🧬 Pipeline Architecture Overview

```
text → summarize → extract → fhir → output
```

---

## 🚦 Pipeline Sequence Diagram

```mermaid
sequenceDiagram
    participant User
    participant Backend as FastAPI Backend
    participant Sum as Summarizer Service
    participant Ext as Extractor Service
    participant FHIR as FHIR Service
    participant LLM as OpenAI / Local LLM

    User->>Backend: POST /pipeline (text)
    Backend->>Sum: summarize(text)
    Sum->>LLM: Summarization Prompt
    LLM-->>Sum: { summary }
    Sum-->>Backend: summary

    Backend->>Ext: extract(text)
    Ext->>LLM: Extraction Prompt with JSON schema
    LLM-->>Ext: { entities }
    Ext-->>Backend: ExtractResponse

    Backend->>FHIR: generate_fhir_bundle(entities)
    FHIR-->>Backend: FHIR Bundle

    Backend-->>User: { summary, entities, fhir }
```

---

## 🧱 Backend Layered Architecture

```mermaid
graph TD
    subgraph Routes
        R1[summarize_routes.py]
        R2[extract_routes.py]
        R3[fhir_routes.py]
        R4[pipeline_routes.py]
    end

    subgraph Services
        S1[summarizer_service.py]
        S2[extractor_service.py]
        S3[fhir_service.py]
        S4[pipeline_service.py]
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

    S1 --> M1
    S2 --> M2
    S3 --> M2
    S4 --> M1
    S4 --> M2
    S4 --> M3
```

---

## 🧠 Key Architecture Decisions

### ✔ **Unified Clinical Schema — ExtractResponse**
One schema powers extraction → fhir.  
No duplication, no drift, simple pipeline.

### ✔ **Services return plain dicts**
FastAPI handles validation through `response_model`.

### ✔ **Interchangeable LLM backend**
Only `summarizer_service` and `extractor_service` depend on the LLM provider.

### ✔ **Agent-ready Pipeline**
The `/pipeline` endpoint can later include:
- validation
- error correction
- tool usage
- medical reasoning

---

## 📌 Future Architectural Enhancements
- Add audio → text service
- Add vector DB for guidelines lookup
- Add terminology server integration (Snowstorm)
- Add agentic orchestration layer

