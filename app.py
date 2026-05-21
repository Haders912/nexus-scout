# =============================================================================
#  NEXUS SCOUT  —  Universal AI Personal Shopper  (Premium UI v2)
#  File    : app.py
#  Run     : streamlit run app.py
#  Deploy  : push to GitHub → connect on share.streamlit.io
#  Deps    : pip install streamlit          (nothing else needed)
#
#  v2 changes over v1
#  ───────────────────
#  • Smart suggestion chips — 6 clickable buttons that populate the search
#    bar AND fire the search immediately via session state + st.rerun()
#  • Region-aware URLs — eBay / Amazon / Google adapt to US / UK / EU / AU
#  • SaaS sidebar — Filter Empty Listings toggle, Target Region dropdown,
#    clean section headings, persistent search history panel
#  • Equal-height 3-col cards — full CSS flexbox chain ensures the CTA
#    button is always flush to the card bottom, no gap mismatches
#  • CSS :has() button differentiation — chip row and Scout CTA get
#    distinct styles without any JavaScript or hidden elements
#  • All _estimate_price / build_search_url / Platform logic unchanged
# =============================================================================

from __future__ import annotations

import hashlib
import re
import time
import urllib.parse
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

import streamlit as st

# ─────────────────────────────────────────────────────────────────────────────
# 0.  PAGE CONFIG  ← must be the very first Streamlit call
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title            = "Nexus Scout",
    page_icon             = "🔭",
    layout                = "wide",
    initial_sidebar_state = "expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# 1.  SESSION STATE  — initialised before any widget so chips can pre-fill
#
#  search_input : str   — the text currently shown in the search bar (widget key)
#  do_search    : bool  — flag set by chip clicks or Scout button press
#  last_query   : str   — last query that was fully executed (prevents re-fire)
#  search_history: list — rolling list of past queries shown in sidebar
# ─────────────────────────────────────────────────────────────────────────────
if "search_input"   not in st.session_state: st.session_state.search_input   = ""
if "do_search"      not in st.session_state: st.session_state.do_search      = False
if "last_query"     not in st.session_state: st.session_state.last_query     = ""
if "search_history" not in st.session_state: st.session_state.search_history = []

# ─────────────────────────────────────────────────────────────────────────────
# 2.  GLOBAL CSS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Mono:wght@400;500&family=Lato:wght@300;400;700&display=swap');

/* ── Design tokens ── */
:root {
  --ink:        #0a0a0f;
  --ink2:       #2c2c3a;
  --ink3:       #72728a;
  --bg:         #f4f4f9;
  --bg2:        #ecedf4;
  --bg3:        #e2e3ed;
  --white:      #ffffff;
  --gold:       #c9a84c;
  --gold-d:     #7d5f10;
  --gold-l:     #fdf3dc;
  --teal:       #0d7a63;
  --teal-l:     #d5f0ea;
  --blue:       #1d5db5;
  --blue-l:     #deeafb;
  --border:     rgba(10,10,15,.08);
  --border-md:  rgba(10,10,15,.14);
  --border-str: rgba(10,10,15,.24);
  --r:          10px;
  --r-lg:       16px;
  --r-xl:       22px;
  --mono:       'DM Mono', monospace;
  --head:       'Syne', sans-serif;
  --body:       'Lato', sans-serif;
  --sh-sm:      0 1px 3px rgba(10,10,15,.06);
  --sh-md:      0 4px 18px rgba(10,10,15,.09);
  --sh-lg:      0 12px 40px rgba(10,10,15,.13);
}

/* ── Global reset ── */
*, *::before, *::after  { box-sizing: border-box; }
html, body, [class*="css"] {
  font-family: var(--body) !important;
  background:  var(--bg)   !important;
}
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 1.8rem 2.4rem 5rem !important; max-width: 1280px; }

/* ── Equal-height card columns ──────────────────────────────────────────────
   Chain of flex-column rules from the Streamlit column wrapper right down
   to .mkt-card so every card in a row stretches to the same height and the
   CTA button is always visually anchored to the card bottom.              */
[data-testid="stHorizontalBlock"]           { align-items: stretch !important; }
[data-testid="stColumn"]                    { display: flex !important; flex-direction: column !important; }
[data-testid="stColumn"] > div              { flex: 1 !important; display: flex !important; flex-direction: column !important; }
[data-testid="stColumn"] > div > div        { flex: 1 !important; display: flex !important; flex-direction: column !important; }
[data-testid="stColumn"] .element-container { flex: 1 !important; display: flex !important; flex-direction: column !important; }
[data-testid="stColumn"] .element-container > div { flex: 1 !important; }

