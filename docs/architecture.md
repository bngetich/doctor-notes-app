# System Architecture

This document explains how the project is structured, what services it has, and how they talk to each other.
It supports the main goal in README: an LLM-powered clinical note structuring app.

## High-Level Components

- **Frontend (React)** – user interface to enter/view notes.
- **Backend Gateway (Spring Boot)** – receives requests from the frontend, calls the AI service.
- **AI Service (FastAPI, Python)** – does the summarization (later: entity extraction, FHIR).
- **Docker Compose** – runs all services together locally.


## Architecture Diagram

```mermaid
graph LR
  A[React Frontend] -->|POST /api/notes| B[Spring Boot API]
  B -->|POST /api/summarize| C[FastAPI Service]
  C --> B
  B --> A


---

### 4. Component details
Now describe each box in 2–4 bullets.

```markdown
## Component Details

### 1. React Frontend
- Runs in the browser.
- Sends doctor/patient notes to Spring Boot.
- Displays summarized result.

### 2. Spring Boot (Java)
- Exposes `/api/notes`.
- Forwards the note to the FastAPI service.
- Returns JSON back to the frontend.
- Good place later for auth/logging.

### 3. FastAPI (Python)
- Exposes `/api/summarize`.
- Right now: RAG-style, in-memory KB.
- Later: real LLM, entity extraction, FHIR.

### 4. Docker Compose
- Creates one network.
- Starts all 3 services with correct ports.

## Request Flow (Summarize Note)

1. User types a clinical note in React and clicks **Summarize**.
2. React does `POST http://localhost:8080/api/notes` with `{ "note": "..." }`.
3. Spring Boot receives it and sends `POST http://fastapi-service:8000/api/summarize` (inside Docker).
4. FastAPI summarizes the note (RAG-style) and returns `{ "summary": "..." }`.
5. Spring Boot forwards that JSON back to React.
6. React shows the summary to the user.

## API Contracts

### FastAPI: POST /api/summarize
**Request**
```json
{ "note": "Patient with diabetes on metformin." }
**Response**
{ "summary": "Clinical summary: ..."}


---

### 7. Future evolution
Tie it back to your original README (LLM → codes → FHIR).

```markdown
## Future Evolution

- Replace mock summarizer with real LLM (OpenAI, NVIDIA).
- Add entity extraction and code mapping (SNOMED CT, ICD-10).
- Add FHIR bundle generation.
- Add voice/audio ingestion (Whisper) as another entry point.

## Summary

The app is split into 3 small services so AI logic (Python) stays separate from enterprise logic (Java) and UI (React). Docker Compose lets us run everything together for demos.
