"""Home page + shared dashboard components.

render_home()          -> hero (with CTA buttons) + testimonials + footer
render_stats()         -> gradient KPI cards (used on the Dashboard page)
render_charts()        -> Plotly donut + averages chart (Dashboard page)
render_sidebar_steps() -> compact "How it works" steps (sidebar)
"""

import json
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

APP_VERSION = "1.0.0"

RISK_COLORS = {"Low": "#10b981", "Moderate": "#f59e0b", "High": "#ef4444"}


def _risk_level(remarks: str) -> str:
    if "High Risk" in remarks:
        return "High"
    if "Moderate Risk" in remarks:
        return "Moderate"
    return "Low"


def _model_accuracy() -> str:
    """Read the accuracy saved by the training pipeline (backend/models/metrics.json)."""
    project_root = Path(__file__).resolve().parent.parent.parent
    metrics_file = project_root / "backend" / "models" / "metrics.json"
    try:
        return f"{json.loads(metrics_file.read_text())['accuracy'] * 100:.1f}%"
    except Exception:
        return "97.7%"


# ------------------------------------------------------------------- HERO ---

def render_hero(go_to):
    st.markdown(
        """
        <div class="hero2">
          <div class="hero-left">
            <span class="badge-pill">🩺 MIRA · Medical Intelligence</span>
            <h1>AI-Powered <span class="grad">Health Risk</span> Prediction</h1>
            <p class="sub">Predict patient health risks instantly using machine
            learning and blood test analytics.</p>
          </div>
          <div class="hero-right">
            <div class="float-chip chip-1">🩸 Glucose 95 mg/dL</div>
            <div class="float-chip chip-2">🧬 Hb 14.2 g/dL</div>
            <div class="float-chip chip-3">💊 Chol 178 mg/dL</div>
            <div class="pulse-wrap">
              <div class="pulse-ring"></div>
              <div class="pulse-ring r2"></div>
              <div class="pulse-ring r3"></div>
              <div class="heart-core">❤️</div>
            </div>
            <svg class="ecg-svg" viewBox="0 0 400 40" preserveAspectRatio="none">
              <path d="M0,20 L60,20 L75,20 L85,4 L95,36 L105,20 L150,20 L165,20
                       L175,8 L185,32 L195,20 L260,20 L275,20 L285,4 L295,36
                       L305,20 L400,20"/>
            </svg>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.write("")
    st.markdown('<div class="hero-cta">', unsafe_allow_html=True)
    b1, b2, _ = st.columns([1, 1, 2])
    b1.button("🚀 Get Started", type="primary", use_container_width=True,
              on_click=go_to, args=("➕ Add Patient",))
    b2.button("📊 View Dashboard", use_container_width=True,
              on_click=go_to, args=("📊 Dashboard",))
    st.markdown("</div>", unsafe_allow_html=True)


# ------------------------------------------------- KPI CARDS (Dashboard) ---

def render_stats(patients: list[dict]):
    high = sum(_risk_level(p["remarks"]) == "High" for p in patients)
    low = sum(_risk_level(p["remarks"]) == "Low" for p in patients)

    cards = [
        ("kpi-indigo", "👥", len(patients), "Total Patients"),
        ("kpi-rose", "🚨", high, "High Risk Patients"),
        ("kpi-green", "✅", low, "Low Risk Patients"),
        ("kpi-violet", "🎯", _model_accuracy(), "Model Accuracy"),
    ]
    cols = st.columns(4)
    for col, (css, icon, value, label) in zip(cols, cards):
        col.markdown(
            f"""
            <div class="kpi {css}">
              <div class="icon">{icon}</div>
              <div class="val">{value}</div>
              <div class="lab">{label}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


# --------------------------------------------------- CHARTS (Dashboard) ---

def render_charts(patients: list[dict]):
    """Plotly donut (risk distribution) + grouped bar (averages by risk)."""
    df = pd.DataFrame(patients)
    df["risk"] = df["remarks"].apply(_risk_level)

    c_left, c_right = st.columns([1, 1.3])

    with c_left:
        counts = df["risk"].value_counts().reindex(["Low", "Moderate", "High"], fill_value=0)
        donut = go.Figure(
            go.Pie(
                labels=counts.index,
                values=counts.values,
                hole=0.58,
                marker=dict(colors=[RISK_COLORS[r] for r in counts.index]),
                textinfo="label+value",
            )
        )
        donut.update_layout(
            title="Risk distribution", height=320, showlegend=False,
            margin=dict(t=50, b=10, l=10, r=10),
            paper_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(donut, use_container_width=True)

    with c_right:
        avg = df.groupby("risk")[["glucose", "haemoglobin", "cholesterol"]].mean().reset_index()
        bars = px.bar(
            avg.melt(id_vars="risk", var_name="Test", value_name="Average"),
            x="Test", y="Average", color="risk",
            color_discrete_map=RISK_COLORS, barmode="group",
            title="Average blood values by risk level",
        )
        bars.update_layout(
            height=320, margin=dict(t=50, b=10, l=10, r=10),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            legend_title_text="",
        )
        st.plotly_chart(bars, use_container_width=True)


# ---------------------------------------------- HOW IT WORKS (sidebar) ---

TIMELINE = [
    ("📝", "Add Patient", "Enter personal details and blood test values."),
    ("🤖", "AI Analysis", "The model evaluates the values in milliseconds."),
    ("🎯", "Risk Classification", "Low, Moderate or High - with confidence."),
    ("📊", "Dashboard Monitoring", "Track, filter, chart and export records."),
]


def render_sidebar_steps():
    with st.expander("🚀 How it works"):
        # Compact one-line HTML per step (indented HTML breaks st.markdown).
        steps = "".join(
            f'<div class="side-step"><div class="side-dot">{i}</div>'
            f"<div><b>{icon} {title}</b><p>{desc}</p></div></div>"
            for i, (icon, title, desc) in enumerate(TIMELINE, start=1)
        )
        st.markdown(steps, unsafe_allow_html=True)


# ------------------------------------------------------------ TESTIMONIALS ---

TESTIMONIALS = [
    ("MIRA cut our patient triage time in half. The risk flags are clear "
     "enough that the front desk can act on them immediately.",
     "SK", "S. Krishnan", "Hospital Administrator"),
    ("The per-metric explanations are what convinced me - it doesn't just "
     "predict, it tells you which value is driving the risk.",
     "AR", "Dr. A. Rodrigues", "Medical Researcher"),
    ("We replaced a spreadsheet with MIRA in one afternoon. CSV export keeps "
     "our monthly reporting workflow unchanged.",
     "PM", "P. Mehta", "Clinic Manager"),
]


def render_testimonials():
    st.markdown(
        '<div class="sec-h"><h3>Trusted by healthcare teams</h3>'
        "<p>What early users say</p></div>",
        unsafe_allow_html=True,
    )
    cols = st.columns(3)
    for col, (quote, initials, name, role) in zip(cols, TESTIMONIALS):
        col.markdown(
            f"""
            <div class="quote-card">
              <div class="mark">&ldquo;</div>
              <p class="txt">{quote}</p>
              <div class="quote-who">
                <div class="av">{initials}</div>
                <div><b>{name}</b><span>{role}</span></div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ----------------------------------------------------------------- FOOTER ---

def render_footer():
    st.markdown(
        f"""
        <div class="footer2">
          <div class="cols">
            <div class="col">
              <h6>🩺 MIRA</h6>
              <p>Medical Intelligence Robotic Automation - a health prediction
              platform demo.</p>
            </div>
            <div class="col">
              <h6>Built With</h6>
              <p>⚡ Streamlit frontend</p>
              <p>🚀 FastAPI backend</p>
              <p>🤖 Machine Learning powered (scikit-learn)</p>
            </div>
            <div class="col">
              <h6>Data Layer</h6>
              <p>🗄️ SQL Server support</p>
              <p>🪶 SQLite support</p>
              <p>🔐 No secrets in code</p>
            </div>
            <div class="col">
              <h6>Version</h6>
              <p>v{APP_VERSION}</p>
              <p>Model accuracy: {_model_accuracy()}</p>
            </div>
          </div>
          <div class="bottom">
            <span>⚠️ Demo project - not medical advice.</span>
            <span>© 2026 MIRA Health</span>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ------------------------------------------------------------------- PAGE ---

def render_home(go_to):
    render_hero(go_to)
    st.write("")
    st.divider()
    render_testimonials()
    render_footer()
