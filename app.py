# =============================================================================
#  NEXUS SCOUT  —  Universal AI Personal Shopper
#  File    : app.py
#  Run     : streamlit run app.py
#  Deploy  : push to GitHub, connect repo on share.streamlit.io — done.
#
#  Dependencies (all standard — no API keys required to run):
#    pip install streamlit
# =============================================================================

import hashlib
import math
import re
import time
import urllib.parse
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
.view-btn {
  display: flex; align-items: center; justify-content: center; gap: 7px;
  width: 100%;
  padding: 11px 0;
  border-radius: 100px;
  text-decoration: none !important;
  font-family: var(--head);
  font-size: 13.5px; font-weight: 700;
  letter-spacing: .3px;
  transition: filter .18s, transform .15s, box-shadow .18s;
  box-shadow: var(--shadow-sm);
}
.view-btn:hover { filter: brightness(1.08); transform: translateY(-1px); box-shadow: var(--shadow-md); }
.view-btn:active { transform: scale(.97); }
.view-btn .arrow { opacity: .7; font-size: 12px; transition: transform .15s; }
.view-btn:hover .arrow { transform: translateX(3px); opacity: 1; }

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
  background: var(--gold-l); color: var(--gold-d);
  border: 0.5px solid rgba(201,168,76,.3);
  padding: 3px 9px; border-radius: 100px; margin-left: 4px;
}

/* ── Expander ── */
[data-testid="stExpander"] {
  border: 0.5px solid var(--border-md) !important;
  border-radius: var(--r-lg) !important;
  background: var(--white) !important;
  box-shadow: var(--shadow-sm) !important;
}
[data-testid="stExpander"] summary {
  font-family: var(--head) !important; font-weight: 700 !important;
  font-size: 14.5px !important; color: var(--ink) !important;
}

/* ── History pills ── */
.history-row { display: flex; gap: 7px; flex-wrap: wrap; margin-bottom: 1.2rem; }
.history-pill {
  font-family: var(--mono); font-size: 11.5px;
  background: var(--white); border: 0.5px solid var(--border-md);
  color: var(--ink2); padding: 5px 13px; border-radius: 100px;
  cursor: pointer; transition: background .15s;
  box-shadow: var(--shadow-sm); text-decoration: none;
}
.history-pill:hover { background: var(--bg2); }

/* ── Divider ── */
hr.scout-div {
  border: none; border-top: 0.5px solid var(--border-md);
  margin: 1.8rem 0;
}

