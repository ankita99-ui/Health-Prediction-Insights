"""All custom CSS in one place - injected once per page run.

Design system:
  - Purple-blue gradient brand (#4f46e5 -> #7c3aed -> #db2777)
  - Glassmorphism: translucent white + backdrop blur + soft border
  - 20px rounded corners, soft layered shadows
  - Hover lift/scale transitions, fade-in-up entry animations
"""

import streamlit as st

GLOBAL_CSS = """
<style>
  :root {
    --brand-1: #4f46e5;
    --brand-2: #7c3aed;
    --brand-3: #db2777;
    --ink: #1f2333;
    --muted: #6b7280;
    --glass: rgba(255, 255, 255, 0.6);
    --glass-border: rgba(255, 255, 255, 0.75);
  }

  /* ---------- entry animations ---------- */
  @keyframes fadeInUp {
    from { opacity: 0; transform: translateY(18px); }
    to   { opacity: 1; transform: translateY(0); }
  }
  @keyframes heartbeat {
    0%, 100% { transform: scale(1); }
    14%      { transform: scale(1.18); }
    28%      { transform: scale(1); }
    42%      { transform: scale(1.18); }
    70%      { transform: scale(1); }
  }
  @keyframes pulseRing {
    0%   { transform: scale(0.6); opacity: 0.8; }
    100% { transform: scale(1.9); opacity: 0; }
  }
  @keyframes floatY {
    0%, 100% { transform: translateY(0); }
    50%      { transform: translateY(-12px); }
  }
  @keyframes ecg {
    0%   { stroke-dashoffset: 480; }
    100% { stroke-dashoffset: 0; }
  }

  .fade-in { animation: fadeInUp .6s ease both; }

  /* ---------- HERO ---------- */
  .hero2 {
    position: relative;
    background: linear-gradient(120deg, #4f46e5 0%, #7c3aed 48%, #db2777 100%);
    border-radius: 20px;
    padding: 3rem 3rem 2.4rem 3rem;
    color: white;
    overflow: hidden;
    box-shadow: 0 18px 45px rgba(124, 58, 237, 0.35);
    display: flex;
    align-items: center;
    gap: 2rem;
    animation: fadeInUp .6s ease both;
  }
  .hero2::before, .hero2::after {       /* soft glass orbs in the background */
    content: "";
    position: absolute;
    border-radius: 50%;
    background: rgba(255,255,255,0.12);
    backdrop-filter: blur(6px);
  }
  .hero2::before { width: 320px; height: 320px; top: -140px; right: -80px; }
  .hero2::after  { width: 200px; height: 200px; bottom: -100px; left: 30%; }

  .hero2 .hero-left { flex: 1.4; position: relative; z-index: 2; }
  .hero2 .badge-pill {
    display: inline-block;
    background: rgba(255,255,255,0.18);
    border: 1px solid rgba(255,255,255,0.35);
    backdrop-filter: blur(8px);
    padding: 0.3rem 0.9rem;
    border-radius: 999px;
    font-size: 0.8rem;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    margin-bottom: 1rem;
  }
  .hero2 h1 {
    margin: 0;
    font-size: 2.6rem;
    line-height: 1.15;
    letter-spacing: -0.5px;
  }
  .hero2 h1 .grad {
    background: linear-gradient(90deg, #fde68a, #fca5a5);
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
  }
  .hero2 p.sub {
    margin: 0.9rem 0 0 0;
    font-size: 1.08rem;
    opacity: 0.92;
    max-width: 34rem;
  }

  /* animated illustration (right side) */
  .hero2 .hero-right {
    flex: 1; position: relative; z-index: 2;
    display: flex; align-items: center; justify-content: center;
    min-height: 210px;
  }
  .pulse-wrap { position: relative; width: 170px; height: 170px;
    display: flex; align-items: center; justify-content: center; }
  .pulse-ring {
    position: absolute; inset: 0; border-radius: 50%;
    border: 3px solid rgba(255,255,255,0.65);
    animation: pulseRing 2.2s ease-out infinite;
  }
  .pulse-ring.r2 { animation-delay: 0.7s; }
  .pulse-ring.r3 { animation-delay: 1.4s; }
  .heart-core {
    width: 110px; height: 110px; border-radius: 50%;
    background: rgba(255,255,255,0.2);
    border: 1px solid rgba(255,255,255,0.5);
    backdrop-filter: blur(10px);
    display: flex; align-items: center; justify-content: center;
    font-size: 3rem;
    animation: heartbeat 1.6s ease-in-out infinite;
    box-shadow: 0 8px 30px rgba(0,0,0,0.18);
  }
  .float-chip {
    position: absolute;
    background: rgba(255,255,255,0.22);
    border: 1px solid rgba(255,255,255,0.45);
    backdrop-filter: blur(8px);
    border-radius: 14px;
    padding: 0.35rem 0.7rem;
    font-size: 0.85rem;
    animation: floatY 3.4s ease-in-out infinite;
    white-space: nowrap;
  }
  .chip-1 { top: 4%;  left: 0;   animation-delay: 0s; }
  .chip-2 { top: 38%; right: 0;  animation-delay: 1.1s; }
  .chip-3 { bottom: 2%; left: 12%; animation-delay: 2.2s; }

  .ecg-svg { position: absolute; bottom: -8px; left: 0; right: 0; width: 100%; opacity: .85; }
  .ecg-svg path {
    stroke: #ffffff; stroke-width: 2.5; fill: none;
    stroke-dasharray: 480; animation: ecg 3.2s linear infinite;
  }

  /* hero CTA buttons (streamlit buttons right under the hero) */
  .hero-cta .stButton button {
    border-radius: 14px;
    padding: 0.65rem 1.4rem;
    font-weight: 700;
    font-size: 1rem;
  }

  /* ---------- KPI cards ---------- */
  .kpi {
    border-radius: 20px;
    padding: 1.2rem 1.3rem;
    color: white;
    position: relative;
    overflow: hidden;
    box-shadow: 0 10px 24px rgba(31, 35, 51, 0.14);
    transition: transform .2s ease, box-shadow .2s ease;
    animation: fadeInUp .6s ease both;
    min-height: 120px;
  }
  .kpi:hover { transform: translateY(-4px) scale(1.02); box-shadow: 0 16px 34px rgba(31,35,51,.22); }
  .kpi .icon { font-size: 1.7rem; }
  .kpi .val  { font-size: 2rem; font-weight: 800; line-height: 1.1; margin-top: .2rem; }
  .kpi .lab  { font-size: .88rem; opacity: .92; }
  .kpi::after {                      /* glass shine */
    content: ""; position: absolute; top: -60%; right: -20%;
    width: 70%; height: 200%; transform: rotate(25deg);
    background: rgba(255,255,255,0.14);
  }
  .kpi-indigo { background: linear-gradient(135deg, #4f46e5, #6366f1); }
  .kpi-rose   { background: linear-gradient(135deg, #e11d48, #f43f5e); }
  .kpi-green  { background: linear-gradient(135deg, #059669, #10b981); }
  .kpi-violet { background: linear-gradient(135deg, #7c3aed, #a855f7); }

  /* ---------- glass feature cards with gradient border ---------- */
  .glass-card {
    background:
      linear-gradient(var(--glass), var(--glass)) padding-box,
      linear-gradient(135deg, #4f46e5, #db2777) border-box;
    border: 2px solid transparent;
    border-radius: 20px;
    backdrop-filter: blur(12px);
    padding: 1.25rem 1.3rem;
    min-height: 168px;
    box-shadow: 0 6px 20px rgba(79, 70, 229, 0.10);
    transition: transform .2s ease, box-shadow .2s ease;
    animation: fadeInUp .6s ease both;
  }
  .glass-card:hover {
    transform: translateY(-5px) scale(1.02);
    box-shadow: 0 16px 36px rgba(124, 58, 237, 0.22);
  }
  .glass-card .icon {
    width: 46px; height: 46px; border-radius: 14px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.4rem;
    background: linear-gradient(135deg, rgba(79,70,229,.14), rgba(219,39,119,.14));
    margin-bottom: .6rem;
  }
  .glass-card h4 { margin: 0 0 .3rem 0; color: var(--ink); font-size: 1.05rem; }
  .glass-card p  { margin: 0; color: var(--muted); font-size: .9rem; line-height: 1.5; }

  /* ---------- sidebar "How it works" steps ---------- */
  .side-step {
    display: flex; align-items: flex-start; gap: .65rem;
    margin-bottom: .85rem;
  }
  .side-dot {
    background: linear-gradient(135deg, var(--brand-1), var(--brand-2));
    color: white; font-weight: 700; font-size: .85rem;
    min-width: 1.7rem; height: 1.7rem; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    box-shadow: 0 4px 10px rgba(124, 58, 237, .3);
    margin-top: .1rem;
  }
  .side-step b { color: var(--ink); font-size: .88rem; }
  .side-step p { margin: .1rem 0 0 0; color: var(--muted); font-size: .78rem; line-height: 1.4; }

  /* ---------- testimonials ---------- */
  .quote-card {
    background: var(--glass);
    border: 1px solid var(--glass-border);
    backdrop-filter: blur(12px);
    border-radius: 20px;
    padding: 1.3rem 1.4rem;
    min-height: 190px;
    box-shadow: 0 6px 20px rgba(31, 35, 51, 0.08);
    transition: transform .2s ease, box-shadow .2s ease;
    animation: fadeInUp .6s ease both;
  }
  .quote-card:hover { transform: translateY(-4px); box-shadow: 0 14px 30px rgba(31,35,51,.14); }
  .quote-card .mark { font-size: 1.9rem; color: var(--brand-2); line-height: 1; }
  .quote-card p.txt { color: #374151; font-size: .92rem; line-height: 1.55; margin: .4rem 0 .9rem 0; }
  .quote-who { display: flex; align-items: center; gap: .65rem; }
  .quote-who .av {
    width: 40px; height: 40px; border-radius: 50%;
    background: linear-gradient(135deg, #4f46e5, #db2777);
    color: white; display: flex; align-items: center; justify-content: center;
    font-weight: 700;
  }
  .quote-who b { color: var(--ink); font-size: .92rem; display: block; }
  .quote-who span { color: var(--muted); font-size: .8rem; }

  /* ---------- footer ---------- */
  .footer2 {
    margin-top: 2.2rem;
    background: linear-gradient(120deg, #1e1b4b, #312e81 60%, #4c1d95);
    border-radius: 20px;
    color: #e0e7ff;
    padding: 1.6rem 2rem 1.2rem 2rem;
    box-shadow: 0 12px 30px rgba(30, 27, 75, 0.35);
  }
  .footer2 .cols { display: flex; gap: 2rem; flex-wrap: wrap; }
  .footer2 .col { flex: 1; min-width: 160px; }
  .footer2 h6 { color: white; margin: 0 0 .45rem 0; font-size: .95rem; }
  .footer2 p { margin: .15rem 0; font-size: .84rem; opacity: .85; }
  .footer2 .bottom {
    border-top: 1px solid rgba(255,255,255,.16);
    margin-top: 1rem; padding-top: .8rem;
    display: flex; justify-content: space-between; flex-wrap: wrap;
    font-size: .8rem; opacity: .75;
  }

  /* ---------- section headings ---------- */
  .sec-h { text-align: center; margin: 0.4rem 0 1.1rem 0; }
  .sec-h h3 { margin: 0; color: var(--ink); font-size: 1.5rem; }
  .sec-h p  { margin: .25rem 0 0 0; color: var(--muted); font-size: .95rem; }

  /* ---------- compact banner (inner pages) ---------- */
  .hero {
    background: linear-gradient(120deg, #4f46e5 0%, #7c3aed 50%, #db2777 100%);
    padding: 1.4rem 2rem;
    border-radius: 20px;
    color: white;
    margin-bottom: 1.2rem;
    box-shadow: 0 10px 30px rgba(124, 58, 237, 0.25);
  }
  .hero h1 { margin: 0; font-size: 1.7rem; letter-spacing: 0.3px; }
  .hero p  { margin: 0.3rem 0 0 0; opacity: 0.92; font-size: 0.98rem; }

  /* ---------- shared (other pages) ---------- */
  div[data-testid="stMetric"] {
    background: #ffffff;
    border: 1px solid #ebedf3;
    border-radius: 16px;
    padding: 1rem 1.1rem;
    box-shadow: 0 3px 10px rgba(79, 70, 229, 0.06);
    transition: transform .15s ease, box-shadow .15s ease;
  }
  div[data-testid="stMetric"]:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 18px rgba(79, 70, 229, 0.12);
  }

  .risk-card {
    border-radius: 14px;
    padding: 1rem 1.2rem;
    margin: 0.8rem 0;
    font-size: 1rem;
    line-height: 1.55;
    border-left: 6px solid;
    box-shadow: 0 2px 8px rgba(0,0,0,0.04);
  }
  .risk-low      { background: #e7f6ee; border-color: #16a34a; color: #14532d; }
  .risk-moderate { background: #fef7e0; border-color: #f59e0b; color: #713f12; }
  .risk-high     { background: #fdebec; border-color: #dc2626; color: #7f1d1d; }

  .stButton button, .stFormSubmitButton button, .stDownloadButton button {
    border-radius: 12px;
    font-weight: 600;
    transition: transform .15s ease;
  }
  .stButton button:hover, .stFormSubmitButton button:hover { transform: translateY(-1px); }

  section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #ffffff 0%, #f3f0fb 100%);
    border-right: 1px solid #ebe7f7;
  }
  .sidebar-brand { font-size: 1.45rem; font-weight: 800; color: #4f46e5; margin-bottom: 0.1rem; }

  .section-title { font-size: 1.35rem; font-weight: 700; color: #1f2333; margin-bottom: 0.2rem; }
  .section-sub   { color: #6b7280; margin-bottom: 1rem; }

  /* ---------- mobile ---------- */
  @media (max-width: 880px) {
    .hero2 { flex-direction: column; padding: 2rem 1.4rem; text-align: center; }
    .hero2 h1 { font-size: 1.9rem; }
    .hero2 .hero-right { min-height: 180px; }
    .timeline { flex-wrap: wrap; gap: 1rem; }
    .t-step { flex: 1 1 40%; }
    .t-step::before { display: none; }
    .footer2 .cols { flex-direction: column; gap: 1rem; }
  }
</style>
"""


def inject_css():
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)
