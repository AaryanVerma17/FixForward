from tools.cost_engine import compare_costs

def test_difference_positive_when_repair_is_cheaper():
    result = compare_costs({"repair_quote_inr": 900, "replacement_price_inr": 2000})
    assert result["replacement_minus_repair_inr"] == 1100
    assert "lower" in result["interpretation"]

def test_missing_cost_does_not_invent_comparison():
    result = compare_costs({"repair_quote_inr": 900, "replacement_price_inr": None})
    assert result["replacement_minus_repair_inr"] is None

def test_repair_more_expensive_than_replacement():
    result = compare_costs({"repair_quote_inr": 2500, "replacement_price_inr": 2000})
    assert result["replacement_minus_repair_inr"] == -500