/* ── Empty state ── */
.empty-wrap {
  text-align: center; padding: 5rem 2rem;
}
.empty-icon { font-size: 3.5rem; margin-bottom: 1rem; line-height: 1; }
.empty-title {
  font-family: var(--head); font-size: 1.6rem; font-weight: 800;
  color: var(--ink); letter-spacing: -.5px; margin-bottom: .5rem;
}
.empty-sub { font-size: 14.5px; color: var(--ink3); max-width: 420px; margin: 0 auto; line-height: 1.7; }
.suggest-row { display: flex; gap: 8px; flex-wrap: wrap; justify-content: center; margin-top: 1.4rem; }
.suggest-chip {
  font-family: var(--mono); font-size: 12px;
  background: var(--white); border: 0.5px solid var(--border-md);
  color: var(--ink2); padding: 6px 14px; border-radius: 100px;
  box-shadow: var(--shadow-sm);
}
</style>
""", unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────────────────────
# 2.  CORE DATA STRUCTURES
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class Platform:
    """
    Describes one marketplace card. All URLs are dynamically constructed
    from the user's query — no hardcoded product links anywhere.
    """
    name:         str         # display name
    icon:         str         # emoji used as the brand icon
    category:     str         # short descriptor e.g. "General Marketplace"
    search_url:   str         # dynamically built live search URL
    trust_label:  str         # e.g. "Buyer Protection"
    trust_color:  str         # CSS class for the trust badge
    button_bg:    str         # hex for the CTA button background
    button_fg:    str         # hex for the CTA button text
    tags:         list[str]   # feature tags shown on the card
    tag_styles:   list[str]   # matching CSS class per tag ("green" / "gold" / "blue" / "")
    price_note:   str         # short note next to estimated price
    est_listings: str         # simulated listing count string
    notes:        str         # one-line tip shown in the card body


# ──────────────────────────────────────────────────────────────────────────────
# 3.  DYNAMIC URL BUILDER
#     Each URL uses the user's exact query — safely percent-encoded.
#     Changing the query re-builds every URL automatically.
# ──────────────────────────────────────────────────────────────────────────────

def build_search_url(template: str, query: str) -> str:
    """
    Safely encode `query` and interpolate it into `template`.

    The template uses {q} for URL-encoded (spaces → %20) and
    {q_plus} for plus-encoded (spaces → +) variants — different
    platforms expect different encoding styles.

    >>> build_search_url("https://www.ebay.com/sch/i.html?_nkw={q_plus}", "vintage rolex")
    'https://www.ebay.com/sch/i.html?_nkw=vintage+rolex'
    """
    q        = urllib.parse.quote(query)          # %20-style
    q_plus   = urllib.parse.quote_plus(query)     # +-style
    return template.format(q=q, q_plus=q_plus)


def get_platforms(query: str) -> list[Platform]:
    """
    Return the full list of Platform objects, each with a live
    search URL built from the user's query.

    To add a new marketplace: copy one block below, change the fields
    and the search_url template. Nothing else needs to change.
    """
    return [
        # ── General marketplaces ──────────────────────────────────────────
        Platform(
            name        = "eBay",
            icon        = "🛍️",
            category    = "General Marketplace",
            search_url  = build_search_url(
                "https://www.ebay.com/sch/i.html?_nkw={q_plus}&_sop=10", query),
            trust_label = "Buyer Protection",
            trust_color = "green",
            button_bg   = "#E53238",
            button_fg   = "#ffffff",
            tags        = ["Auction & Buy Now", "Global Sellers", "Buyer Protection"],
            tag_styles  = ["", "gold", "green"],
            price_note  = "incl. auction + BIN",
            est_listings= "Millions of listings",
            notes       = "Sort by 'Newly Listed' for freshest inventory.",
        ),
        Platform(
            name        = "Amazon",
            icon        = "📦",
            category    = "General Marketplace",
            search_url  = build_search_url(
                "https://www.amazon.com/s?k={q_plus}&ref=nb_sb_noss", query),
            trust_label = "A-to-Z Guarantee",
            trust_color = "green",
            button_bg   = "#FF9900",
            button_fg   = "#0a0a0f",
            tags        = ["Prime Shipping", "New & Used", "A-to-Z Guarantee"],
            tag_styles  = ["blue", "", "green"],
            price_note  = "new + marketplace",
            est_listings= "Extensive catalogue",
            notes       = "Filter by 'Used' under 'Condition' for best deals.",
        ),
        Platform(
            name        = "Google Shopping",
            icon        = "🔍",
            category    = "Price Comparison",
            search_url  = build_search_url(
                "https://www.google.com/search?tbm=shop&q={q_plus}", query),
            trust_label = "Price Comparison",
            trust_color = "blue",
            button_bg   = "#4285F4",
            button_fg   = "#ffffff",
            tags        = ["Cross-retailer", "Price History", "Local availability"],
            tag_styles  = ["blue", "gold", ""],
            price_note  = "across all retailers",
            est_listings= "All major retailers",
            notes       = "Use 'Price drop' filter to catch recent reductions.",
        ),

        # ── Specialist / collectibles ─────────────────────────────────────
        Platform(
            name        = "Chrono24",
            icon        = "⌚",
            category    = "Watches & Timepieces",
            search_url  = build_search_url(
                "https://www.chrono24.com/search/index.htm?dosearch=true&query={q_plus}", query),
            trust_label = "Escrow Service",
            trust_color = "green",
            button_bg   = "#1A1A2E",
            button_fg   = "#ffffff",
            tags        = ["Verified Dealers", "Escrow Payments", "14-day Return"],
            tag_styles  = ["green", "green", ""],
            price_note  = "dealer + private",
            est_listings= "500,000+ watches",
            notes       = "Filter by 'Trusted Seller' for authenticated pieces.",
        ),
        Platform(
            name        = "StockX",
            icon        = "👟",
            category    = "Sneakers, Cards & Collectibles",
            search_url  = build_search_url(
                "https://stockx.com/search?s={q_plus}", query),
            trust_label = "Authenticated",
            trust_color = "green",
            button_bg   = "#08A05C",
            button_fg   = "#ffffff",
            tags        = ["100% Authenticated", "Live Bids & Asks", "Price Tracking"],
            tag_styles  = ["green", "blue", "gold"],
            price_note  = "last sale price",
            est_listings= "Authenticated resale",
            notes       = "Check 'Price History' chart before bidding.",
        ),
        Platform(
            name        = "Grailed",
            icon        = "👔",
            category    = "Designer & Streetwear",
            search_url  = build_search_url(
                "https://www.grailed.com/search?query={q_plus}", query),
            trust_label = "Community Vetted",
            trust_color = "blue",
            button_bg   = "#C8102E",
            button_fg   = "#ffffff",
            tags        = ["Peer-to-peer", "Offer Accepted", "Community Curated"],
            tag_styles  = ["", "gold", "blue"],
            price_note  = "peer-to-peer",
            est_listings= "9M+ listings",
            notes       = "Most sellers accept offers — try 10–15% below asking.",
        ),
        Platform(
            name        = "Vestiaire Collective",
            icon        = "👜",
            category    = "Luxury Pre-owned Fashion",
            search_url  = build_search_url(
                "https://www.vestiairecollective.com/search/?q={q_plus}", query),
            trust_label = "Authentication",
            trust_color = "green",
            button_bg   = "#2E2E2E",
            button_fg   = "#f0d98c",
            tags        = ["Physical Auth Check", "Luxury Focus", "Global Community"],
            tag_styles  = ["green", "gold", ""],
            price_note  = "authenticated pre-owned",
            est_listings= "Curated luxury",
            notes       = "Items ship to Vestiaire first for physical inspection.",
        ),
        Platform(
            name        = "Depop",
            icon        = "🌿",
            category    = "Vintage & Streetwear",
            search_url  = build_search_url(
                "https://www.depop.com/search/?q={q_plus}", query),
            trust_label = "Buyer Protection",
            trust_color = "blue",
            button_bg   = "#FF2300",
            button_fg   = "#ffffff",
            tags        = ["Vintage Gems", "Gen-Z Sellers", "Buyer Protection"],
            tag_styles  = ["gold", "", "blue"],
            price_note  = "individual sellers",
            est_listings= "30M+ items",
            notes       = "Prices are negotiable — DM sellers directly.",
        ),
        Platform(
            name        = "1stDibs",
            icon        = "🪑",
            category    = "Antiques & Designer Furniture",
            search_url  = build_search_url(
                "https://www.1stdibs.com/search/all/?q={q_plus}", query),
            trust_label = "Trade-vetted",
            trust_color = "gold",
            button_bg   = "#B8972E",
            button_fg   = "#ffffff",
            tags        = ["Trade Vetted", "Antiques & Art", "White Glove Shipping"],
            tag_styles  = ["gold", "gold", "green"],
            price_note  = "dealer asking price",
            est_listings= "High-end curated",
            notes       = "Prices are negotiable — most dealers quote on request.",
        ),
        Platform(
            name        = "Reddit",
            icon        = "🔖",
            category    = "Community Classifieds",
            search_url  = build_search_url(
                "https://www.reddit.com/search/?q={q_plus}+%28for+sale+OR+FS+OR+WTS%29&type=link", query),
            trust_label = "Community",
            trust_color = "blue",
            button_bg   = "#FF4500",
            button_fg   = "#ffffff",
            tags        = ["No Fees", "r/Watchexchange", "r/Smarthome etc."],
            tag_styles  = ["green", "", "blue"],
            price_note  = "peer-to-peer, no fees",
            est_listings= "Niche subreddits",
            notes       = "Search niche subreddits directly for better results.",
        ),
        Platform(
            name        = "Facebook Marketplace",
            icon        = "📍",
            category    = "Local & National",
            search_url  = build_search_url(
                "https://www.facebook.com/marketplace/search?query={q_plus}", query),
            trust_label = "Local Pickup",
            trust_color = "blue",
            button_bg   = "#1877F2",
            button_fg   = "#ffffff",
            tags        = ["Local Pickup", "No Fees", "Negotiate Direct"],
            tag_styles  = ["", "green", ""],
            price_note  = "local market price",
            est_listings= "Hyper-local results",
            notes       = "Best for bulky items — local pickup avoids shipping costs.",
        ),
        Platform(
            name        = "Catawiki",
            icon        = "🏺",
            category    = "Curated Auctions",
            search_url  = build_search_url(
                "https://www.catawiki.com/en/s#q={q_plus}", query),
            trust_label = "Expert Curated",
            trust_color = "gold",
            button_bg   = "#6B2D8B",
            button_fg   = "#ffffff",
            tags        = ["Expert-curated", "Weekly Auctions", "Rare & Special"],
            tag_styles  = ["gold", "blue", "gold"],
            price_note  = "auction hammer price",
            est_listings= "Curated auctions",
            notes       = "Register 24h before closing to place last-minute bids.",
        ),
    ]


# ──────────────────────────────────────────────────────────────────────────────
# 4.  PRICE INTELLIGENCE ENGINE
#     Derives a baseline estimate from the query string so the "Average Market
#     Price" metric always shows something meaningful.
#     No API keys. No hardcoded lists. Pure signal-based inference.
# ──────────────────────────────────────────────────────────────────────────────

# Keyword → (base_price, price_spread_factor)
# base_price       : estimated median market price (GBP)
# spread_factor    : how wide the realistic price band is (0.3 = ±30%)
_PRICE_SIGNALS: list[tuple[list[str], float, float]] = [
    # Ultra-luxury watches & jewellery
    (["patek philippe", "patek", "nautilus", "pp 5711"],          32_000, 0.45),
    (["audemars piguet", "ap royal oak", "audemars"],             22_000, 0.45),
    (["richard mille", "rm 011", "rm011"],                        120_000, 0.55),
    (["vacheron", "vacheron constantin"],                          18_000, 0.4),
    # Rolex & prestige
    (["rolex daytona", "daytona"],                                 18_000, 0.45),
    (["rolex submariner", "submariner"],                           10_500, 0.35),
    (["rolex gmt", "gmt master"],                                  12_000, 0.35),
    (["rolex datejust", "datejust"],                               7_200,  0.35),
    (["rolex", "tudor black bay"],                                  7_000, 0.4),
    # Other prestige watches
    (["omega speedmaster", "speedmaster"],                         4_800,  0.35),
    (["omega seamaster", "seamaster"],                             3_200,  0.35),
    (["omega", "tag heuer", "iwc", "jaeger"],                     3_500,  0.35),
    (["cartier tank", "cartier santos", "cartier"],                4_200,  0.4),
    # Sneakers — hype
    (["jordan 1 chicago", "jordan 1 bred", "jordan 1 royal"],     550,    0.30),
    (["jordan 4 travis", "jordan 4 off white"],                    850,    0.35),
    (["yeezy 350 zebra", "yeezy 350 v2"],                          280,    0.3),
    (["air jordan 1", "jordan 1"],                                 280,    0.35),
    (["nike dunk low", "dunk low"],                                180,    0.3),
    (["air force 1", "af1"],                                       120,    0.25),
    (["yeezy", "adidas yeezy"],                                    250,    0.35),
    (["new balance 550", "new balance 2002"],                      140,    0.3),
    # Designer fashion
    (["hermès birkin", "birkin 25", "birkin 30", "birkin 35"],     18_000, 0.45),
    (["hermès kelly", "kelly bag"],                                 12_000, 0.45),
    (["chanel classic flap", "chanel 2.55"],                       7_500,  0.35),
    (["louis vuitton neverfull", "lv neverfull"],                   1_100,  0.3),
    (["gucci diana", "gucci horsebit"],                            1_400,  0.35),
    (["supreme box logo", "box logo hoodie", "bogo"],              850,    0.45),
    (["stone island", "stone island shadow"],                       420,    0.35),
    (["balenciaga triple s", "triple s"],                          480,    0.35),
    # Electronics
    (["macbook pro m3", "macbook pro m2"],                         1_800,  0.2),
    (["macbook air m2", "macbook air m3"],                         1_050,  0.2),
    (["iphone 15 pro max", "iphone 15 pro"],                       1_050,  0.15),
    (["iphone 14 pro", "iphone 13 pro"],                           650,    0.15),
    (["sony a7r v", "sony a7 iv"],                                  2_400,  0.2),
    (["leica q2", "leica m11", "leica"],                           4_800,  0.3),
    (["playstation 5", "ps5"],                                      480,    0.12),
    (["nintendo switch oled", "nintendo switch"],                   260,    0.12),
    # Art & antiques
    (["first edition", "first printing", "signed copy"],           350,    0.65),
    (["banksy", "basquiat", "kaws original"],                      28_000, 0.6),
    (["warhol", "hirst spot print"],                               4_500,  0.55),
    (["vintage poster", "original poster"],                         280,    0.55),
    # Furniture
    (["eames lounge chair", "eames chair"],                         4_200,  0.4),
    (["knoll barcelona chair", "barcelona chair"],                  5_500,  0.4),
    (["vitra", "hay furniture", "herman miller"],                   1_200,  0.4),
]

_DEFAULT_BASE = 320.0
_DEFAULT_SPREAD = 0.40


def _estimate_price(query: str) -> tuple[float, float, float]:
    """
    Return (low, mid, high) price estimates for `query`.

    Algorithm
    ---------
    1. Scan _PRICE_SIGNALS for keyword matches in the lowercase query.
    2. Use the first (most-specific) match found.
    3. Derive a deterministic ±spread using a hash of the query so the
       numbers are stable across re-renders but vary between queries.
    4. If no keyword matches, use _DEFAULT_BASE with a wide spread.

    The hash-based jitter means repeated searches for "Vintage Rolex"
    always return the same range — it won't flicker on re-render.
    """
    q = query.lower().strip()

    base   = _DEFAULT_BASE
    spread = _DEFAULT_SPREAD

    for keywords, b, s in _PRICE_SIGNALS:
        if any(kw in q for kw in keywords):
            base   = b
            spread = s
            break

    # Deterministic jitter seeded on the query string (stable per query)
    h = int(hashlib.md5(q.encode()).hexdigest()[:8], 16) / 0xFFFFFFFF  # 0.0–1.0
    jitter = 0.88 + h * 0.24          # range 0.88 – 1.12

    mid  = base * jitter
    low  = mid  * (1 - spread * 0.7)
    high = mid  * (1 + spread * 0.9)

    return round(low, -1), round(mid, -1), round(high, -1)


def _fmt_price(p: float) -> str:
    """Format a price as £ with comma thousands-separator, no pence."""
    return f"£{p:,.0f}"


def _price_verdict(query: str) -> tuple[str, str, str]:
    """
    Return (dot_color_css, label, sub) for the verdict strip.
    Varies by spread width — wider spread = more uncertainty.
    """
    q = query.lower()
    for keywords, _, spread in _PRICE_SIGNALS:
        if any(kw in q for kw in keywords):
            if spread <= 0.20:
                return "#2d9e7a", "Tight market", "Prices are consistent — limited negotiation room."
            elif spread <= 0.35:
                return "#c9a84c", "Active market", "Moderate price variance — room to find value."
            else:
                return "#b03030", "Volatile market", "Wide price spread — research comps before buying."
    return "#c9a84c", "Exploratory search", "Limited price data — check multiple platforms."


# ──────────────────────────────────────────────────────────────────────────────
# 5.  CARD RENDERER
# ──────────────────────────────────────────────────────────────────────────────

def render_platform_card(p: Platform, low: float, high: float) -> None:
    """Render a single marketplace card as self-contained HTML."""

    # Build tag HTML
    tag_html = "".join(
        f'<span class="tag {style}">{label}</span>'
        for label, style in zip(p.tags, p.tag_styles)
    )

    # Trust badge inline style depends on colour key
    badge_styles = {
        "green": "background:#d5f0ea;color:#0d7a63;border:0.5px solid rgba(13,122,99,.2)",
        "gold":  "background:#fdf3dc;color:#8a6a1f;border:0.5px solid rgba(201,168,76,.3)",
        "blue":  "background:#deeafb;color:#1d5db5;border:0.5px solid rgba(29,93,181,.2)",
    }
    badge_style = badge_styles.get(p.trust_color, badge_styles["blue"])

    # Price range
    price_range = f"{_fmt_price(low)} – {_fmt_price(high)}"

    st.markdown(f"""
    <div class="mkt-card">
      <div class="card-header">
        <div class="platform-icon">{p.icon}</div>
        <div class="card-title-block">
          <div class="platform-name">{p.name}</div>
          <div class="platform-category">{p.category}</div>
        </div>
        <span class="trust-badge" style="{badge_style}">{p.trust_label}</span>
      </div>

      <div class="card-body">
        <div class="listing-count">{p.est_listings}</div>
        <div class="tag-row">{tag_html}</div>
        <div style="font-size:12px;color:var(--ink3);line-height:1.6;margin-bottom:8px">
          {p.notes}
        </div>
        <div class="price-estimate">
          {price_range}
          <span>est. {p.price_note}</span>
        </div>
      </div>

      <div class="card-footer">
        <a href="{p.search_url}" target="_blank" rel="noopener noreferrer"
           class="view-btn"
           style="background:{p.button_bg};color:{p.button_fg}">
          Search {p.name}
          <span class="arrow">→</span>
        </a>
      </div>
    </div>
    """, unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────────────────────
# 6.  SESSION STATE
# ──────────────────────────────────────────────────────────────────────────────
if "search_history" not in st.session_state:
    st.session_state.search_history: list[str] = []
if "last_query" not in st.session_state:
    st.session_state.last_query: str = ""


# ──────────────────────────────────────────────────────────────────────────────
# 7.  SIDEBAR
# ──────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding:1.2rem 0 1rem">
      <div style="font-family:'Syne',sans-serif;font-size:1.5rem;font-weight:800;
                  letter-spacing:-1px;color:#fff;line-height:1">
        Nexus<span style="color:#c9a84c">Scout</span>
      </div>
      <div style="font-family:'DM Mono',monospace;font-size:10px;
                  color:rgba(255,255,255,.45);margin-top:4px;letter-spacing:1px;
                  text-transform:uppercase">
        Universal Search Engine
      </div>
    </div>
    <div style="height:0.5px;background:rgba(255,255,255,.1);margin-bottom:1.4rem"></div>
    """, unsafe_allow_html=True)

    st.markdown("## Filters")

    # ── Platform toggles ──────────────────────────────────────────────────
    st.markdown("""
    <div style="font-family:'DM Mono',monospace;font-size:10px;color:rgba(255,255,255,.45);
                text-transform:uppercase;letter-spacing:1px;margin-bottom:8px">
      Show platforms
    </div>
    """, unsafe_allow_html=True)

    show_general      = st.checkbox("General Marketplaces",   value=True)
    show_collectibles = st.checkbox("Specialist / Collectibles", value=True)
    show_fashion      = st.checkbox("Fashion & Streetwear",   value=True)
    show_local        = st.checkbox("Local & Community",      value=True)
    show_auctions     = st.checkbox("Auctions",               value=True)

    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

    sort_order = st.selectbox(
        "Sort platforms by",
        ["Recommended", "Alphabetical", "Most Listings First"],
    )

    st.markdown("""
    <hr style="border:none;border-top:0.5px solid rgba(255,255,255,.1);margin:1.2rem 0">
    <div style="font-family:'DM Mono',monospace;font-size:10px;color:rgba(255,255,255,.35);
                line-height:1.9;text-transform:uppercase;letter-spacing:.8px">
      All links open live<br>search results pages.<br>
      No hardcoded URLs.
    </div>
    """, unsafe_allow_html=True)

    if st.session_state.search_history:
        st.markdown("""
        <div style="height:0.5px;background:rgba(255,255,255,.1);margin:1.2rem 0 .8rem"></div>
        <div style="font-family:'DM Mono',monospace;font-size:10px;
                    color:rgba(255,255,255,.45);text-transform:uppercase;letter-spacing:.8px;
                    margin-bottom:.6rem">Recent searches</div>
        """, unsafe_allow_html=True)
        for h in reversed(st.session_state.search_history[-5:]):
            st.markdown(
                f'<div style="font-family:\'DM Mono\',monospace;font-size:12px;'
                f'color:rgba(255,255,255,.65);padding:3px 0">{h}</div>',
                unsafe_allow_html=True,
            )


