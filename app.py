from __future__ import annotations

import json
import streamlit as st
from agent.orchestrator import assess_case
from tools.input_validator import validate_case

st.set_page_config(page_title="FixForward", page_icon="🔧", layout="wide")

st.markdown("""
<style>
.block-container {max-width: 1180px; padding-top: 2rem;}
.hero {padding: 1.5rem 1.8rem; border-radius: 18px; background: linear-gradient(120deg,#10243a,#174b50); color: white; margin-bottom: 1.2rem;}
.hero h1 {font-size: 2.6rem; margin: 0;}
.hero p {font-size: 1.05rem; opacity: .9; margin-bottom: 0;}
.small-muted {color: #6b7280; font-size: .88rem;}
</style>
<div class="hero">
  <h1>🔧 FixForward</h1>
  <p>Repair smarter. Replace responsibly. Make evidence-informed decisions about faulty appliances.</p>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.header("About this assessment")
    st.write("FixForward is decision support, not a physical diagnosis. It never instructs users to open or repair live electrical equipment.")
    st.caption("MVP scope: electric fans and mixer grinders.")
    st.divider()
    st.write("**Integration status**")
    st.write("Decider endpoint:", "Configured" if __import__("os").getenv("DECIDER_URL") else "Not configured (demo fallback)")
    st.write("Bedrock model:", "Configured" if __import__("os").getenv("BEDROCK_MODEL_ID") else "Not configured (deterministic explanation)")

with st.form("case_form"):
    st.subheader("Assess your appliance")
    c1, c2, c3 = st.columns(3)
    with c1:
        category = st.selectbox("Appliance", ["electric_fan", "mixer_grinder"], format_func=lambda x: "Electric fan" if x == "electric_fan" else "Mixer grinder")
        brand = st.text_input("Brand (optional)", placeholder="e.g., Example brand")
        age = st.number_input("Product age (years)", min_value=0, max_value=80, value=3, step=1)
    with c2:
        warranty = st.selectbox("Warranty status", ["unknown", "active", "expired", "not_applicable"])
        repair_quote = st.number_input("Repair quote (₹)", min_value=0, max_value=1_000_000, value=900, step=100)
        replacement_price = st.number_input("Comparable replacement price (₹)", min_value=0, max_value=1_000_000, value=2000, step=100)
    with c3:
        purchase_price = st.number_input("Original purchase price (₹, optional)", min_value=0, max_value=1_000_000, value=2500, step=100)
        remaining_years = st.number_input("Estimated years after repair", min_value=0, max_value=30, value=2, step=1)
        symptom = st.selectbox("Main symptom", [
            "unusual_noise", "not_switching_on", "overheating", "burning_smell",
            "smoke_or_sparks", "intermittent_operation", "physical_damage", "other"
        ], format_func=lambda x: x.replace("_", " ").capitalize())
    notes = st.text_area("Additional details (optional)", placeholder="When did it start? Has a technician inspected it?")
    submitted = st.form_submit_button("Assess next best step", type="primary", use_container_width=True)

if submitted:
    case = {
        "category": category, "brand": brand.strip(), "age_years": age,
        "warranty_status": warranty, "repair_quote_inr": repair_quote if repair_quote > 0 else None,
        "replacement_price_inr": replacement_price if replacement_price > 0 else None,
        "purchase_price_inr": purchase_price if purchase_price > 0 else None,
        "estimated_repair_years": remaining_years, "symptoms": [symptom],
        "notes": notes.strip()
    }
    errors = validate_case(case)
    if errors:
        st.error("Please fix the following inputs:")
        for error in errors: st.write(f"- {error}")
    else:
        with st.spinner("Checking safety, selecting a workflow, and preparing the assessment…"):
            result = assess_case(case)
        st.session_state["last_result"] = result
        st.session_state["last_case"] = case

if "last_result" in st.session_state:
    result = st.session_state["last_result"]
    case = st.session_state["last_case"]
    st.divider()
    st.subheader("Assessment")
    if result.get("safety", {}).get("hazard"):
        st.error("Safety warning: stop using the appliance and disconnect power only if this can be done safely. Do not open the unit. Seek qualified professional help.")
    c1, c2, c3 = st.columns(3)
    c1.metric("Selected workflow", result["decision"]["selected_action"].replace("_", " ").title())
    c2.metric("Decision latency", f'{result["decision"].get("latency_ms", 0):.0f} ms' if result["decision"].get("latency_ms") is not None else "N/A")
    c3.metric("Decision mode", result["decision"].get("mode", "unknown").replace("_", " ").title())
    st.markdown("### Recommended next step")
    st.write(result["recommendation"])
    if result.get("cost_comparison"):
        cost = result["cost_comparison"]
        m1, m2, m3 = st.columns(3)
        m1.metric("Repair quote", f'₹{cost["repair_cost_inr"]:,.0f}' if cost.get("repair_cost_inr") is not None else "Not supplied")
        m2.metric("Replacement", f'₹{cost["replacement_cost_inr"]:,.0f}' if cost.get("replacement_cost_inr") is not None else "Not supplied")
        m3.metric("Difference (replacement − repair)", f'₹{cost["replacement_minus_repair_inr"]:,.0f}' if cost.get("replacement_minus_repair_inr") is not None else "Cannot compare")
        st.caption(cost["interpretation"])
    st.markdown("### Explanation")
    st.write(result["explanation"])
    if result.get("evidence"):
        with st.expander("Evidence and retrieval results", expanded=True):
            for item in result["evidence"]:
                st.markdown(f"**{item['title']}** · `{item['source']}`")
                st.write(item["excerpt"])
    with st.expander("Decision trace (for transparency)"):
        st.json(result["decision"])
    with st.expander("Case data sent to the assessment"):
        st.json(case)
    st.download_button("Download assessment JSON", data=json.dumps(result, indent=2), file_name="fixforward-assessment.json", mime="application/json")
    st.caption("Estimates depend on user-supplied inputs. This is not a diagnosis, safety certification, or guarantee of repair outcome.")
