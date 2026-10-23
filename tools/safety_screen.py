HAZARDOUS_SYMPTOMS = {"burning_smell", "smoke_or_sparks", "overheating"}

def screen_safety(case: dict) -> dict:
    symptoms = set(case.get("symptoms", []))
    hazards = sorted(symptoms.intersection(HAZARDOUS_SYMPTOMS))
    if hazards:
        return {"hazard": True, "flags": hazards,
                "reason": "Reported symptom(s) indicate a potential electrical or thermal hazard: " + ", ".join(hazards)}
    return {"hazard": False, "flags": [], "reason": "No predefined hazard symptom was reported; this does not certify the appliance as safe."}
