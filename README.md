# FixForward — Repair smarter. Replace responsibly.

FixForward is an evidence-informed decision-support prototype for faulty electric fans and mixer grinders. It demonstrates **tool selection** with Strands Decider 2B, deterministic safety checks and cost arithmetic, document retrieval, and optional Amazon Bedrock explanations.

> This repository is a prototype. It does not diagnose physical faults, certify appliance safety, or provide DIY electrical repair instructions. Sample documents are explicitly illustrative and are not manufacturer manuals.

## What works in this repository

- Streamlit intake form and assessment view.
- Deterministic hazard gate for smoke/sparks, burning smell, and overheating.
- Transparent repair-vs-replacement upfront cost comparison.
- Local JSON document retrieval over clearly labeled illustrative notes.
- Optional Strands Decider HTTP integration.
- Optional Amazon Bedrock `Converse` explanation.
- Explicit fallback modes; the UI does not claim that a heuristic result came from Decider.
- pytest suite, Docker image, GitHub Actions CI, and AWS setup/deployment notes.

## Architecture

`Streamlit → validation → deterministic safety gate → Decider choice → selected workflow → optional Bedrock explanation → decision trace`

Decider endpoint requests use the official `/v1/systemone` shape. The Decider service can be run separately using the `strands-decider` package. The app and Decider service are separate processes; a local model requires sufficient RAM/CPU or a compatible GPU. The model download may be several GB.

## Quickstart — Windows PowerShell

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
streamlit run app.py
```

Open the local URL Streamlit prints. In demo mode, the app runs without AWS credentials. Demo mode is useful for testing the UI and deterministic logic, but **does not demonstrate a real Decider or Bedrock invocation**.

### Run tests

```powershell
pytest -q
```

## Enable real Strands Decider

In a second terminal, install the official package and launch a local HTTP server. Check the current official Strands Decider README for the latest model IDs and hardware requirements.

```powershell
pip install strands-decider
strands-decider serve StrandsAgents/strands-decider-2B-qwen3.5-v1-2610 --port 8000
```

Then in the app terminal set:

```powershell
$env:DECIDER_URL="http://127.0.0.1:8000"
streamlit run app.py
```

The app sends a typed `choice` question with five options. Confirm that the endpoint responds at `/v1/systemone` before demo day. Model identifiers change over time; choose an available supported model from the official project docs. If the Decider service fails, the app clearly marks its heuristic fallback. For a strict demo, set `$env:DECIDER_FAIL_CLOSED="true"` to prevent silent degraded routing.

## Enable Amazon Bedrock explanations

1. Configure AWS credentials using an AWS profile, IAM Identity Center, or the standard AWS credential chain. Do not hardcode access keys.
2. Confirm the selected foundation model is enabled and available in the chosen AWS Region.
3. Grant only the required `bedrock:InvokeModel` permission for that model.
4. Set the model ID and region in the environment.

PowerShell example:

```powershell
$env:AWS_PROFILE="your-profile"
$env:AWS_REGION="us-east-1"
$env:BEDROCK_MODEL_ID="your-enabled-model-id"
streamlit run app.py
```

The model ID above is a placeholder. If Bedrock is unavailable, the app returns a deterministic explanation and clearly notes the fallback.

## Configuration

| Variable | Purpose |
|---|---|
| `DECIDER_URL` | Base URL for Strands Decider's HTTP server; blank enables heuristic demo routing |
| `DECIDER_TIMEOUT_SECONDS` | Request timeout (default 8 seconds) |
| `DECIDER_FAIL_CLOSED` | If `true`, Decider failure routes to professional assessment instead of heuristic routing |
| `BEDROCK_MODEL_ID` | Enabled Bedrock model ID; blank disables model-generated explanations |
| `AWS_REGION` | Bedrock region |

`.env.example` documents configuration. This MVP intentionally avoids automatically loading `.env`; set environment variables in your shell or configure secrets in your deployment platform.

## Docker

```bash
docker build -t fixforward:local .
docker run --rm -p 8501:8501 \
  -e DECIDER_URL=http://host.docker.internal:8000 \
  -e AWS_REGION=us-east-1 \
  -e BEDROCK_MODEL_ID=your-enabled-model-id \
  fixforward:local
```

On Linux, `host.docker.internal` may require an explicit host-gateway mapping. Do not bake AWS credentials into the image. Prefer an IAM role in AWS deployments.

## AWS deployment notes

For a time-boxed hackathon, first demonstrate locally. A container deployment is optional and should only be attempted after the demo path is stable.

- Build and test the image locally.
- Push it to Amazon ECR.
- Deploy to an AWS container service such as App Runner or ECS/Fargate.
- Assign a task/instance role with least-privilege Bedrock access.
- Store secrets/configuration in the deployment environment or AWS Secrets Manager.
- Configure health checks, logs, HTTPS, and budget alarms.
- If the Decider runs locally on your laptop, an AWS-hosted app cannot reach `localhost`. Host the Decider in a reachable secured environment, or demonstrate both services locally.
- Do not expose an unauthenticated Decider endpoint publicly. Use network controls and authentication where applicable.

The supplied Dockerfile and GitHub Actions workflow are starter infrastructure, not proof that the app has been deployed to AWS.

## Decision behavior

Actions:
- `REQUEST_INFO`
- `CHECK_DOCUMENTS`
- `COMPARE_COSTS`
- `END_OF_LIFE`
- `PROFESSIONAL_ASSESSMENT`

The deterministic safety gate runs before ordinary routing. If a hazard is detected, it overrides the Decider. The heuristic router exists only for development resilience and is explicitly labeled.

## Important limitations

- Sample JSON documents are not manufacturer-approved sources; all have `verified: false`.
- The cost comparison is upfront only and does not estimate service life, maintenance, carbon impact, or repair quality.
- No live prices, warranty lookup, recycling directory, or repair marketplace is integrated.
- A successful model response is not proof of correctness. Review decisions against a labelled test set.
- Validate current Decider model availability and API behavior before relying on it in a public demonstration.

## Hackathon ship checklist

- [ ] Verify a real Decider request and show the actual selected action.
- [ ] Verify a real Bedrock `Converse` response.
- [ ] Replace illustrative documents with lawful, verified, relevant sources where possible.
- [ ] Run `pytest -q`.
- [ ] Record real latency and decision-mode traces.
- [ ] Publish a reusable `tool_selection` decision pattern and setup guide.
- [ ] Add Builder Center article and public demo video under three minutes.
- [ ] Confirm official tags and submission instructions on the hackathon page.
- [ ] Ensure no credentials or personal data are committed.
