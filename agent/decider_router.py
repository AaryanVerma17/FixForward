from __future__ import annotations

import json
import os
import time
import urllib.request
import urllib.error

ACTIONS = ["REQUEST_INFO", "CHECK_DOCUMENTS", "COMPARE_COSTS", "END_OF_LIFE", "PROFESSIONAL_ASSESSMENT"]

def _missing(case: dict) -> list[str]:
    missing = []
    if case.get("replacement_price_inr") is None and case.get("repair_quote_inr") is None:
        missing.append("repair quote or replacement price")
    if case.get("warranty_status", "unknown") == "unknown":
        missing.append("warranty status")
    return missing

def choose_action(case: dict) -> dict:
    state = {
        "category": case.get("category"), "age_years": case.get("age_years"),
        "symptoms": case.get("symptoms", []), "warranty_status": case.get("warranty_status"),
        "repair_quote_inr": case.get("repair_quote_inr"),
        "replacement_price_inr": case.get("replacement_price_inr"),
        "missing_fields": _missing(case), "notes": case.get("notes", "")
    }
    endpoint = os.getenv("DECIDER_URL", "").strip().rstrip("/")
    if endpoint:
        try:
            return _remote_decision(endpoint, state)
        except Exception as exc:
            if os.getenv("DECIDER_FAIL_CLOSED", "false").lower() == "true":
                return {"selected_action": "PROFESSIONAL_ASSESSMENT", "confidence": None,
                        "latency_ms": None, "mode": "safe_fallback",
                        "reason": f"Decider unavailable; safe fallback used ({type(exc).__name__}).",
                        "candidate_actions": ACTIONS, "fallback_used": True}
            # Keep the app available but make degraded mode explicit.
            result = _heuristic_decision(state)
            result["mode"] = "heuristic_fallback"
            result["fallback_used"] = True
            result["reason"] = f"Decider endpoint unavailable; transparent fallback used ({type(exc).__name__})."
            return result
    return _heuristic_decision(state)

def _remote_decision(endpoint: str, state: dict) -> dict:
    # Compatible with the official strands-decider HTTP server's /v1/systemone API.
    # Start it with: strands-decider serve StrandsAgents/strands-decider-2B-hobson-v19 --port 8000
    body = {
        "state": json.dumps(state, ensure_ascii=False),
        "questions": {
            "next_action": {
                "type": "choice",
                "instructions": "Choose the single most useful next workflow for this appliance case. Missing essential cost data means REQUEST_INFO. Unknown warranty means CHECK_DOCUMENTS. If complete cost data exists, choose COMPARE_COSTS unless professional inspection or end-of-life guidance is clearly more appropriate. Do not override safety checks.",
                "criteria": {action: action.replace("_", " ").title() for action in ACTIONS}
            }
        }
    }
    request = urllib.request.Request(
        endpoint + "/v1/systemone", data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json"}, method="POST"
    )
    started = time.perf_counter()
    with urllib.request.urlopen(request, timeout=float(os.getenv("DECIDER_TIMEOUT_SECONDS", "8"))) as response:
        payload = json.loads(response.read().decode("utf-8"))
    elapsed = (time.perf_counter() - started) * 1000
    answer = payload.get("answers", {}).get("next_action", {})
    selected = answer.get("choice")
    if selected not in ACTIONS:
        raise ValueError("Decider returned an unsupported action")
    return {
        "selected_action": selected,
        "confidence": answer.get("confidence"),
        "probabilities": answer.get("probabilities"),
        "latency_ms": payload.get("latency_ms", elapsed),
        "mode": "strands_decider_2b",
        "reason": "Selected by the configured Strands Decider endpoint.",
        "candidate_actions": ACTIONS,
        "fallback_used": False
    }

def _heuristic_decision(state: dict) -> dict:
    missing = state["missing_fields"]
    if missing and state.get("repair_quote_inr") is None and state.get("replacement_price_inr") is None:
        selected = "REQUEST_INFO"
    elif state.get("warranty_status") == "unknown":
        selected = "CHECK_DOCUMENTS"
    elif state.get("symptoms") and any(s in state["symptoms"] for s in ["intermittent_operation", "physical_damage", "other"]):
        selected = "PROFESSIONAL_ASSESSMENT"
    elif state.get("repair_quote_inr") is not None and state.get("replacement_price_inr") is not None:
        selected = "COMPARE_COSTS"
    else:
        selected = "REQUEST_INFO"
    return {
        "selected_action": selected, "confidence": None, "probabilities": None,
        "latency_ms": 0.0, "mode": "heuristic_demo",
        "reason": "No Decider endpoint configured; deterministic demo routing used. This is not a Decider result.",
        "candidate_actions": ACTIONS, "fallback_used": False
    }
