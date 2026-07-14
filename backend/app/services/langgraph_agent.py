from __future__ import annotations

import os
import json
from typing import Any, Dict, List, TypedDict

import requests
from langgraph.graph import END, START, StateGraph


class AgentState(TypedDict, total=False):
    mode: str
    raw_input: str
    structured_payload: Dict[str, Any]
    intent: str
    tools_used: List[str]
    tool_results: List[Dict[str, Any]]
    summary: str


INTERACTION_STORE: List[Dict[str, Any]] = []


def call_groq_llm(prompt: str, system_prompt: str = "You are an expert HCP field insights assistant.") -> str | None:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return None

    payload = {
        "model": "gemma2-9b-it",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.3,
        "max_tokens": 400,
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]
    except Exception:
        return None


def lookup_hcp_profile(payload: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "tool": "lookup_hcp_profile",
        "hcp": payload.get("hcp_name", "Unknown HCP"),
        "specialty": payload.get("specialty", "General Medicine"),
        "profile_score": 82,
        "notes": "Eligible for a follow-up on oncology education and time-sensitive sample access.",
    }


def assess_engagement_level(payload: Dict[str, Any]) -> Dict[str, Any]:
    objective = payload.get("objective", "")
    channel = payload.get("channel", "")
    return {
        "tool": "assess_engagement_level",
        "engagement": "High" if "follow-up" in objective.lower() or channel.lower() == "video" else "Medium",
        "signal": "Noted strong interest in therapeutic education and upcoming conference attendance.",
    }


def recommend_next_step(payload: Dict[str, Any]) -> Dict[str, Any]:
    objective = payload.get("objective", "")
    next_step = "Share a product comparison brief and schedule a 20-minute scientific discussion." if objective else "Schedule a follow-up touchpoint within 72 hours."
    return {
        "tool": "recommend_next_step",
        "next_action": next_step,
        "priority": "High",
    }


def generate_follow_up_email(payload: Dict[str, Any]) -> Dict[str, Any]:
    hcp_name = payload.get("hcp_name", "the HCP")
    return {
        "tool": "generate_follow_up_email",
        "email_draft": f"Hi {hcp_name}, thanks again for the discussion. I will share the latest evidence summary and propose a follow-up at your earliest convenience.",
    }


def update_opportunity_status(payload: Dict[str, Any]) -> Dict[str, Any]:
    objective = payload.get("objective", "")
    status = "Qualified" if objective else "Open"
    return {
        "tool": "update_opportunity_status",
        "status": status,
        "crm_note": "Interaction logged and a next-step task created for the field representative.",
    }


def classify_input(state: AgentState) -> AgentState:
    payload = state.get("structured_payload") or {}
    raw_input = state.get("raw_input") or ""
    text = raw_input or " ".join([payload.get("hcp_name", ""), payload.get("objective", ""), payload.get("notes", "")])
    if payload:
        mode = "structured"
    else:
        mode = "chat"

    prompt = f"Classify this CRM interaction into intent and update the summary. Text: {text}"
    llm_hint = call_groq_llm(prompt)
    intent = "follow_up" if llm_hint else "capture"
    state["mode"] = mode
    state["intent"] = intent
    return state


def run_tools(state: AgentState) -> AgentState:
    payload = state.get("structured_payload") or {}
    tools_used: List[str] = []
    tool_results: List[Dict[str, Any]] = []

    for tool in [
        lookup_hcp_profile,
        assess_engagement_level,
        recommend_next_step,
        generate_follow_up_email,
        update_opportunity_status,
    ]:
        result = tool(payload)
        tools_used.append(result["tool"])
        tool_results.append(result)

    state["tools_used"] = tools_used
    state["tool_results"] = tool_results

    INTERACTION_STORE.append({
        "mode": state.get("mode"),
        "intent": state.get("intent"),
        "payload": payload,
        "tools_used": tools_used,
    })
    return state


def summarize_result(state: AgentState) -> AgentState:
    payload = state.get("structured_payload") or {}
    tool_results = state.get("tool_results") or []
    summary_text = "Interaction recorded successfully. "
    for result in tool_results:
        summary_text += f"{result['tool']}: {result.get('next_action') or result.get('status') or result.get('email_draft') or result.get('notes')} "

    prompt = f"Turn the following tool results into a concise CRM interaction summary. Tool results: {json.dumps(tool_results)}"
    llm_summary = call_groq_llm(prompt)
    state["summary"] = llm_summary or summary_text
    return state


def build_interaction_plan(payload: Dict[str, Any], raw_input: str = "") -> Dict[str, Any]:
    workflow = StateGraph(AgentState)
    workflow.add_node("classify", classify_input)
    workflow.add_node("run_tools", run_tools)
    workflow.add_node("summarize", summarize_result)
    workflow.add_edge(START, "classify")
    workflow.add_edge("classify", "run_tools")
    workflow.add_edge("run_tools", "summarize")
    workflow.add_edge("summarize", END)

    app = workflow.compile()
    result = app.invoke({"structured_payload": payload, "raw_input": raw_input})
    return {
        "mode": result.get("mode", "structured"),
        "intent": result.get("intent", "capture"),
        "tools_used": result.get("tools_used", []),
        "tool_results": result.get("tool_results", []),
        "summary": result.get("summary", "Interaction logged."),
    }
