# LLM-Powered Clinical Note Structuring App

This is a prototype application that captures doctor-patient encounters, uses a Large Language Model (LLM) to extract clinical entities, maps them to standardized medical codes (e.g., SNOMED CT, ICD-10), and outputs the data as FHIR-compliant resources.

## 🚀 Overview

- **Voice Input**: Doctors can upload voice recordings of clinical notes.
- **LLM Processing**: Transcribes and extracts relevant clinical entities.
- **Medical Coding**: Maps entities to SNOMED CT, ICD-10, or other coding systems.
- **FHIR Output**: Produces structured FHIR resources for interoperability.

## 🧠 Tech Stack

- **Frontend**: React
- **Backend**: FastAPI (Python)
- **LLM/NLP**: (Pluggable, placeholder for Whisper + entity mapping)
- **Data Standardization**: SNOMED CT, ICD-10, FHIR

## 📁 Project Structure

```
llm-doctor-notes/
├── server/             # FastAPI backend
│   ├── main.py         # API endpoints
│   ├── services/       # LLM and transcription logic
│   └── requirements.txt
├── src/                # React frontend
│   ├── components/     # UI components (e.g. UploadForm)
│   ├── App.js
│   └── index.js
├── public/             # HTML template
├── package.json
└── README.md
```

## 🛠️ Setup

### 1. Backend

```bash
cd server
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

### 2. Frontend

```bash
cd ..
npm install
npm start
```

The React app runs on `localhost:3000` and proxies requests to FastAPI on `localhost:8000`.

## 📤 Upload Flow

1. Doctor records or uploads an `.mp3`/`.wav` file
2. Audio sent to `/audio/upload`
3. Server transcribes and extracts structured clinical data
4. Returns mapped entities and FHIR resource JSON

## 📦 Future Enhancements

- Integrate OpenAI Whisper or WhisperX for real transcription
- Use scispaCy or MedCAT for medical entity recognition
- Add UI for editing structured output
- Support OAuth2 for secure access
- Store FHIR bundles in a compatible backend (e.g. HAPI FHIR server)

---

### 🧩 Development Progress
Current work: [Design a Service that Summarizes Patient Notes](./docs/plan.md)
