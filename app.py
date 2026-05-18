# =============================================================================
#   NEXUS SCOUT  —  Universal AI Personal Shopper
#   File    : app.py
#   Run     : streamlit run app.py
#   Deploy  : push to GitHub, connect repo on share.streamlit.io — done.
#
#   Dependencies (all standard — no API keys required to run):
#     pip install streamlit
# =============================================================================

import hashlib
import math
import re
import time
import urllib.parse
import datetime  # 🧠 <-- This fixes the "datetime not defined" error!
from dataclasses import dataclass
from typing import Optional

import streamlit as st

# ──────────────────────────────────────────────────────────────────────────────
# 0.  PAGE CONFIG  ← must be the first Streamlit call
# ──────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Nexus Scout",
    page_icon="🔭",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ──────────────────────────────────────────────────────────────────────────────
# 1.  GLOBAL CSS
# ──────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Mono:wght@400;500&family=Lato:wght@300;400;700&display=swap');

/* ── Tokens ── */
:root {
  --ink:       #0a0a0f;
  --ink2:      #2c2c3a;
  --ink3:      #72728a;
  --bg:        #f7f7fc;
  --bg2:       #efeff6;
  --bg3:       #e6e6f0;
  --white:     #ffffff;
  --gold:      #c9a84c;
  --gold-d:    #8a6a1f;
  --gold-l:    #fdf3dc;
  --teal:      #0d7a63;
  --teal-l:    #d5f0ea;
  --red:       #b03030;
  --red-l:     #fce8e8;
  --blue:      #1d5db5;
  --blue-l:    #deeafb;
  --border:    rgba(10,10,15,.09);
  --border-md: rgba(10,10,15,.17);
  --r:         10px;
  --r-lg:      18px;
  --mono:      'DM Mono', monospace;
  --head:      'Syne', sans-serif;
  --body:      'Lato', sans-serif;
  --shadow-sm: 0 1px 4px rgba(10,10,15,.06);
  --shadow-md: 0 4px 20px rgba(10,10,15,.09);
  --shadow-lg: 0 12px 40px rgba(10,10,15,.13);
}

/* ── Reset + global ── */
*, *::before, *::after { box-sizing: border-box; }
html, body, [class*="css"] { font-family: var(--body) !important; background: var(--bg) !important; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 1.5rem 2rem 4rem !important; max-width: 1300px; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
  background: var(--ink) !important;
  border-right: none !important;
}
[data-testid="stSidebar"] * { color: rgba(255,255,255,.82) !important; }
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
  font-family: var(--head) !important;
  color: #fff !important;
  font-weight: 700 !important;
}
[data-testid="stSidebar"] .stSlider [data-baseweb="slider"] div[role="slider"] {
  background-color: var(--gold) !important;
}
[data-testid="stSidebar"] input {
  background: rgba(255,255,255,.08) !important;
  border-color: rgba(255,255,255,.18) !important;
  color: #fff !important;
  border-radius: var(--r) !important;
}
[data-testid="stSidebar"] [data-baseweb="select"] div {
  background: rgba(255,255,255,.08) !important;
  border-color: rgba(255,255,255,.18) !important;
  color: #fff !important;
}
[data-testid="stSidebar"] label { color: rgba(255,255,255,.6) !important; font-size: 11px !important; text-transform: uppercase; letter-spacing: .8px; }
[data-testid="stSidebar"] .stCheckbox label { color: rgba(255,255,255,.82) !important; font-size: 13px !important; text-transform: none; letter-spacing: 0; }

/* ── Text input ── */
[data-testid="stTextInput"] input {
  font-family: var(--head) !important;
  font-size: 17px !important;
  font-weight: 600 !important;
  background: var(--white) !important;
  border: 1.5px solid var(--border-md) !important;
  border-radius: 100px !important;
  padding: .75rem 1.4rem !important;
  box-shadow: var(--shadow-sm);
  transition: border-color .2s, box-shadow .2s;
}
[data-testid="stTextInput"] input:focus {
  border-color: var(--gold) !important;
  box-shadow: 0 0 0 4px rgba(201,168,76,.14) !important;
}
[data-testid="stTextInput"] input::placeholder { color: var(--ink3) !important; font-weight: 400; font-size: 15px !important; }
[data-testid="stTextInput"] > label { display: none !important; }

/* ── Primary button ── */
.stButton > button {
  font-family: var(--head) !important;
  font-weight: 700 !important;
  font-size: 14px !important;
  letter-spacing: .5px;
  background: var(--ink) !important;
  color: #fff !important;
  border: none !important;
  border-radius: 100px !important;
  padding: .7rem 1.6rem !important;
  transition: transform .15s, background .2s, box-shadow .2s !important;
  box-shadow: var(--shadow-md) !important;
}
.stButton > button:hover {
  background: var(--ink2) !important;
  transform: translateY(-1px) !important;
  box-shadow: var(--shadow-lg) !important;
}
.stButton > button:active { transform: scale(.97) !important; }

