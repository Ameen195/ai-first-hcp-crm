# AI-First CRM HCP Module

This repository contains a lightweight prototype for an AI-first CRM HCP module with:

- React + Redux frontend for the Log Interaction Screen
- FastAPI backend for request handling
- LangGraph-based orchestration with five sales-oriented tools
- Groq integration using the Gemma 2 9B Instruct model when a GROQ_API_KEY is available

## Architecture

- Frontend: React + Redux
- Backend: Python + FastAPI
- AI orchestration: LangGraph
- LLM: Groq (Gemma 2 9B IT)

## Run the backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Set the environment variable before running:

```bash
set GROQ_API_KEY=your_key_here
```

## Run the frontend

```bash
cd frontend
npm install
npm start
```


## Demo

1. Open the app in the browser.
2. Enter an HCP name, specialty, objective, and notes.
3. Submit the form to trigger the LangGraph workflow.
4. Review the generated CRM summary, tool usage, and recommended next step.

## LangGraph tools included

1. lookup_hcp_profile
2. assess_engagement_level
3. recommend_next_step
4. generate_follow_up_email
5. update_opportunity_status
