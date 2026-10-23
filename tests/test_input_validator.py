from tools.input_validator import validate_case

def test_valid_case():
    case = {"category":"electric_fan","age_years":3,"warranty_status":"unknown","repair_quote_inr":900,"replacement_price_inr":2000,"purchase_price_inr":2500,"symptoms":["unusual_noise"]}
    assert validate_case(case) == []

def test_rejects_negative_cost():
    case = {"category":"electric_fan","age_years":3,"warranty_status":"unknown","repair_quote_inr":-1,"replacement_price_inr":2000,"symptoms":["unusual_noise"]}
    assert validate_case(case)