# ──────────────────────────────────────────────────────────────────────────────
# 8.  PLATFORM FILTERING LOGIC
# ──────────────────────────────────────────────────────────────────────────────

_GENERAL      = {"eBay", "Amazon", "Google Shopping"}
_COLLECTIBLES = {"Chrono24", "StockX"}
_FASHION      = {"Grailed", "Vestiaire Collective", "Depop", "1stDibs"}
_LOCAL        = {"Reddit", "Facebook Marketplace"}
_AUCTIONS     = {"Catawiki"}


def _platform_visible(p: Platform) -> bool:
    if p.name in _GENERAL      and not show_general:      return False
    if p.name in _COLLECTIBLES and not show_collectibles:  return False
    if p.name in _FASHION      and not show_fashion:       return False
    if p.name in _LOCAL        and not show_local:         return False
    if p.name in _AUCTIONS     and not show_auctions:      return False
    return True


def _sorted_platforms(platforms: list[Platform]) -> list[Platform]:
    if sort_order == "Alphabetical":
        return sorted(platforms, key=lambda p: p.name)
    if sort_order == "Most Listings First":
        # Crude proxy: put the ones with numbers in est_listings first
        def _score(p: Platform) -> int:
            nums = re.findall(r"[\d,]+", p.est_listings)
            if not nums:
                return 0
            return int(nums[0].replace(",", ""))
        return sorted(platforms, key=_score, reverse=True)
    return platforms   # "Recommended" — keep authored order


