"""Update History page — graphs showing how the same patient's values change over time."""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

RISK_COLORS = {"Low": "#10b981", "Moderate": "#f59e0b", "High": "#ef4444"}
RISK_ORDER = {"Low": 0, "Moderate": 1, "High": 2}


def _chart_history_rows(df: pd.DataFrame) -> pd.DataFrame:
    """Graphs only when blood test values change — skip duplicate snapshots."""
    if len(df) <= 1:
        return df
    keep_idx = [0]
    for i in range(1, len(df)):
        prev, curr = df.iloc[i - 1], df.iloc[i]
        if (
            prev["glucose"] != curr["glucose"]
            or prev["haemoglobin"] != curr["haemoglobin"]
            or prev["cholesterol"] != curr["cholesterol"]
        ):
            keep_idx.append(i)
    return df.iloc[keep_idx].copy()


def render_history_page(
    all_patients: list[dict],
    fetch_history,
    patient_label,
    section,
):
    section(
        "📈 Update History",
        "Same patient ID — each create/update adds a snapshot. See glucose, "
        "haemoglobin, cholesterol and risk level change over time.",
    )

    if not all_patients:
        st.info("No patients yet. Add a patient first, then update values to build history.")
        return

    selected = st.selectbox(
        "Select patient",
        all_patients,
        format_func=patient_label,
        key="history_select",
    )

    flash = st.session_state.get("history_flash")
    if flash and flash.get("patient_id") == selected["id"]:
        st.success(flash["message"])
        if flash.get("once"):
            st.session_state.pop("history_flash", None)

    try:
        history = fetch_history(selected["id"])
    except Exception as exc:
        st.error(f"Could not load history: {exc}")
        return

    if not history:
        st.warning("No history yet for this patient. Update their blood values to see trends.")
        return

    df = pd.DataFrame(history)
    df["recorded_at"] = pd.to_datetime(df["recorded_at"])
    df = df.sort_values("recorded_at")

    chart_df = _chart_history_rows(df)

    st.markdown(f"**Patient ID #{selected['id']}** — {selected['full_name']} ({selected['email']})")
    st.caption(f"{len(df)} snapshot(s) on record · {len(chart_df)} point(s) on trend charts")

    # Highlight risk changes (blood-value snapshots only)
    changes = []
    for i in range(1, len(chart_df)):
        prev, curr = chart_df.iloc[i - 1], chart_df.iloc[i]
        if prev["risk_level"] != curr["risk_level"]:
            changes.append(
                f"**{prev['recorded_at'].strftime('%d %b %Y %H:%M')}** → "
                f"**{curr['recorded_at'].strftime('%d %b %Y %H:%M')}**: "
                f"{prev['risk_level']} → **{curr['risk_level']}** "
                f"({curr['source']})"
            )
    if changes:
        st.success("🔄 Risk level changed:")
        for line in changes:
            st.markdown(f"- {line}")

    # Blood values line chart
    st.markdown("##### 🩸 Blood test trends")
    melted = chart_df.melt(
        id_vars=["recorded_at", "source"],
        value_vars=["glucose", "haemoglobin", "cholesterol"],
        var_name="Test",
        value_name="Value",
    )
    melted["Test"] = melted["Test"].map({
        "glucose": "Glucose (mg/dL)",
        "haemoglobin": "Haemoglobin (g/dL)",
        "cholesterol": "Cholesterol (mg/dL)",
    })
    line = px.line(
        melted,
        x="recorded_at",
        y="Value",
        color="Test",
        markers=True,
        title="Glucose, Haemoglobin & Cholesterol over updates",
    )
    line.update_layout(
        height=380,
        xaxis_title="When recorded",
        legend_title="",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(line, use_container_width=True)

    # Risk level trend
    st.markdown("##### 🎯 Risk level over time")
    risk_df = chart_df.copy()
    risk_df["risk_score"] = risk_df["risk_level"].map(RISK_ORDER)
    risk_chart = go.Figure()
    risk_chart.add_trace(
        go.Scatter(
            x=risk_df["recorded_at"],
            y=risk_df["risk_score"],
            mode="lines+markers+text",
            text=risk_df["risk_level"],
            textposition="top center",
            line=dict(color="#7c3aed", width=3),
            marker=dict(size=12, color=[RISK_COLORS[r] for r in risk_df["risk_level"]]),
        )
    )
    risk_chart.update_layout(
        height=300,
        yaxis=dict(
            tickvals=[0, 1, 2],
            ticktext=["Low", "Moderate", "High"],
            title="Risk",
        ),
        xaxis_title="When recorded",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(risk_chart, use_container_width=True)

    # Snapshot table
    st.markdown("##### 📋 All snapshots (same patient ID)")
    show = df[["recorded_at", "source", "glucose", "haemoglobin", "cholesterol", "risk_level", "remarks"]].copy()
    show["recorded_at"] = show["recorded_at"].dt.strftime("%Y-%m-%d %H:%M")
    show.columns = ["Time", "Action", "Glucose", "Hb", "Cholesterol", "Risk", "AI Remarks"]
    st.dataframe(show, use_container_width=True, hide_index=True)
