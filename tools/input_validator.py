def validate_case(case: dict) -> list[str]:
    errors = []
    if case.get("category") not in {"electric_fan", "mixer_grinder"}:
        errors.append("Choose a supported appliance category.")
    try:
        age = float(case.get("age_years"))
        if age < 0 or age > 80: errors.append("Product age must be between 0 and 80 years.")
    except (TypeError, ValueError):
        errors.append("Product age must be a number.")
    for field, label in [("repair_quote_inr", "Repair quote"), ("replacement_price_inr", "Replacement price"), ("purchase_price_inr", "Purchase price")]:
        value = case.get(field)
        if value is not None and (not isinstance(value, (int, float)) or value < 0 or value > 1_000_000):
            errors.append(f"{label} must be between ₹0 and ₹10,00,000.")
    if case.get("warranty_status") not in {"unknown", "active", "expired", "not_applicable"}:
        errors.append("Choose a valid warranty status.")
    if not case.get("symptoms"):
        errors.append("Provide at least one symptom.")
    return errors