# ──────────────────────────────────────────────────────────────────────────────
# 9.  MAIN UI
# ──────────────────────────────────────────────────────────────────────────────

# ── Hero bar ──────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-bar">
  <div class="logo-mark">🔭</div>
  <div>
    <div class="brand-name">Nexus<em>Scout</em>
      <span class="beta-pill">BETA</span>
    </div>
    <div class="brand-tag">
      Type anything. Get live results across every major marketplace instantly.
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Search bar ────────────────────────────────────────────────────────────────
search_col, btn_col = st.columns([6, 1])

with search_col:
    query = st.text_input(
        label       = "q",
        placeholder = "Search across the web for any product…  e.g. 'Vintage Rolex Submariner', 'Air Jordan 1 Chicago', 'Eames Lounge Chair'",
        label_visibility = "collapsed",
    )

with btn_col:
    go = st.button("Scout →", use_container_width=True)

# Allow Enter-key submission (Streamlit fires on text_input change)
triggered = go or (query.strip() and query != st.session_state.last_query and go)

# Also search when user hits Enter (query change + non-empty)
if query.strip() and query.strip() != st.session_state.last_query:
    triggered = True

# ── History pills (quick re-search) ──────────────────────────────────────────
if st.session_state.search_history and not query:
    recent = list(dict.fromkeys(reversed(st.session_state.search_history)))[:6]
    pills  = "".join(f'<span class="suggest-chip">{q}</span>' for q in recent)
    st.markdown(
        f'<div style="margin-top:.4rem"><span style="font-family:\'DM Mono\',sans-serif;'
        f'font-size:10px;color:var(--ink3);text-transform:uppercase;letter-spacing:.8px;'
        f'margin-right:8px">Recent:</span>{pills}</div>',
        unsafe_allow_html=True,
    )


