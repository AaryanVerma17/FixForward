from __future__ import annotations

import time
from tools.safety_screen import screen_safety
from tools.cost_engine import compare_costs
from tools.document_retriever import retrieve_documents
from tools.end_of_life import end_of_life_guidance
from agent.decider_router import choose_action
from services.bedrock_explainer import explain_assessment

def assess_case(case: dict) -> dict:
    started = time.perf_counter()
    safety = screen_safety(case)
    # Deterministic safety gate always takes precedence over model routing.
    if safety["hazard"]:
        action = {"selected_action": "PROFESSIONAL_ASSESSMENT", "confidence": 1.0,
                  "latency_ms": 0.0, "mode": "deterministic_safety_override",
                  "reason": safety["reason"], "candidate_actions": []}
        evidence = retrieve_documents(case)
        costs = None
    else:
        decision = choose_action(case)
        action = decision
        evidence = []
        costs = None
        if action["selected_action"] == "REQUEST_INFO":
            action["reason"] = action.get("reason") or "Essential information is missing before a useful comparison can be made."
        elif action["selected_action"] == "CHECK_DOCUMENTS":
            evidence = retrieve_documents(case)
        elif action["selected_action"] == "COMPARE_COSTS":
            costs = compare_costs(case)
        elif action["selected_action"] == "END_OF_LIFE":
            action["reason"] = end_of_life_guidance(case)
        elif action["selected_action"] == "PROFESSIONAL_ASSESSMENT":
            action["reason"] = "The symptoms or uncertainty warrant assessment by a qualified technician."
    payload = {
        "case": case, "safety": safety, "decision": action,
        "cost_comparison": costs, "evidence": evidence,
        "elapsed_ms": (time.perf_counter() - started) * 1000
    }
    payload["explanation"] = explain_assessment(payload)
    payload["recommendation"] = _recommendation(payload)
    return payload

def _recommendation(result: dict) -> str:
    if result["safety"]["hazard"]:
        return "Stop using the appliance. Do not open it or attempt a repair. Arrange a qualified inspection; if there is smoke or fire, move away and contact local emergency services."
    action = result["decision"]["selected_action"]
    choices = {
        "REQUEST_INFO": "Provide the missing cost or product information before deciding. Do not infer unknown values.",
        "CHECK_DOCUMENTS": "Check the product's verified manual and warranty terms before paying for repair.",
        "COMPARE_COSTS": "Review the cost comparison alongside safety, warranty, and expected remaining service life.",
        "END_OF_LIFE": "Explore manufacturer take-back, authorized e-waste collection, or repair/reuse options. Verify local rules and availability.",
        "PROFESSIONAL_ASSESSMENT": "Ask a qualified technician to inspect the appliance before deciding whether repair is practical."
    }
    return choices.get(action, "Gather more information and consult a qualified professional if the fault is uncertain.")