/* ── Metric overrides ── */
[data-testid="metric-container"] {
  background: var(--white);
  border: 0.5px solid var(--border-md);
  border-radius: var(--r-lg);
  padding: 1rem 1.2rem !important;
  box-shadow: var(--shadow-sm);
}
[data-testid="metric-container"] label {
  font-family: var(--mono) !important;
  font-size: 10px !important;
  text-transform: uppercase;
  letter-spacing: 1px;
  color: var(--ink3) !important;
}
[data-testid="stMetricValue"] {
  font-family: var(--head) !important;
  font-size: 1.55rem !important;
  font-weight: 800 !important;
  color: var(--ink) !important;
}
[data-testid="stMetricDelta"] { font-family: var(--mono) !important; font-size: 11px !important; }
[data-testid="stMetricDeltaIcon"] { display: none; }

/* ── Marketplace card ── */
.mkt-card {
  background: var(--white);
  border: 0.5px solid var(--border-md);
  border-radius: var(--r-lg);
  overflow: hidden;
  box-shadow: var(--shadow-sm);
  transition: transform .22s cubic-bezier(.25,.8,.25,1), box-shadow .22s;
  height: 100%;
  display: flex;
  flex-direction: column;
  padding-bottom: 20px;
}
.mkt-card:hover {
  transform: translateY(-4px) scale(1.01);
  box-shadow: var(--shadow-lg);
}
.card-header {
  padding: 1.3rem 1.3rem .9rem;
  display: flex;
  align-items: flex-start;
  gap: 12px;
  border-bottom: 0.5px solid var(--border);
}
.platform-icon {
  width: 48px; height: 48px;
  border-radius: 12px;
  display: flex; align-items: center; justify-content: center;
  font-size: 22px;
  flex-shrink: 0;
  background: var(--bg2);
  border: 0.5px solid var(--border);
}
.card-title-block { flex: 1; min-width: 0; }
.platform-name {
  font-family: var(--head);
  font-size: 15.5px; font-weight: 700;
  color: var(--ink); letter-spacing: -.2px;
  margin-bottom: 2px;
}
.platform-category {
  font-family: var(--mono);
  font-size: 10px; color: var(--ink3);
  text-transform: uppercase; letter-spacing: .8px;
}
.trust-badge {
  font-family: var(--mono);
  font-size: 10px; font-weight: 500;
  padding: 3px 8px;
  border-radius: 100px;
}
.card-body { padding: .9rem 1.3rem; flex: 1; }
.listing-count {
  font-family: var(--mono); font-size: 11.5px;
  color: var(--ink3); margin-bottom: 8px;
}
.listing-count b { color: var(--ink); font-weight: 500; }
.tag-row { display: flex; gap: 6px; flex-wrap: wrap; margin-bottom: 10px; }
.tag {
  font-family: var(--mono); font-size: 10.5px; font-weight: 500;
  padding: 3px 9px; border-radius: 100px;
  background: var(--bg2); border: 0.5px solid var(--border-md);
  color: var(--ink2);
}
.tag.green  { background: var(--teal-l); color: var(--teal); border-color: rgba(13,122,99,.18); }
.tag.gold   { background: var(--gold-l); color: var(--gold-d); border-color: rgba(201,168,76,.25); }
.tag.blue   { background: var(--blue-l); color: var(--blue); border-color: rgba(29,93,181,.18); }
.price-estimate {
  font-family: var(--head); font-size: 14px; font-weight: 700;
  color: var(--ink); margin-top: 6px;
}
.price-estimate span { font-family: var(--mono); font-size: 11px; font-weight: 400; color: var(--ink3); margin-left: 4px; }
.card-footer { padding: .9rem 1.3rem 1.1rem; }

/* ── Verdict strip ── */
.verdict-strip {
  display: flex; align-items: center; gap: 10px;
  background: var(--white);
  border: 0.5px solid var(--border-md);
  border-radius: 100px;
  padding: 10px 18px;
  margin: .6rem 0 1.4rem;
  box-shadow: var(--shadow-sm);
  flex-wrap: wrap;
}
.verdict-dot { width: 9px; height: 9px; border-radius: 50%; flex-shrink: 0; }
.verdict-text { font-family: var(--head); font-size: 13.5px; font-weight: 700; color: var(--ink); }
.verdict-sub  { font-family: var(--mono); font-size: 11px; color: var(--ink3); }

/* ── Section label ── */
.section-eyebrow {
  font-family: var(--mono); font-size: 10px;
  text-transform: uppercase; letter-spacing: 2px;
  color: var(--gold);
  margin-bottom: 4px;
}
h2.section-title {
  font-family: var(--head) !important; font-size: 1.7rem !important;
  font-weight: 800 !important; letter-spacing: -.5px;
  color: var(--ink) !important; margin: 0 0 1rem 0 !important;
}

/* ── Hero ── */
.hero-bar {
  display: flex; align-items: center; gap: 14px;
  margin-bottom: 2rem;
  padding-bottom: 1.4rem;
  border-bottom: 0.5px solid var(--border-md);
}
.logo-mark {
  width: 42px; height: 42px; border-radius: 12px;
  background: var(--ink); display: flex; align-items: center;
  justify-content: center; font-size: 20px; flex-shrink: 0;
  box-shadow: var(--shadow-md);
}
.brand-name {
  font-family: var(--head); font-size: 1.5rem;
  font-weight: 800; letter-spacing: -1px; color: var(--ink);
}
.brand-name em { font-style: normal; color: var(--gold); }
.brand-tag {
  font-family: var(--mono); font-size: 11px;
  color: var(--ink3); margin-top: 1px;
}
.beta-pill {
  font-family: var(--mono); font-size: 9.5px; font-weight: 500;
  background: var(--gold-l
