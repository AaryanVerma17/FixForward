# Evaluation plan

## Initial labelled cases
Create at least 15 cases spanning:
- complete repair and replacement prices;
- missing one or both prices;
- unknown warranty;
- overheating, burning smell, smoke/sparks;
- uncertain symptoms;
- repair quote above replacement price;
- unsupported category;
- Decider timeout / malformed response;
- Bedrock failure and no matching evidence.

## Metrics
- Action accuracy against expected action.
- Hazard interception rate for the defined test suite.
- Unsupported-choice rejection rate.
- Fallback rate.
- Decider and end-to-end latency (median and p95).
- Bedrock error rate and estimated cost if pricing is available.
- Evidence support review: proportion of factual claims traceable to supplied documents or deterministic calculations.

## Baseline
Compare the Decider route with a defined baseline on the same labelled cases. Do not claim performance improvements without measured evidence. Report hardware, model version, number of cases, and failed calls.
