# 🏗️ System Architecture

This document describes how the **Doctor Notes App** is structured, what components it includes, and how they interact.  
It supports the project’s goal: building an **LLM-powered clinical note structuring app** that can later expand to include entity extraction, coding, and FHIR outputs.

---

## ⚙️ High-Level Overview

At this stage, the system has **two main components** and optional containerization:

- **Frontend (React)** — The user interface where clinicians type or upload notes.
- **Backend (FastAPI, Python)** — The AI service that analyzes and structures the notes.

---

## 🧩 Architecture Diagram

```mermaid
graph LR
    A[React Frontend] -->|POST /api/analyze| B[FastAPI Backend]
    B -->|JSON Summary| A
