# Architecture and operational notes

## Request lifecycle
1. Streamlit collects structured inputs.
2. `input_validator` rejects malformed values.
3. `safety_screen` runs deterministic rules.
4. Hazardous cases bypass routine routing and go to professional assessment.
5. Non-hazard cases are sent to Decider if `DECIDER_URL` is configured; otherwise a clearly labeled heuristic is used.
6. The selected action runs a local workflow.
7. Optional Bedrock `Converse` generates an explanation from structured results.
8. The app displays the result and supports JSON export.

## Trust boundaries
- User input is untrusted.
- Retrieved documents are not automatically authoritative; source and verification state are shown.
- Model-generated explanation cannot override deterministic safety rules.
- Credentials come from AWS credential providers or runtime roles, never from source control.

## Failure behavior
- Decider timeout: explicit heuristic fallback or safe fail-closed mode.
- Bedrock error: deterministic explanation with an explicit fallback note.
- Missing costs: no fabricated comparison.
- No retrieved documents: explicit statement that evidence was not found.
