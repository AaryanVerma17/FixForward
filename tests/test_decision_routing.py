from agent.decider_router import _heuristic_decision

def test_missing_costs_requests_info():
    result = _heuristic_decision({"missing_fields": ["repair quote or replacement price"], "repair_quote_inr": None, "replacement_price_inr": None, "warranty_status": "expired", "symptoms": []})
    assert result["selected_action"] == "REQUEST_INFO"
    assert result["mode"] == "heuristic_demo"

def test_unknown_warranty_checks_documents():
    result = _heuristic_decision({"missing_fields": [], "repair_quote_inr": 900, "replacement_price_inr": 2000, "warranty_status": "unknown", "symptoms": []})
    assert result["selected_action"] == "CHECK_DOCUMENTS"
