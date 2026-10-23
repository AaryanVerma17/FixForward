# Reusable pattern: typed tool selection

## Purpose
Choose the next workflow from a finite set of actions based on the validated case state.

## Question
`Which workflow should execute next for this case?`

## Options
`REQUEST_INFO`, `CHECK_DOCUMENTS`, `COMPARE_COSTS`, `END_OF_LIFE`, `PROFESSIONAL_ASSESSMENT`

## Integration
The app sends the validated state to the Strands Decider `/v1/systemone` API as a `choice` question. It maps the returned choice to a fixed allowlist and executes only the corresponding local workflow.

## Guardrails
1. Deterministic validation runs before model routing.
2. Deterministic safety screening runs before normal routing and overrides it for defined hazards.
3. Returned choices outside the allowlist are rejected.
4. Low confidence should be calibrated on a labelled evaluation set before defining a threshold.
5. A Decider service error is explicitly logged and marked; demo fallback must never be presented as a Decider result.

## Evaluation
Use `tests/test_decision_routing.py` and extend it with labelled examples. Compare Decider against a clearly specified baseline, using identical cases and reporting sample size, accuracy, latency, failure rate, and measured costs where available.