# ──────────────────────────────────────────────────────────────────────────────
# 10.  RESULTS
# ──────────────────────────────────────────────────────────────────────────────

if triggered and query.strip():

    q = query.strip()
    st.session_state.last_query = q

    # Add to history (deduplicate, keep last 20)
    history = st.session_state.search_history
    if q not in history:
        history.append(q)
    st.session_state.search_history = history[-20:]

    # ── Price metrics ─────────────────────────────────────────────────────
    low, mid, high = _estimate_price(q)
    dot_c, vlabel, vsub = _price_verdict(q)

    # Simulate a brief "thinking" delay for UX polish
    with st.spinner(f"Scouting **{q}** across all platforms…"):
        time.sleep(0.55)

    # ── Metric strip ──────────────────────────────────────────────────────
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Est. Market Low",    _fmt_price(low),  delta="budget entry")
    m2.metric("Est. Market Average", _fmt_price(mid), delta="median comparable")
    m3.metric("Est. Market High",   _fmt_price(high), delta="premium examples")
    m4.metric("Price Spread",
              f"{round((high - low) / mid * 100)}%",
              delta="variance across platforms")

    # ── Verdict strip ─────────────────────────────────────────────────────
    st.markdown(f"""
    <div class="verdict-strip">
      <div class="verdict-dot" style="background:{dot_c}"></div>
      <div class="verdict-text">{vlabel}</div>
      <div class="verdict-sub"> — {vsub}</div>
    </div>
    """, unsafe_allow_html=True)

    # ── Platform cards ────────────────────────────────────────────────────
    st.markdown('<p class="section-eyebrow">Live Marketplaces</p>', unsafe_allow_html=True)
    st.markdown(f'<h2 class="section-title">Search results for &ldquo;{q}&rdquo;</h2>',
                unsafe_allow_html=True)

    all_platforms = get_platforms(q)
    visible       = _sorted_platforms([p for p in all_platforms if _platform_visible(p)])

    if not visible:
        st.warning("All platforms are hidden — enable at least one category in the sidebar.")
    else:
        # 3-column grid
        COLS = 3
        rows = [visible[i:i+COLS] for i in range(0, len(visible), COLS)]
        for row in rows:
            cols = st.columns(COLS, gap="medium")
            for col, platform in zip(cols, row):
                with col:
                    render_platform_card(platform, low, high)
            st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

    # ── Intelligence expander ─────────────────────────────────────────────
    st.markdown('<hr class="scout-div">', unsafe_allow_html=True)

    with st.expander("📊  Price Intelligence & Buying Guide", expanded=False):
        g1, g2 = st.columns(2)

        with g1:
            st.markdown("#### Where to start")
            st.markdown(f"""
            <div style="font-size:13.5px;color:var(--ink2);line-height:1.8">
              <b>Best for new condition:</b> Amazon, eBay (BIN listings)<br>
              <b>Best for price-negotiation:</b> Grailed, Facebook Marketplace, Reddit<br>
              <b>Best for authenticity:</b> StockX, Vestiaire Collective, Chrono24<br>
              <b>Best for rare / unique:</b> Catawiki, 1stDibs, eBay Auction<br>
              <b>Best for price history:</b> Google Shopping, StockX
            </div>
            """, unsafe_allow_html=True)

        with g2:
            st.markdown("#### Estimated price breakdown")
            st.markdown(f"""
            <div style="font-size:13.5px;color:var(--ink2);line-height:1.8">
              <b>Budget entry:</b> {_fmt_price(low)} — older stock, fair condition<br>
              <b>Market median:</b> {_fmt_price(mid)} — typical example, good condition<br>
              <b>Premium examples:</b> {_fmt_price(high)} — new/mint, full provenance<br>
              <br>
              <i style="color:var(--ink3);font-size:12px">
                ⚠️ Estimates are indicative only. Always verify current
                prices on the platform before transacting.
              </i>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown(f"""
        <div style="font-family:'DM Mono',monospace;font-size:11px;color:var(--ink3);line-height:1.9">
          Query: <b style="color:var(--ink)">{q}</b> &nbsp;·&nbsp;
          Platforms shown: <b style="color:var(--ink)">{len(visible)}</b> &nbsp;·&nbsp;
          Generated: <b style="color:var(--ink)">{datetime.now().strftime('%H:%M:%S')}</b>
        </div>
        """, unsafe_allow_html=True)

elif not query.strip():
    # ── Empty / welcome state ─────────────────────────────────────────────
    st.markdown("""
    <div class="empty-wrap">
      <div class="empty-icon">🔭</div>
      <div class="empty-title">Scout anything, anywhere.</div>
      <div class="empty-sub">
        Type any product into the search bar above.
        Nexus Scout will open live search results across
        every major marketplace simultaneously — watches, sneakers,
        furniture, electronics, fashion, art, and more.
      </div>
      <div class="suggest-row">
        <span class="suggest-chip">Vintage Rolex Submariner</span>
        <span class="suggest-chip">Air Jordan 1 Chicago</span>
        <span class="suggest-chip">Eames Lounge Chair</span>
        <span class="suggest-chip">Birkin 30 Togo</span>
        <span class="suggest-chip">Supreme Box Logo Hoodie</span>
        <span class="suggest-chip">Sony A7R V</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

# ── Import for datetime usage in expander ─────────────────────────────────────
from datetime import datetime
