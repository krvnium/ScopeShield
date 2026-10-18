"""Streamlit UI for the local-first ScopeShield auditor."""

from __future__ import annotations

import streamlit as st

from ai_engine import audit_scope
from db import (
    calculate_total_revenue_saved,
    get_dashboard_totals,
    init_db,
    insert_contract,
    save_change_order,
)
from pdf_parser import extract_pages, generate_sample_contract


def total_cost(hours: float, rate: float) -> float:
    return round(max(0.0, hours) * max(0.0, rate), 2)


def load_contract(title: str, pdf_bytes: bytes) -> None:
    pages = extract_pages(pdf_bytes)
    if not pages:
        raise ValueError("The PDF contains no readable text.")
    st.session_state.contract = {
        "id": insert_contract(title, pages),
        "title": title,
        "pages": pages,
    }
    st.session_state.audit = None


def main() -> None:
    st.set_page_config(page_title="ScopeShield", page_icon="🛡️", layout="wide")
    init_db()
    st.title("🛡️ ScopeShield")
    st.caption("Freelance Scope Creep Auditor & Change-Order Generator")

    metrics = get_dashboard_totals()
    first, second, third = st.columns(3)
    first.metric("Total Contracts Audited", metrics["contracts"])
    second.metric("Scope Creep Requests Caught", metrics["caught"])
    third.metric("Total Revenue Saved", f"${calculate_total_revenue_saved():,.2f}")

    with st.sidebar:
        st.header("Project setup")
        rate = st.number_input("Hourly rate ($)", min_value=0.0, value=75.0, step=5.0)
        uploaded = st.file_uploader("Upload contract PDF", type="pdf")
        if st.button("Load Sample Web Dev Contract", use_container_width=True):
            try:
                load_contract("Sample Web Dev Contract", generate_sample_contract())
                st.success("Sample contract loaded.")
            except ValueError as exc:
                st.error(str(exc))
        if uploaded is not None and st.session_state.get("uploaded_name") != uploaded.name:
            try:
                load_contract(uploaded.name, uploaded.getvalue())
                st.session_state.uploaded_name = uploaded.name
            except ValueError as exc:
                st.error(str(exc))

    contract = st.session_state.get("contract")
    if not contract:
        st.info("Load the sample contract or upload a PDF to begin.")
        return

    st.success(f"Auditing: {contract['title']}")
    message = st.text_area("Paste the client's message", height=160)

    if st.button("Audit Scope", type="primary", disabled=not message.strip()):
        with st.spinner("Reviewing the contract..."):
            try:
                st.session_state.audit = audit_scope(contract["pages"], message)
            except (RuntimeError, ValueError) as exc:
                st.error(str(exc))

    result = st.session_state.get("audit")
    if not result:
        return
    st.subheader("Audit result")
    verdict = result["verdict"].replace("_", " ").title()
    st.write(f"**Verdict:** {verdict}")
    st.write(f"**Requested feature:** {result['requested_feature_summary']}")
    st.write(
        f"**Cited clause (page {result['page_number']}):** "
        f"{result['cited_clause']}"
    )
    st.write(result["reasoning"])
    hours = st.slider(
        "Adjust estimated hours",
        min_value=0.0,
        max_value=200.0,
        value=float(result["estimated_hours"]),
        step=0.5,
    )
    cost = total_cost(hours, rate)
    st.metric(
        "Change-order total",
        f"${cost:,.2f}",
        f"{hours:g} h × ${rate:,.2f}/h",
    )
    reply = result["diplomatic_reply"].replace(
        "[TOTAL_COST]", f"${cost:,.2f}"
    ).replace("{total_cost}", f"${cost:,.2f}")
    st.info(reply)
    st.caption(f"Invoice line item: {result['invoice_line_item']}")

    if st.button("Confirm & Log Change Order"):
        save_change_order(
            contract["id"],
            result["requested_feature_summary"],
            verdict,
            int(result["page_number"]) if result["page_number"] else None,
            hours,
            rate,
            cost,
        )
        st.session_state.audit = None
        st.success("Change order confirmed and saved.")
        st.rerun()


if __name__ == "__main__":
    main()
