# 📘 Development Plan

This document provides a step-by-step plan for building the LLM-Powered Clinical Note App.

---

# 🧩 Phase Breakdown

## **Phase 1 — Backend Setup (Done)**
- FastAPI folder structure
- Modular routes, services, models
- Base README + docs

---

## **Phase 2 — LLM Integration (In Progress)**

### Summarization:
- Prompt engineering for summary
- OpenAI API integration
- Error handling + retry logic

### Extraction:
- Define ExtractResponse schema
- Strong JSON schema in system prompt
- Normalize LLM JSON
- Validate via Pydantic

---

## **Phase 3 — FHIR Bundle Generation (In Progress)**
- Map conditions → Condition
- Map symptoms → Observation
- Map meds → MedicationStatement
- Map allergies → AllergyIntolerance
- Map procedures → Procedure
- Produce correct Bundle structure

---

## **Phase 4 — Audio Pipeline**
- Upload `.wav` / `.mp3`
- Integrate Whisper / WhisperX
- Transcription → extract → fhir

---

## **Phase 5 — Frontend (React)**
- Clinician input UI
- Summary + entities display
- JSON viewer for FHIR
- Audio upload component

---

## **Phase 6 — Coding Expansion**
- SNOMED CT coding
- ICD-10 suggestions
- LOINC for labs/vitals
- RxNorm for medications

---

## **Phase 7 — Agentic Reasoning Layer**
- Validate model outputs
- Look up clinical guidelines
- Detect missing findings
- Ask follow-up questions
- Chain-of-thought via internal reasoning (not exposed)

---

## **Phase 8 — Deployment + EHR Integration**
- Docker container
- FHIR server export
- OAuth2 + JWT
- HAPI FHIR / Firely integration

---

# 🏁 Long-Term Goal
A system that:
- listens to encounters
- summarizes them
- extracts structured entities
- validates accuracy
- codes them
- outputs FHIR
- integrates into clinical workflow

