"""Streamlit frontend for the MIRA Health Prediction app.

Run with:  streamlit run streamlit_app.py
(The FastAPI backend must be running first: uvicorn app.main:app --reload)

This file never touches the database directly - it only calls the REST API.

Navigation uses a sidebar radio instead of tabs on purpose: every page
change is a real interaction, so the script reruns and data is always
fresh - no manual refresh needed.
"""

import os
from datetime import date

import pandas as pd
import requests
import streamlit as st

from ui.home import render_charts, render_home, render_sidebar_steps, render_stats
from ui.styles import inject_css

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")
PATIENTS = f"{API_URL}/api/patients"

st.set_page_config(
    page_title="MIRA - Health Prediction",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_css()

# ---------------------------------------------------------------- helpers ---

def risk_level(remarks: str) -> str:
    if "High Risk" in remarks:
        return "High"
    if "Moderate Risk" in remarks:
        return "Moderate"
    return "Low"


RISK_EMOJI = {"Low": "🟢", "Moderate": "🟡", "High": "🔴"}
RISK_CSS = {"Low": "risk-low", "Moderate": "risk-moderate", "High": "risk-high"}


def risk_card(remarks: str):
    """Show the AI remark in a colour-coded card."""
    level = risk_level(remarks)
    st.markdown(
        f'<div class="risk-card {RISK_CSS[level]}">'
        f"<strong>{RISK_EMOJI[level]} AI Result — {level} Risk</strong><br>{remarks}</div>",
        unsafe_allow_html=True,
    )


def section(title: str, subtitle: str = ""):
    st.markdown(f'<div class="section-title">{title}</div>', unsafe_allow_html=True)
    if subtitle:
        st.markdown(f'<div class="section-sub">{subtitle}</div>', unsafe_allow_html=True)


def api_error_text(response: requests.Response) -> str:
    """Convert FastAPI/Pydantic error responses into a readable message."""
    try:
        detail = response.json().get("detail")
        if isinstance(detail, str):
            return detail
        if isinstance(detail, list):  # Pydantic validation errors
            return "; ".join(f"{e['loc'][-1]}: {e['msg']}" for e in detail)
    except Exception:
        pass
    return f"Request failed (HTTP {response.status_code})"


def fetch_patients() -> list[dict]:
    response = requests.get(PATIENTS, timeout=10)
    response.raise_for_status()
    return response.json()


def patient_form(defaults: dict | None = None, key: str = "form"):
    """Reusable Add/Edit form. Returns the submitted payload or None."""
    d = defaults or {}
    with st.form(key=key):
        col_a, col_b = st.columns(2)
        full_name = col_a.text_input(
            "👤 Full Name", value=d.get("full_name", ""), placeholder="e.g. Asha Patel"
        )
        email = col_b.text_input(
            "📧 Email Address", value=d.get("email", ""), placeholder="e.g. asha@example.com"
        )
        dob = st.date_input(
            "🎂 Date of Birth",
            value=date.fromisoformat(d["date_of_birth"]) if d else date(2000, 1, 1),
            min_value=date(1900, 1, 1),
            max_value=date.today(),  # future dates are impossible to pick
        )

        st.markdown("**🩸 Blood Test Values**")
        col1, col2, col3 = st.columns(3)
        glucose = col1.number_input(
            "Glucose (mg/dL)", min_value=1.0, max_value=1000.0,
            value=float(d.get("glucose", 90.0)), step=0.1,
            help="Fasting glucose. Normal range: 70-99 mg/dL",
        )
        haemoglobin = col2.number_input(
            "Haemoglobin (g/dL)", min_value=1.0, max_value=30.0,
            value=float(d.get("haemoglobin", 14.0)), step=0.1,
            help="Normal range: 12-17.5 g/dL",
        )
        cholesterol = col3.number_input(
            "Cholesterol (mg/dL)", min_value=1.0, max_value=1000.0,
            value=float(d.get("cholesterol", 180.0)), step=0.1,
            help="Total cholesterol. Desirable: below 200 mg/dL",
        )

        st.caption("🤖 The AI remark is generated automatically after saving.")
        submitted = st.form_submit_button(
            "💾 Save Patient", type="primary", use_container_width=True
        )

    if not submitted:
        return None

    # Basic client-side checks (the API validates everything again).
    if len(full_name.strip()) < 2:
        st.error("Full name must have at least 2 characters.")
        return None
    if "@" not in email or "." not in email.split("@")[-1]:
        st.error("Please enter a valid email address.")
        return None

    return {
        "full_name": full_name.strip(),
        "date_of_birth": dob.isoformat(),
        "email": email.strip(),
        "glucose": glucose,
        "haemoglobin": haemoglobin,
        "cholesterol": cholesterol,
    }


def patient_label(p: dict) -> str:
    return f"{RISK_EMOJI[risk_level(p['remarks'])]} #{p['id']} — {p['full_name']} ({p['email']})"


PAGES = ["🏠 Home", "📊 Dashboard", "➕ Add Patient", "✏️ Update Patient", "🗑️ Delete Patient"]


def go_to(page_name: str):
    """Button callback: changes the current page (callbacks run before the rerun)."""
    st.session_state.nav = page_name


def _radio_changed():
    st.session_state.nav = st.session_state.nav_radio


# --------------------------------------------------------------- navigation ---

# "nav" is the single source of truth for the current page. The sidebar radio
# is only rendered on inner pages and is kept in sync with it.
page = st.session_state.setdefault("nav", "🏠 Home")

if page == "🏠 Home":
    # Hide the sidebar completely on the landing page (including the
    # little arrow that would re-open it). Navigation happens through
    # the hero buttons instead.
    st.markdown(
        """
        <style>
          section[data-testid="stSidebar"],
          [data-testid="stSidebarCollapsedControl"],
          [data-testid="collapsedControl"] { display: none !important; }
        </style>
        """,
        unsafe_allow_html=True,
    )
else:
    with st.sidebar:
        st.markdown('<div class="sidebar-brand">🩺 MIRA</div>', unsafe_allow_html=True)
        st.caption("Medical Intelligence Robotic Automation")
        st.divider()

        # Keep the radio in sync when the page was changed by a button.
        if st.session_state.get("nav_radio") != page:
            st.session_state.nav_radio = page

        st.radio(
            "Navigation",
            PAGES,
            label_visibility="collapsed",
            key="nav_radio",
            on_change=_radio_changed,
        )

        st.divider()
        render_sidebar_steps()

        st.divider()
        with st.expander("📖 Normal reference ranges"):
            st.markdown(
                """
                | Test | Normal |
                |---|---|
                | Glucose | 70–99 mg/dL |
                | Haemoglobin | 12–17.5 g/dL |
                | Cholesterol | < 200 mg/dL |
                """
            )
        st.caption("⚠️ Demo project — not medical advice.")

# Stop early with a friendly message if the backend is not running.
try:
    requests.get(API_URL, timeout=3)
except requests.ConnectionError:
    st.error(
        "🔌 Cannot reach the backend API. Start it first:\n\n"
        "`uvicorn app.main:app --reload`"
    )
    st.stop()

# Show a success message saved before the last rerun (e.g. after a delete).
if flash := st.session_state.pop("flash", None):
    st.success(flash)

# Data is re-fetched on EVERY interaction, so it is always up to date.
all_patients = fetch_patients()

# Inner pages get a compact banner and a one-click way back home.
if page != "🏠 Home":
    st.markdown(
        """
        <div class="hero">
          <h1>🩺 MIRA — Health Prediction</h1>
          <p>Patient blood test records with AI-generated health risk analysis</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.button("← Back to Home", on_click=go_to, args=("🏠 Home",))

# ------------------------------------------------------------------- HOME ---
if page == "🏠 Home":
    render_home(go_to)

# -------------------------------------------------------------- DASHBOARD ---
elif page == "📊 Dashboard":
    render_stats(all_patients)
    st.write("")

    if not all_patients:
        st.info("👋 No patients yet. Open **➕ Add Patient** in the sidebar to create the first record.")
    else:
        f1, f2 = st.columns([3, 2])
        search = f1.text_input(
            "🔍 Search", placeholder="Search by name or email...", label_visibility="collapsed"
        )
        risk_filter = f2.multiselect(
            "Filter by risk",
            options=["Low", "Moderate", "High"],
            placeholder="Filter by risk level",
            label_visibility="collapsed",
        )

        filtered = [
            p for p in all_patients
            if (not search or search.lower() in p["full_name"].lower()
                or search.lower() in p["email"].lower())
            and (not risk_filter or risk_level(p["remarks"]) in risk_filter)
        ]

        if not filtered:
            st.warning("No patients match your search.")
        else:
            df = pd.DataFrame(filtered)
            df["risk"] = df["remarks"].apply(lambda r: f"{RISK_EMOJI[risk_level(r)]} {risk_level(r)}")
            df = df[["id", "full_name", "date_of_birth", "email",
                     "glucose", "haemoglobin", "cholesterol", "risk", "remarks"]]

            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "id": st.column_config.NumberColumn("ID", width="small"),
                    "full_name": "Full Name",
                    "date_of_birth": "Date of Birth",
                    "email": "Email",
                    "glucose": st.column_config.NumberColumn("Glucose (mg/dL)", format="%.1f"),
                    "haemoglobin": st.column_config.NumberColumn("Haemoglobin (g/dL)", format="%.1f"),
                    "cholesterol": st.column_config.NumberColumn("Cholesterol (mg/dL)", format="%.1f"),
                    "risk": st.column_config.TextColumn("Risk", width="small"),
                    "remarks": st.column_config.TextColumn("Remarks (AI)", width="large"),
                },
            )

            st.write("")
            render_charts(filtered)

            st.markdown("##### ⬇️ Export Data")
            e1, e2 = st.columns([1, 3])
            e1.download_button(
                "Download as CSV",
                df.to_csv(index=False).encode("utf-8"),
                file_name="patients.csv",
                mime="text/csv",
                use_container_width=True,
            )
            e2.caption(f"{len(filtered)} of {len(all_patients)} record(s) shown")

# ----------------------------------------------------------------- CREATE ---
elif page == "➕ Add Patient":
    section("➕ Add a New Patient",
            "Fill in the details — the AI analyses the blood values the moment you save.")
    payload = patient_form(key="add_form")
    if payload:
        with st.spinner("Saving and running AI prediction..."):
            response = requests.post(PATIENTS, json=payload, timeout=30)
        if response.status_code == 201:
            created = response.json()
            st.success(f"✅ Patient **{created['full_name']}** created successfully!")
            risk_card(created["remarks"])
            if risk_level(created["remarks"]) == "Low":
                st.balloons()
        else:
            st.error(f"❌ {api_error_text(response)}")

# ----------------------------------------------------------------- UPDATE ---
elif page == "✏️ Update Patient":
    section("✏️ Update an Existing Patient",
            "Pick a patient, change the values, and the AI remark is regenerated.")
    if not all_patients:
        st.info("No patients to update yet.")
    else:
        selected = st.selectbox(
            "Select a patient", all_patients, format_func=patient_label, key="edit_select"
        )
        risk_card(selected["remarks"])
        payload = patient_form(defaults=selected, key=f"edit_form_{selected['id']}")
        if payload:
            with st.spinner("Updating and re-running AI prediction..."):
                response = requests.put(
                    f"{PATIENTS}/{selected['id']}", json=payload, timeout=30
                )
            if response.status_code == 200:
                updated = response.json()
                st.success("✅ Patient updated — AI remarks regenerated!")
                risk_card(updated["remarks"])
            else:
                st.error(f"❌ {api_error_text(response)}")

# ----------------------------------------------------------------- DELETE ---
elif page == "🗑️ Delete Patient":
    section("🗑️ Delete a Patient", "Review the record carefully before removing it.")
    if not all_patients:
        st.info("No patients to delete.")
    else:
        selected = st.selectbox(
            "Select a patient", all_patients, format_func=patient_label, key="delete_select"
        )

        info = st.columns(3)
        info[0].metric("Glucose", f"{selected['glucose']:g} mg/dL")
        info[1].metric("Haemoglobin", f"{selected['haemoglobin']:g} g/dL")
        info[2].metric("Cholesterol", f"{selected['cholesterol']:g} mg/dL")
        risk_card(selected["remarks"])

        st.warning(f"⚠️ You are about to **permanently delete** {selected['full_name']}.")
        confirmed = st.checkbox("Yes, I am sure", key="delete_confirm")
        if st.button("🗑️ Delete Patient", type="primary", disabled=not confirmed):
            response = requests.delete(f"{PATIENTS}/{selected['id']}", timeout=10)
            if response.status_code == 204:
                # Save the message, rerun so the list and metrics refresh,
                # then the message is shown at the top of the new run.
                st.session_state["flash"] = f"🗑️ Patient **{selected['full_name']}** deleted."
                st.rerun()
            else:
                st.error(f"❌ {api_error_text(response)}")
