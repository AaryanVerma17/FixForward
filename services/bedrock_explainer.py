from __future__ import annotations
import json
import os

def explain_assessment(result: dict) -> str:
    model_id = os.getenv("BEDROCK_MODEL_ID", "").strip()
    if model_id:
        try:
            return _bedrock_explanation(result, model_id)
        except Exception as exc:
            return _deterministic_explanation(result) + f"\n\nNote: Bedrock explanation was unavailable ({type(exc).__name__}); this fallback is deterministic."
    return _deterministic_explanation(result) + "\n\nDemo mode: configure BEDROCK_MODEL_ID and AWS credentials to enable Amazon Bedrock."

def _bedrock_explanation(result: dict, model_id: str) -> str:
    import boto3
    region = os.getenv("AWS_REGION") or os.getenv("AWS_DEFAULT_REGION") or "us-east-1"
    client = boto3.client("bedrock-runtime", region_name=region)
    context = {
        "safety": result["safety"], "decision": result["decision"],
        "cost_comparison": result.get("cost_comparison"),
        "evidence": result.get("evidence", []),
        "case": result.get("case")
    }
    prompt = (
        "You are FixForward, a cautious appliance repair decision-support assistant. "
        "Explain only the supplied facts. Do not diagnose a physical fault, invent warranty terms, "
        "claim a document is verified unless its verified field is true, or give instructions to open "
        "or repair electrical equipment. Treat a hazard flag as overriding all cost reasoning. "
        "Clearly separate supplied facts, calculations, assumptions, and uncertainty. Keep the answer concise. "
        "Assessment JSON:\n" + json.dumps(context, ensure_ascii=False)
    )
    response = client.converse(
        modelId=model_id,
        messages=[{"role": "user", "content": [{"text": prompt}]}],
        inferenceConfig={"maxTokens": 450, "temperature": 0.2}
    )
    return "".join(part.get("text", "") for part in response["output"]["message"]["content"])

def _deterministic_explanation(result: dict) -> str:
    safety = result["safety"]
    action = result["decision"]["selected_action"]
    lines = []
    if safety["hazard"]:
        lines.append("Safety takes priority. A reported warning symptom triggered the deterministic safety gate.")
        lines.append("Do not use the appliance or attempt a DIY repair; seek qualified help.")
        return "\n".join(lines)
    lines.append(f"The selected next workflow is {action.replace('_', ' ').lower()}.")
    costs = result.get("cost_comparison")
    if costs:
        lines.append(costs["interpretation"])
        lines.append(costs.get("limitations", ""))
    if result.get("evidence"):
        lines.append("Retrieved material is shown in the evidence panel. Check the source and applicability to the exact model before relying on it.")
    else:
        lines.append("No matching document evidence was retrieved for this case. Warranty and product-specific claims remain unverified.")
    lines.append("This assessment does not establish the physical cause of the fault. A technician may need to inspect the appliance.")
    return " ".join(line for line in lines if line)
