def compare_costs(case: dict) -> dict:
    repair = case.get("repair_quote_inr")
    replacement = case.get("replacement_price_inr")
    if repair is None or replacement is None:
        return {
            "repair_cost_inr": repair, "replacement_cost_inr": replacement,
            "replacement_minus_repair_inr": None,
            "interpretation": "A comparison requires both a repair quote and a comparable replacement price."
        }
    difference = replacement - repair
    if difference > 0:
        interpretation = f"The supplied repair quote is ₹{difference:,.0f} lower than the replacement price before maintenance and service-life differences."
    elif difference < 0:
        interpretation = f"The supplied repair quote is ₹{abs(difference):,.0f} higher than the replacement price before warranty and service-life differences."
    else:
        interpretation = "The supplied repair quote equals the replacement price; compare warranty, safety, and expected service life."
    return {
        "repair_cost_inr": round(float(repair), 2),
        "replacement_cost_inr": round(float(replacement), 2),
        "replacement_minus_repair_inr": round(float(difference), 2),
        "interpretation": interpretation,
        "limitations": "This is a simple upfront comparison. It excludes future maintenance, downtime, warranty, and uncertain remaining service life."
    }