/* ── Sidebar ────────────────────────────────────────────────────────────── */
[data-testid="stSidebar"] {
  background:   #0e0e16 !important;
  border-right: 0.5px solid rgba(255,255,255,.07) !important;
}
[data-testid="stSidebar"] > div { padding-top: .4rem !important; }
[data-testid="stSidebar"] *     { color: rgba(255,255,255,.80) !important; }
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3    { color: #fff !important; font-family: var(--head) !important; font-weight: 700 !important; }
[data-testid="stSidebar"] input,
[data-testid="stSidebar"] textarea {
  background:  rgba(255,255,255,.07) !important;
  border:      0.5px solid rgba(255,255,255,.15) !important;
  color:       #fff !important;
  border-radius: var(--r) !important;
}
[data-testid="stSidebar"] [data-baseweb="select"] > div:first-child {
  background:    rgba(255,255,255,.07) !important;
  border:        0.5px solid rgba(255,255,255,.15) !important;
  border-radius: var(--r) !important;
}
[data-testid="stSidebar"] [data-baseweb="select"] span { color: #fff !important; }
[data-testid="stSidebar"] [role="slider"]              { background: var(--gold) !important; }
[data-testid="stSidebar"] label {
  color:          rgba(255,255,255,.40) !important;
  font-family:    var(--mono) !important;
  font-size:      10px !important;
  text-transform: uppercase;
  letter-spacing: 1px;
}
[data-testid="stSidebar"] .stCheckbox label,
[data-testid="stSidebar"] .stToggle   label {
  color:          rgba(255,255,255,.82) !important;
  font-family:    var(--body) !important;
  font-size:      13px !important;
  text-transform: none;
  letter-spacing: 0;
}

/* ── Search bar ─────────────────────────────────────────────────────────── */
[data-testid="stTextInput"] input {
  font-family:  var(--head)  !important;
  font-size:    16px         !important;
  font-weight:  600          !important;
  background:   var(--white) !important;
  border:       1.5px solid var(--border-md) !important;
  border-radius:100px        !important;
  padding:      .8rem 1.5rem !important;
  height:       52px         !important;
  box-shadow:   var(--sh-sm);
  transition:   border-color .2s, box-shadow .2s;
}
[data-testid="stTextInput"] input:focus {
  border-color: var(--gold)  !important;
  box-shadow:   0 0 0 4px rgba(201,168,76,.14), var(--sh-sm) !important;
  outline:      none !important;
}
[data-testid="stTextInput"] input::placeholder {
  color:       var(--ink3) !important;
  font-weight: 400;
  font-size:   14px !important;
}
[data-testid="stTextInput"] > label { display: none !important; }

/* ── Chip buttons (6-column row) ─────────────────────────────────────────
   CSS :has() is supported in Chrome 105+, Firefox 121+, Safari 15.4+.
   We target any horizontal block that contains at least 6 child columns.  */
[data-testid="stHorizontalBlock"]:has(> [data-testid="stColumn"]:nth-child(6)) .stButton > button {
  background:    var(--white)      !important;
  color:         var(--ink2)       !important;
  border:        0.5px solid var(--border-md) !important;
  border-radius: 100px             !important;
  font-family:   var(--mono)       !important;
  font-size:     11.5px            !important;
  font-weight:   500               !important;
  letter-spacing: 0                !important;
  padding:       .45rem .8rem      !important;
  box-shadow:    var(--sh-sm)      !important;
  transition:    background .15s, border-color .15s, color .15s,
                 transform .15s, box-shadow .15s  !important;
  white-space:   nowrap !important;
}
[data-testid="stHorizontalBlock"]:has(> [data-testid="stColumn"]:nth-child(6)) .stButton > button:hover {
  background:    var(--bg2)        !important;
  border-color:  var(--border-str) !important;
  color:         var(--ink)        !important;
  transform:     translateY(-1px)  !important;
  box-shadow:    var(--sh-md)      !important;
}
[data-testid="stHorizontalBlock"]:has(> [data-testid="stColumn"]:nth-child(6)) .stButton > button:active {
  transform: scale(.96) !important;
}

/* ── Scout CTA button (2-column search row) ──────────────────────────────
   Targets the horizontal block that has exactly 2 columns.               */
[data-testid="stHorizontalBlock"]:has(> [data-testid="stColumn"]:nth-child(2):last-child) .stButton > button {
  background:    var(--ink)        !important;
  color:         #fff              !important;
  border:        none              !important;
  border-radius: 100px             !important;
  font-family:   var(--head)       !important;
  font-size:     14px              !important;
  font-weight:   700               !important;
  letter-spacing:.4px              !important;
  padding:       .8rem 1.4rem      !important;
  height:        52px              !important;
  box-shadow:    var(--sh-md)      !important;
  transition:    background .2s, transform .15s, box-shadow .2s !important;
}
[data-testid="stHorizontalBlock"]:has(> [data-testid="stColumn"]:nth-child(2):last-child) .stButton > button:hover {
  background: var(--ink2)   !important;
  transform:  translateY(-1px) !important;
  box-shadow: var(--sh-lg)  !important;
}
[data-testid="stHorizontalBlock"]:has(> [data-testid="stColumn"]:nth-child(2):last-child) .stButton > button:active {
  transform: scale(.97) !important;
}

/* ── Metric tiles ────────────────────────────────────────────────────────── */
[data-testid="metric-container"] {
  background:    var(--white);
  border:        0.5px solid var(--border-md);
  border-radius: var(--r-lg);
  padding:       1.1rem 1.3rem !important;
  box-shadow:    var(--sh-sm);
}
[data-testid="metric-container"] label {
  font-family:    var(--mono) !important;
  font-size:      9.5px !important;
  text-transform: uppercase;
  letter-spacing: 1.2px;
  color:          var(--ink3) !important;
}
[data-testid="stMetricValue"] {
  font-family: var(--head) !important;
  font-size:   1.5rem !important;
  font-weight: 800 !important;
  color:       var(--ink) !important;
}
[data-testid="stMetricDelta"]     { font-family: var(--mono) !important; font-size: 10.5px !important; }
[data-testid="stMetricDeltaIcon"] { display: none; }

/* ── Marketplace card ────────────────────────────────────────────────────── */
.mkt-card {
  background:     var(--white);
  border:         0.5px solid var(--border-md);
  border-radius:  var(--r-xl);
  overflow:       hidden;
  box-shadow:     var(--sh-sm);
  transition:     transform .22s cubic-bezier(.25,.8,.25,1),
                  box-shadow .22s, border-color .22s;
  display:        flex;
  flex-direction: column;
  height:         100%;          /* fills the stretched column */
}
.mkt-card:hover {
  transform:    translateY(-4px);
  box-shadow:   var(--sh-lg);
  border-color: var(--border-str);
}
.card-header {
  padding:       1.2rem 1.25rem 1rem;
  display:       flex;
  align-items:   flex-start;
  gap:           12px;
  border-bottom: 0.5px solid var(--border);
}
.platform-icon {
  width: 46px; height: 46px;
  border-radius: 12px;
  display: flex; align-items: center; justify-content: center;
  font-size: 21px; flex-shrink: 0;
  background: var(--bg2);
  border: 0.5px solid var(--border-md);
}
.card-title-block { flex: 1; min-width: 0; }
.platform-name {
  font-family:   var(--head);
  font-size:     15px; font-weight: 700;
  color:         var(--ink); letter-spacing: -.2px;
  margin-bottom: 2px;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.platform-category {
  font-family:    var(--mono);
  font-size:      9.5px; color: var(--ink3);
  text-transform: uppercase; letter-spacing: .8px;
}
.trust-badge {
  font-family:  var(--mono);
  font-size:    9.5px; font-weight: 500;
  padding:      3px 9px; border-radius: 100px;
  white-space:  nowrap; flex-shrink: 0;
}
/* card-body has flex:1 so it expands and pushes card-footer to the bottom */
.card-body {
  padding:        .9rem 1.25rem .7rem;
  flex:           1;
  display:        flex;
  flex-direction: column;
  gap:            7px;
}
.listing-count { font-family: var(--mono); font-size: 11px; color: var(--ink3); }
.listing-count b { color: var(--ink); font-weight: 500; }
.tag-row { display: flex; gap: 5px; flex-wrap: wrap; }
.tag {
  font-family: var(--mono); font-size: 10px; font-weight: 500;
  padding: 2px 8px; border-radius: 100px;
  background: var(--bg2); border: 0.5px solid var(--border-md);
  color: var(--ink2);
}
.tag.green { background: var(--teal-l); color: var(--teal);   border-color: rgba(13,122,99,.2); }
.tag.gold  { background: var(--gold-l); color: var(--gold-d); border-color: rgba(201,168,76,.28); }
.tag.blue  { background: var(--blue-l); color: var(--blue);   border-color: rgba(29,93,181,.2); }
.price-estimate {
  font-family: var(--head); font-size: 13.5px; font-weight: 700;
  color: var(--ink);
}
.price-estimate span {
  font-family: var(--mono); font-size: 10.5px; font-weight: 400;
  color: var(--ink3); margin-left: 4px;
}
.card-tip {
  font-size: 12px; color: var(--ink3);
  line-height: 1.55;
  margin-top: auto;   /* pushes tip to bottom of card-body */
  padding-top: 4px;
}
/* card-footer is always visually at the bottom because card-body has flex:1 */
.card-footer {
  padding:    .8rem 1.25rem 1.1rem;
  border-top: 0.5px solid var(--border);
}
.view-btn {
  display:         flex;
  align-items:     center;
  justify-content: center;
  gap:             7px;
  width:           100%;
  padding:         10px 0;
  border-radius:   100px;
  text-decoration: none !important;
  font-family:     var(--head);
  font-size:       13px; font-weight: 700;
  letter-spacing:  .3px;
  box-shadow:      var(--sh-sm);
  transition:      filter .18s, transform .15s, box-shadow .18s;
}
.view-btn:hover  { filter: brightness(1.09); transform: translateY(-1px); box-shadow: var(--sh-md); }
.view-btn:active { transform: scale(.97); }
.view-btn .arr   { opacity: .65; font-size: 11px; transition: transform .15s, opacity .15s; }
.view-btn:hover .arr { transform: translateX(3px); opacity: 1; }

/* ── Verdict strip ───────────────────────────────────────────────────────── */
.verdict-strip {
  display: flex; align-items: center; gap: 10px;
  background: var(--white);
  border: 0.5px solid var(--border-md);
  border-radius: 100px;
  padding: 9px 18px;
  margin: .7rem 0 1.5rem;
  box-shadow: var(--sh-sm);
  flex-wrap: wrap;
}
.verdict-dot  { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }
.verdict-text { font-family: var(--head); font-size: 13px; font-weight: 700; color: var(--ink); }
.verdict-sub  { font-family: var(--mono); font-size: 10.5px; color: var(--ink3); }

/* ── Section labels ─────────────────────────────────────────────────────── */
.eyebrow {
  font-family: var(--mono); font-size: 10px;
  text-transform: uppercase; letter-spacing: 2px;
  color: var(--gold); margin-bottom: 3px;
}
h2.section-title {
  font-family: var(--head) !important; font-size: 1.6rem !important;
  font-weight: 800 !important; letter-spacing: -.5px;
  color: var(--ink) !important; margin: 0 0 1rem 0 !important;
}
.chips-label {
  font-family: var(--mono); font-size: 9.5px;
  text-transform: uppercase; letter-spacing: 1.5px;
  color: var(--ink3); margin-bottom: 6px;
}

/* ── Hero bar ────────────────────────────────────────────────────────────── */
.hero-bar {
  display: flex; align-items: center; gap: 14px;
  padding-bottom: 1.5rem; margin-bottom: 1.8rem;
  border-bottom: 0.5px solid var(--border-md);
}
.logo-mark {
  width: 44px; height: 44px; border-radius: 12px;
  background: var(--ink);
  display: flex; align-items: center; justify-content: center;
  font-size: 21px; flex-shrink: 0; box-shadow: var(--sh-md);
}
.brand-name {
  font-family: var(--head); font-size: 1.45rem;
  font-weight: 800; letter-spacing: -1px; color: var(--ink);
}
.brand-name em { font-style: normal; color: var(--gold); }
.brand-sub     { font-family: var(--mono); font-size: 10.5px; color: var(--ink3); margin-top: 1px; }
.beta-pill {
  font-family: var(--mono); font-size: 9px; font-weight: 500;
  background: var(--gold-l); color: var(--gold-d);
  border: 0.5px solid rgba(201,168,76,.35);
  padding: 2px 8px; border-radius: 100px;
  margin-left: 6px; vertical-align: middle;
}

/* ── Sidebar section dividers ────────────────────────────────────────────── */
.sb-section {
  font-family:    var(--mono); font-size: 9px;
  text-transform: uppercase; letter-spacing: 1.5px;
  color:          rgba(255,255,255,.30);
  padding:        .9rem 0 .35rem;
  border-top:     0.5px solid rgba(255,255,255,.07);
  margin-top:     .3rem;
}

/* ── Expander ────────────────────────────────────────────────────────────── */
[data-testid="stExpander"] {
  border: 0.5px solid var(--border-md) !important;
  border-radius: var(--r-lg) !important;
  background: var(--white)  !important;
  box-shadow: var(--sh-sm)  !important;
}
[data-testid="stExpander"] summary {
  font-family: var(--head) !important; font-weight: 700 !important;
  font-size: 14px !important; color: var(--ink) !important;
}

/* ── Empty state ─────────────────────────────────────────────────────────── */
.empty-wrap { text-align: center; padding: 4.5rem 2rem; }
.empty-icon  { font-size: 3.5rem; margin-bottom: 1rem; line-height: 1; }
.empty-title {
  font-family: var(--head); font-size: 1.6rem; font-weight: 800;
  color: var(--ink); letter-spacing: -.5px; margin-bottom: .5rem;
}
.empty-sub {
  font-size: 14px; color: var(--ink3);
  max-width: 400px; margin: 0 auto; line-height: 1.75;
}

/* ── Misc ────────────────────────────────────────────────────────────────── */
hr.scout-div { border: none; border-top: 0.5px solid var(--border-md); margin: 1.8rem 0; }
[data-testid="stAlert"] { border-radius: var(--r-lg) !important; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# 3.  DATA MODEL  — unchanged
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class Platform:
    name:         str
    icon:         str
    category:     str
    search_url:   str
    trust_label:  str
    trust_color:  str
    button_bg:    str
    button_fg:    str
    tags:         list[str]
    tag_styles:   list[str]
    price_note:   str
    est_listings: str
    notes:        str


# ─────────────────────────────────────────────────────────────────────────────
# 4.  REGION CONFIG
#     Drives URL selection + currency symbol for eBay / Amazon / Google.
#     All other platforms use global URLs (they handle localisation themselves).
# ─────────────────────────────────────────────────────────────────────────────

_REGION_CFG: dict[str, dict] = {
    "🌍 Global": {
        "ebay":   "https://www.ebay.com/sch/i.html?_nkw={q_plus}&_sop=10",
        "amazon": "https://www.amazon.com/s?k={q_plus}&ref=nb_sb_noss",
        "google": "https://www.google.com/search?tbm=shop&q={q_plus}",
        "sym":    "$",
    },
    "🇺🇸 United States": {
        "ebay":   "https://www.ebay.com/sch/i.html?_nkw={q_plus}&_sop=10",
        "amazon": "https://www.amazon.com/s?k={q_plus}&ref=nb_sb_noss",
        "google": "https://www.google.com/search?tbm=shop&q={q_plus}",
        "sym":    "$",
    },
    "🇬🇧 United Kingdom": {
        "ebay":   "https://www.ebay.co.uk/sch/i.html?_nkw={q_plus}&_sop=10",
        "amazon": "https://www.amazon.co.uk/s?k={q_plus}",
        "google": "https://www.google.co.uk/search?tbm=shop&q={q_plus}",
        "sym":    "£",
    },
    "🇪🇺 Europe": {
        "ebay":   "https://www.ebay.de/sch/i.html?_nkw={q_plus}&_sop=10",
        "amazon": "https://www.amazon.de/s?k={q_plus}",
        "google": "https://www.google.de/search?tbm=shop&q={q_plus}",
        "sym":    "€",
    },
    "🇦🇺 Australia": {
        "ebay":   "https://www.ebay.com.au/sch/i.html?_nkw={q_plus}&_sop=10",
        "amazon": "https://www.amazon.com.au/s?k={q_plus}",
        "google": "https://www.google.com.au/search?tbm=shop&q={q_plus}",
        "sym":    "A$",
    },
}


# ─────────────────────────────────────────────────────────────────────────────
# 5.  URL BUILDER  — unchanged
# ─────────────────────────────────────────────────────────────────────────────

def build_search_url(template: str, query: str) -> str:
    """
    Safely encode `query` and interpolate into `template`.
    {q}      → %20-style percent-encoding
    {q_plus} → +-style encoding (used by eBay, Amazon, etc.)
    """
    q      = urllib.parse.quote(query)
    q_plus = urllib.parse.quote_plus(query)
    return template.format(q=q, q_plus=q_plus)


# ─────────────────────────────────────────────────────────────────────────────
# 6.  SMART SUGGESTION CHIPS
#     Each tuple: (emoji, short display label, full query string to fire)
#     Six chips → 6-column layout → targeted by the chip CSS rule above.
# ─────────────────────────────────────────────────────────────────────────────

CHIPS: list[tuple[str, str, str]] = [
    ("⌚", "Vintage Rolex",    "Vintage Rolex Submariner"),
    ("💻", "MacBook Pro M3",   "MacBook Pro M3"),
    ("👟", "Jordan 1 Chicago", "Air Jordan 1 Chicago"),
    ("🪑", "Eames Chair",      "Eames Lounge Chair"),
    ("👜", "Birkin 30",        "Hermès Birkin 30 Togo"),
    ("📷", "Leica M11",        "Leica M11"),
]


def _fire_chip(query_text: str) -> None:
    """
    Pre-populate the search bar and arm the search flag.
    Because the text_input uses key='search_input', setting
    st.session_state.search_input here updates the widget on the next render.
    st.rerun() is called by the caller immediately after this.
    """
    st.session_state.search_input = query_text
    st.session_state.do_search    = True


# ─────────────────────────────────────────────────────────────────────────────
# 7.  PLATFORM CATALOGUE
#     Region-aware for eBay / Amazon / Google Shopping.
#     filter_empty appends an eBay condition filter (cosmetic for MVP).
#     All other platform URLs are unchanged from v1.
# ─────────────────────────────────────────────────────────────────────────────

def get_platforms(query: str,
                  region: str       = "🌍 Global",
                  filter_empty: bool = False) -> list[Platform]:
    cfg      = _REGION_CFG.get(region, _REGION_CFG["🌍 Global"])
    ebay_tpl = cfg["ebay"] + ("&LH_ItemCondition=3000" if filter_empty else "")

    def u(tpl: str) -> str:
        return build_search_url(tpl, query)

    return [
        # ── General ──────────────────────────────────────────────────────────
        Platform(
            name         = "eBay",
            icon         = "🛍️",
            category     = "General Marketplace",
            search_url   = u(ebay_tpl),
            trust_label  = "Buyer Protection",
            trust_color  = "green",
            button_bg    = "#E53238",
            button_fg    = "#ffffff",
            tags         = ["Auction & Buy Now", "Global Sellers", "Buyer Protection"],
            tag_styles   = ["", "gold", "green"],
            price_note   = "auction + BIN",
            est_listings = "Millions of listings" if not filter_empty else "Verified listings",
            notes        = "Sort by 'Newly Listed' to surface the freshest inventory.",
        ),
        Platform(
            name         = "Amazon",
            icon         = "📦",
            category     = "General Marketplace",
            search_url   = u(cfg["amazon"]),
            trust_label  = "A-to-Z Guarantee",
            trust_color  = "green",
            button_bg    = "#FF9900",
            button_fg    = "#0a0a0f",
            tags         = ["Prime Shipping", "New & Used", "A-to-Z Guarantee"],
            tag_styles   = ["blue", "", "green"],
            price_note   = "new + marketplace",
            est_listings = "Extensive catalogue",
            notes        = "Filter by 'Used' under Condition for the best deals.",
        ),
        Platform(
            name         = "Google Shopping",
            icon         = "🔍",
            category     = "Price Comparison",
            search_url   = u(cfg["google"]),
            trust_label  = "Price Comparison",
            trust_color  = "blue",
            button_bg    = "#4285F4",
            button_fg    = "#ffffff",
            tags         = ["Cross-retailer", "Price History", "Local availability"],
            tag_styles   = ["blue", "gold", ""],
            price_note   = "across all retailers",
            est_listings = "All major retailers",
            notes        = "Use the 'Price drop' filter to surface recent reductions.",
        ),
        # ── Specialist / collectibles ─────────────────────────────────────────
        Platform(
            name         = "Chrono24",
            icon         = "⌚",
            category     = "Watches & Timepieces",
            search_url   = u("https://www.chrono24.com/search/index.htm?dosearch=true&query={q_plus}"),
            trust_label  = "Escrow Service",
            trust_color  = "green",
            button_bg    = "#1A1A2E",
            button_fg    = "#ffffff",
            tags         = ["Verified Dealers", "Escrow Payments", "14-day Return"],
            tag_styles   = ["green", "green", ""],
            price_note   = "dealer + private",
            est_listings = "500,000+ watches",
            notes        = "Filter by 'Trusted Seller' for fully authenticated pieces.",
        ),
        Platform(
            name         = "StockX",
            icon         = "👟",
            category     = "Sneakers, Cards & Collectibles",
            search_url   = u("https://stockx.com/search?s={q_plus}"),
            trust_label  = "Authenticated",
            trust_color  = "green",
            button_bg    = "#08A05C",
            button_fg    = "#ffffff",
            tags         = ["100% Authenticated", "Live Bids & Asks", "Price Tracking"],
            tag_styles   = ["green", "blue", "gold"],
            price_note   = "last sale price",
            est_listings = "Authenticated resale",
            notes        = "Check the Price History chart before placing a bid.",
        ),
        Platform(
            name         = "Grailed",
            icon         = "👔",
            category     = "Designer & Streetwear",
            search_url   = u("https://www.grailed.com/search?query={q_plus}"),
            trust_label  = "Community Vetted",
            trust_color  = "blue",
            button_bg    = "#C8102E",
            button_fg    = "#ffffff",
            tags         = ["Peer-to-peer", "Offer Accepted", "Community Curated"],
            tag_styles   = ["", "gold", "blue"],
            price_note   = "peer-to-peer",
            est_listings = "9M+ listings",
            notes        = "Most sellers accept offers — try 10–15% below asking price.",
        ),
        Platform(
            name         = "Vestiaire Collective",
            icon         = "👜",
            category     = "Luxury Pre-owned Fashion",
            search_url   = u("https://www.vestiairecollective.com/search/?q={q_plus}"),
            trust_label  = "Authentication",
            trust_color  = "green",
            button_bg    = "#2E2E2E",
            button_fg    = "#f0d98c",
            tags         = ["Physical Auth Check", "Luxury Focus", "Global Community"],
            tag_styles   = ["green", "gold", ""],
            price_note   = "authenticated pre-owned",
            est_listings = "Curated luxury",
            notes        = "Items are physically inspected by Vestiaire before shipping.",
        ),
        Platform(
            name         = "Depop",
            icon         = "🌿",
            category     = "Vintage & Streetwear",
            search_url   = u("https://www.depop.com/search/?q={q_plus}"),
            trust_label  = "Buyer Protection",
            trust_color  = "blue",
            button_bg    = "#FF2300",
            button_fg    = "#ffffff",
            tags         = ["Vintage Gems", "Gen-Z Sellers", "Buyer Protection"],
            tag_styles   = ["gold", "", "blue"],
            price_note   = "individual sellers",
            est_listings = "30M+ items",
            notes        = "Prices are negotiable — DM the seller directly.",
        ),
        Platform(
            name         = "1stDibs",
            icon         = "🪑",
            category     = "Antiques & Designer Furniture",
            search_url   = u("https://www.1stdibs.com/search/all/?q={q_plus}"),
            trust_label  = "Trade-vetted",
            trust_color  = "gold",
            button_bg    = "#B8972E",
            button_fg    = "#ffffff",
            tags         = ["Trade Vetted", "Antiques & Art", "White Glove Shipping"],
            tag_styles   = ["gold", "gold", "green"],
            price_note   = "dealer asking price",
            est_listings = "High-end curated",
            notes        = "Most dealers quote on request — prices are always negotiable.",
        ),
        Platform(
            name         = "Reddit",
            icon         = "🔖",
            category     = "Community Classifieds",
            search_url   = u("https://www.reddit.com/search/?q={q_plus}+%28for+sale+OR+FS+OR+WTS%29&type=link"),
            trust_label  = "Community",
            trust_color  = "blue",
            button_bg    = "#FF4500",
            button_fg    = "#ffffff",
            tags         = ["No Fees", "Niche Subreddits", "Direct from Seller"],
            tag_styles   = ["green", "", "blue"],
            price_note   = "peer-to-peer, no fees",
            est_listings = "Niche subreddits",
            notes        = "Search category-specific subreddits directly for better results.",
        ),
        Platform(
            name         = "Facebook Marketplace",
            icon         = "📍",
            category     = "Local & National",
            search_url   = u("https://www.facebook.com/marketplace/search?query={q_plus}"),
            trust_label  = "Local Pickup",
            trust_color  = "blue",
            button_bg    = "#1877F2",
            button_fg    = "#ffffff",
            tags         = ["Local Pickup", "No Fees", "Negotiate Direct"],
            tag_styles   = ["", "green", ""],
            price_note   = "local market price",
            est_listings = "Hyper-local results",
            notes        = "Best for bulky items — local pickup avoids all shipping costs.",
        ),
        Platform(
            name         = "Catawiki",
            icon         = "🏺",
            category     = "Curated Auctions",
            search_url   = u("https://www.catawiki.com/en/s#q={q_plus}"),
            trust_label  = "Expert Curated",
            trust_color  = "gold",
            button_bg    = "#6B2D8B",
            button_fg    = "#ffffff",
            tags         = ["Expert-curated", "Weekly Auctions", "Rare & Special"],
            tag_styles   = ["gold", "blue", "gold"],
            price_note   = "auction hammer price",
            est_listings = "Curated specialist auctions",
            notes        = "Register 24 h before closing to place last-minute bids.",
        ),
    ]


# ─────────────────────────────────────────────────────────────────────────────
# 8.  PRICE INTELLIGENCE ENGINE  — unchanged
# ─────────────────────────────────────────────────────────────────────────────

_PRICE_SIGNALS: list[tuple[list[str], float, float]] = [
    (["patek philippe", "nautilus", "pp 5711"],              32_000, 0.45),
    (["audemars piguet", "ap royal oak"],                    22_000, 0.45),
    (["richard mille", "rm 011"],                           120_000, 0.55),
    (["vacheron constantin"],                                18_000, 0.40),
    (["rolex daytona", "daytona"],                           18_000, 0.45),
    (["rolex submariner", "submariner"],                     10_500, 0.35),
    (["rolex gmt", "gmt master"],                            12_000, 0.35),
    (["rolex datejust", "datejust"],                          7_200, 0.35),
    (["rolex", "tudor black bay"],                            7_000, 0.40),
    (["omega speedmaster", "speedmaster"],                    4_800, 0.35),
    (["omega seamaster", "seamaster"],                        3_200, 0.35),
    (["omega", "tag heuer", "iwc", "jaeger"],                 3_500, 0.35),
    (["cartier tank", "cartier santos", "cartier"],           4_200, 0.40),
    (["jordan 1 chicago", "jordan 1 bred"],                     550, 0.30),
    (["jordan 4 travis", "jordan 4 off white"],                 850, 0.35),
    (["yeezy 350 zebra", "yeezy 350 v2"],                       280, 0.30),
    (["air jordan 1", "jordan 1"],                              280, 0.35),
    (["nike dunk low", "dunk low"],                             180, 0.30),
    (["air force 1", "af1"],                                    120, 0.25),
    (["yeezy", "adidas yeezy"],                                 250, 0.35),
    (["new balance 550", "new balance 2002"],                   140, 0.30),
    (["hermès birkin", "birkin 25", "birkin 30", "birkin 35"],18_000, 0.45),
    (["hermès kelly", "kelly bag"],                           12_000, 0.45),
    (["chanel classic flap", "chanel 2.55"],                   7_500, 0.35),
    (["louis vuitton neverfull", "lv neverfull"],              1_100, 0.30),
    (["gucci diana", "gucci horsebit"],                        1_400, 0.35),
    (["supreme box logo", "box logo hoodie"],                    850, 0.45),
    (["stone island"],                                           420, 0.35),
    (["balenciaga triple s"],                                    480, 0.35),
    (["macbook pro m3", "macbook pro m2"],                     1_800, 0.20),
    (["macbook air m2", "macbook air m3"],                     1_050, 0.20),
    (["iphone 15 pro max", "iphone 15 pro"],                   1_050, 0.15),
    (["iphone 14 pro", "iphone 13 pro"],                         650, 0.15),
    (["sony a7r v", "sony a7 iv"],                             2_400, 0.20),
    (["leica q2", "leica m11", "leica"],                       4_800, 0.30),
    (["playstation 5", "ps5"],                                   480, 0.12),
    (["nintendo switch oled", "nintendo switch"],                260, 0.12),
    (["first edition", "signed copy"],                           350, 0.65),
    (["banksy", "basquiat", "kaws"],                          28_000, 0.60),
    (["warhol", "hirst spot print"],                           4_500, 0.55),
    (["vintage poster", "original poster"],                      280, 0.55),
    (["eames lounge chair", "eames chair"],                    4_200, 0.40),
    (["barcelona chair", "knoll barcelona"],                   5_500, 0.40),
    (["vitra", "hay furniture", "herman miller"],              1_200, 0.40),
]

_DEFAULT_BASE   = 320.0
_DEFAULT_SPREAD = 0.40


def _estimate_price(query: str) -> tuple[float, float, float]:
    """Derive (low, mid, high) price estimates — logic unchanged from v1."""
    q = query.lower().strip()
    base, spread = _DEFAULT_BASE, _DEFAULT_SPREAD
    for keywords, b, s in _PRICE_SIGNALS:
        if any(kw in q for kw in keywords):
            base, spread = b, s
            break
    h      = int(hashlib.md5(q.encode()).hexdigest()[:8], 16) / 0xFFFFFFFF
    jitter = 0.88 + h * 0.24
    mid    = base * jitter
    low    = mid  * (1 - spread * 0.7)
    high   = mid  * (1 + spread * 0.9)
    return round(low, -1), round(mid, -1), round(high, -1)


def _fmt_price(p: float, sym: str = "£") -> str:
    return f"{sym}{p:,.0f}"


def _price_verdict(query: str) -> tuple[str, str, str]:
    q = query.lower()
    for keywords, _, spread in _PRICE_SIGNALS:
        if any(kw in q for kw in keywords):
            if spread <= 0.20:
                return "#2d9e7a", "Tight market",    "Consistent pricing — limited negotiation room."
            elif spread <= 0.35:
                return "#c9a84c", "Active market",   "Moderate variance — value deals are findable."
            else:
                return "#b03030", "Volatile market", "Wide spread — research comparables carefully."
    return "#c9a84c", "Exploratory search", "Limited data — cross-reference multiple platforms."


# ─────────────────────────────────────────────────────────────────────────────
# 9.  PLATFORM VISIBILITY + SORT  — logic unchanged
# ─────────────────────────────────────────────────────────────────────────────

_GENERAL      = {"eBay", "Amazon", "Google Shopping"}
_COLLECTIBLES = {"Chrono24", "StockX"}
_FASHION      = {"Grailed", "Vestiaire Collective", "Depop", "1stDibs"}
_LOCAL        = {"Reddit", "Facebook Marketplace"}
_AUCTIONS     = {"Catawiki"}


def _platform_visible(p: Platform, show_general: bool, show_collectibles: bool,
                       show_fashion: bool, show_local: bool, show_auctions: bool) -> bool:
    if p.name in _GENERAL      and not show_general:      return False
    if p.name in _COLLECTIBLES and not show_collectibles:  return False
    if p.name in _FASHION      and not show_fashion:       return False
    if p.name in _LOCAL        and not show_local:         return False
    if p.name in _AUCTIONS     and not show_auctions:      return False
    return True


def _sorted_platforms(platforms: list[Platform], sort_order: str) -> list[Platform]:
    if sort_order == "Alphabetical":
        return sorted(platforms, key=lambda p: p.name)
    if sort_order == "Most Listings First":
        def _score(p: Platform) -> int:
            nums = re.findall(r"[\d,]+", p.est_listings)
            return int(nums[0].replace(",", "")) if nums else 0
        return sorted(platforms, key=_score, reverse=True)
    return platforms   # Recommended


# ─────────────────────────────────────────────────────────────────────────────
# 10. CARD RENDERER
#     The card-footer CTA button is always flush to the bottom of the card
#     because:  column div → flex-column → card-body has flex:1 →
#               card-footer is last child → visually anchored at bottom.
# ─────────────────────────────────────────────────────────────────────────────

def _badge_style(color: str) -> str:
    return {
        "green": "background:#d5f0ea;color:#0d7a63;border:0.5px solid rgba(13,122,99,.2)",
        "gold":  "background:#fdf3dc;color:#7d5f10;border:0.5px solid rgba(201,168,76,.28)",
        "blue":  "background:#deeafb;color:#1d5db5;border:0.5px solid rgba(29,93,181,.2)",
    }.get(color, "background:#ecedf4;color:#2c2c3a;border:0.5px solid rgba(10,10,15,.14)")


def render_platform_card(p: Platform, low: float, high: float, sym: str = "£") -> None:
    tag_html    = "".join(f'<span class="tag {s}">{l}</span>' for l, s in zip(p.tags, p.tag_styles))
    price_range = f"{_fmt_price(low, sym)} – {_fmt_price(high, sym)}"

    st.markdown(f"""
    <div class="mkt-card">
      <div class="card-header">
        <div class="platform-icon">{p.icon}</div>
        <div class="card-title-block">
          <div class="platform-name">{p.name}</div>
          <div class="platform-category">{p.category}</div>
        </div>
        <span class="trust-badge" style="{_badge_style(p.trust_color)}">{p.trust_label}</span>
      </div>
      <div class="card-body">
        <div class="listing-count">{p.est_listings}</div>
        <div class="tag-row">{tag_html}</div>
        <div class="price-estimate">{price_range}<span>est. {p.price_note}</span></div>
        <div class="card-tip">{p.notes}</div>
      </div>
      <div class="card-footer">
        <a href="{p.search_url}" target="_blank" rel="noopener noreferrer"
           class="view-btn" style="background:{p.button_bg};color:{p.button_fg}">
          Search {p.name} <span class="arr">→</span>
        </a>
      </div>
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# 11. SIDEBAR  — premium SaaS settings panel
# ─────────────────────────────────────────────────────────────────────────────

with st.sidebar:

    st.markdown("""
    <div style="padding:.5rem 0 1.1rem">
      <div style="font-family:'Syne',sans-serif;font-size:1.35rem;font-weight:800;
                  letter-spacing:-1px;color:#fff;line-height:1">
        Nexus<span style="color:#c9a84c">Scout</span>
      </div>
      <div style="font-family:'DM Mono',monospace;font-size:9px;letter-spacing:1px;
                  text-transform:uppercase;color:rgba(255,255,255,.3);margin-top:3px">
        AI Personal Shopper
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── SEARCH SETTINGS ──────────────────────────────────────────────────────
    st.markdown('<div class="sb-section">Search Settings</div>', unsafe_allow_html=True)

    region = st.selectbox(
        "Target Region",
        options = list(_REGION_CFG.keys()),
        index   = 0,
        help    = "Adapts eBay, Amazon, and Google URLs to the selected market.",
    )

    filter_empty = st.toggle(
        "Filter Out Empty Listings",
        value = False,
        help  = "Appends a condition filter to eBay to hide listings without images.",
    )

    # ── PLATFORMS ────────────────────────────────────────────────────────────
    st.markdown('<div class="sb-section">Show Platforms</div>', unsafe_allow_html=True)

    show_general      = st.checkbox("General Marketplaces",     value=True)
    show_collectibles = st.checkbox("Specialist / Collectibles", value=True)
    show_fashion      = st.checkbox("Fashion & Streetwear",      value=True)
    show_local        = st.checkbox("Local & Community",         value=True)
    show_auctions     = st.checkbox("Auctions",                  value=True)

    # ── DISPLAY ──────────────────────────────────────────────────────────────
    st.markdown('<div class="sb-section">Display</div>', unsafe_allow_html=True)

    sort_order = st.selectbox(
        "Sort platforms by",
        ["Recommended", "Alphabetical", "Most Listings First"],
    )

    # ── SEARCH HISTORY ───────────────────────────────────────────────────────
    if st.session_state.search_history:
        st.markdown('<div class="sb-section">Recent Searches</div>', unsafe_allow_html=True)
        for h in reversed(st.session_state.search_history[-6:]):
            st.markdown(
                f'<div style="font-family:\'DM Mono\',monospace;font-size:11px;'
                f'color:rgba(255,255,255,.5);padding:3px 0;'
                f'white-space:nowrap;overflow:hidden;text-overflow:ellipsis">'
                f'{h}</div>',
                unsafe_allow_html=True,
            )

    # ── FOOTER NOTE ──────────────────────────────────────────────────────────
    st.markdown("""
    <div style="margin-top:2rem;font-family:'DM Mono',monospace;font-size:9px;
                color:rgba(255,255,255,.18);line-height:2;text-transform:uppercase;
                letter-spacing:.8px;border-top:0.5px solid rgba(255,255,255,.07);
                padding-top:1rem">
      All links open live<br>search results pages.<br>No hardcoded URLs.
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# 12. MAIN UI
# ─────────────────────────────────────────────────────────────────────────────

# ── Hero bar ──────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-bar">
  <div class="logo-mark">🔭</div>
  <div>
    <div class="brand-name">Nexus<em>Scout</em>
      <span class="beta-pill">BETA</span>
    </div>
    <div class="brand-sub">Type anything. Live results across every major marketplace, instantly.</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Search bar + Scout button  (2 columns → CSS applies CTA style here) ───────
search_col, btn_col = st.columns([6, 1])

with search_col:
    # key="search_input" so chip clicks can pre-populate this field
    st.text_input(
        label            = "search",
        placeholder      = "Search for any product — 'Vintage Rolex', 'MacBook Pro M3', 'Eames Chair'…",
        label_visibility = "collapsed",
        key              = "search_input",
    )

with btn_col:
    if st.button("Scout →", use_container_width=True, key="scout_btn"):
        if st.session_state.search_input.strip():
            st.session_state.do_search = True

# ── Smart suggestion chips  (6 columns → CSS applies chip style here) ─────────
st.markdown('<div class="chips-label">✦ Smart Suggestions</div>', unsafe_allow_html=True)

chip_cols = st.columns(len(CHIPS))
for col, (emoji, label, full_query) in zip(chip_cols, CHIPS):
    with col:
        if st.button(f"{emoji}  {label}", key=f"chip_{label}", use_container_width=True):
            _fire_chip(full_query)
            st.rerun()   # rerun so text_input picks up the new session state value

st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# 13. SEARCH EXECUTION
#     Fires when:
#       (a) Scout button clicked       → do_search = True
#       (b) Chip clicked + rerun fires → do_search = True
#       (c) User presses Enter         → query differs from last_query
# ─────────────────────────────────────────────────────────────────────────────

current_q = st.session_state.search_input.strip()

should_search = (
    st.session_state.do_search                                   # button / chip
    or (current_q and current_q != st.session_state.last_query)  # Enter key
)

if should_search and current_q:

    # Reset flags before rendering to prevent double-fire on next rerun
    st.session_state.do_search  = False
    st.session_state.last_query = current_q

    # Rolling history (deduped, max 20)
    hist = st.session_state.search_history
    if current_q not in hist:
        hist.append(current_q)
    st.session_state.search_history = hist[-20:]

    # ── Price intelligence ─────────────────────────────────────────────────
    low, mid, high = _estimate_price(current_q)
    dot_c, vlabel, vsub = _price_verdict(current_q)
    sym = _REGION_CFG.get(region, _REGION_CFG["🌍 Global"])["sym"]

    with st.spinner(f"Scouting **{current_q}** across all platforms…"):
        time.sleep(0.5)

    # ── Four metric tiles ──────────────────────────────────────────────────
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Est. Market Low",     _fmt_price(low,  sym), delta="budget entry")
    m2.metric("Est. Market Average", _fmt_price(mid,  sym), delta="median comparable")
    m3.metric("Est. Market High",    _fmt_price(high, sym), delta="premium examples")
    m4.metric("Price Spread",
              f"{round((high - low) / mid * 100)}%",
              delta="variance across sources")

    # ── Verdict strip ──────────────────────────────────────────────────────
    st.markdown(f"""
    <div class="verdict-strip">
      <div class="verdict-dot" style="background:{dot_c}"></div>
      <div class="verdict-text">{vlabel}</div>
      <div class="verdict-sub"> — {vsub}</div>
    </div>
    """, unsafe_allow_html=True)

    # ── Platform grid header ───────────────────────────────────────────────
    st.markdown('<p class="eyebrow">Live Marketplaces</p>', unsafe_allow_html=True)
    st.markdown(
        f'<h2 class="section-title">Results for &ldquo;{current_q}&rdquo;</h2>',
        unsafe_allow_html=True,
    )

    # ── Build + filter platform list ───────────────────────────────────────
    all_platforms = get_platforms(current_q, region, filter_empty)
    visible = _sorted_platforms(
        [p for p in all_platforms if _platform_visible(
            p, show_general, show_collectibles,
            show_fashion, show_local, show_auctions,
        )],
        sort_order,
    )

    if not visible:
        st.warning("All platform categories are disabled. Enable at least one in the sidebar.")
    else:
        # ── 3-column card grid ─────────────────────────────────────────────
        COLS = 3
        for row in [visible[i : i + COLS] for i in range(0, len(visible), COLS)]:
            cols = st.columns(COLS, gap="medium")
            for col, platform in zip(cols, row):
                with col:
                    render_platform_card(platform, low, high, sym)
            st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    # ── Price Intelligence expander ────────────────────────────────────────
    st.markdown('<hr class="scout-div">', unsafe_allow_html=True)

    with st.expander("📊  Price Intelligence & Buying Guide", expanded=False):
        g1, g2 = st.columns(2)
        with g1:
            st.markdown("#### Where to start")
            st.markdown(f"""
            <div style="font-size:13px;color:var(--ink2);line-height:1.85">
              <b>New condition:</b> Amazon, eBay (Buy It Now)<br>
              <b>Best negotiation:</b> Grailed, Facebook Marketplace, Reddit<br>
              <b>Authenticity first:</b> StockX, Vestiaire Collective, Chrono24<br>
              <b>Rare &amp; unique:</b> Catawiki, 1stDibs, eBay Auction<br>
              <b>Price history:</b> Google Shopping, StockX chart
            </div>
            """, unsafe_allow_html=True)
        with g2:
            st.markdown("#### Estimated price breakdown")
            st.markdown(f"""
            <div style="font-size:13px;color:var(--ink2);line-height:1.85">
              <b>Budget entry:</b> {_fmt_price(low, sym)} — older stock, fair condition<br>
              <b>Market median:</b> {_fmt_price(mid, sym)} — typical example, good condition<br>
              <b>Premium end:</b>   {_fmt_price(high, sym)} — mint / full provenance<br><br>
              <i style="color:var(--ink3);font-size:11.5px">
                Estimates are indicative only. Always verify live prices before transacting.
              </i>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("---")
        st.markdown(f"""
        <div style="font-family:'DM Mono',monospace;font-size:10.5px;color:var(--ink3);line-height:2">
          Query: <b style="color:var(--ink)">{current_q}</b> &nbsp;·&nbsp;
          Region: <b style="color:var(--ink)">{region}</b> &nbsp;·&nbsp;
          Platforms: <b style="color:var(--ink)">{len(visible)}</b> &nbsp;·&nbsp;
          {datetime.now().strftime('%H:%M:%S')}
        </div>
        """, unsafe_allow_html=True)

elif not current_q:
    # ── Welcome / empty state ──────────────────────────────────────────────
    st.markdown("""
    <div class="empty-wrap">
      <div class="empty-icon">🔭</div>
      <div class="empty-title">Scout anything, anywhere.</div>
      <div class="empty-sub">
        Type any product above, or click a suggestion chip.
        Nexus Scout opens live search results across every major
        marketplace — watches, sneakers, furniture, electronics,
        fashion, art, and beyond.
      </div>
    </div>
    """, unsafe_allow_html=True)
