# =============================================================================
# NEXUS SCOUT — AI Personal Shopper MVP
# Framework : Streamlit
# File      : nexus_scout.py
# Run with  : streamlit run nexus_scout.py
# =============================================================================

import streamlit as st
import time
import random
from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime, timedelta

# ─────────────────────────────────────────────
# 0.  PAGE CONFIG  (must be first Streamlit call)
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Nexus Scout",
    page_icon="🔭",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# 1.  GLOBAL STYLES
# ─────────────────────────────────────────────
st.markdown("""
<style>
/* ── Fonts ── */
@import url('https://fonts.googleapis.com/css2?family=Fraunces:ital,wght@0,600;0,800;1,600&family=DM+Sans:wght@300;400;500&family=DM+Mono:wght@400;500&display=swap');

/* ── Root tokens ── */
:root {
    --ink:      #0e0d0b;
    --ink2:     #3a3830;
    --ink3:     #6b6860;
    --surface:  #faf9f6;
    --surface2: #f3f1ec;
    --surface3: #eae8e1;
    --gold:     #b8860b;
    --gold-l:   #f5e6c0;
    --gold-d:   #7a5800;
    --teal:     #0f6e56;
    --teal-l:   #d8f0e9;
    --coral:    #9b3a21;
    --coral-l:  #fceae6;
    --blue:     #1a5fa5;
    --blue-l:   #e0edfa;
    --red:      #a32d2d;
    --red-l:    #fde8e8;
    --green:    #2d6a4f;
    --green-l:  #d8f3e8;
    --border:   rgba(14,13,11,.10);
    --border-s: rgba(14,13,11,.22);
    --radius:   10px;
    --radius-l: 16px;
    --mono:     'DM Mono', monospace;
    --serif:    'Fraunces', serif;
    --sans:     'DM Sans', sans-serif;
}

/* ── Global reset ── */
html, body, [class*="css"] { font-family: var(--sans) !important; }

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 1.5rem !important; max-width: 1180px; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: var(--surface2) !important;
    border-right: 0.5px solid var(--border-s) !important;
}
[data-testid="stSidebar"] .stMarkdown h2 {
    font-family: var(--serif) !important;
    font-size: 1.4rem !important;
    font-weight: 800 !important;
    letter-spacing: -0.5px;
    color: var(--ink) !important;
}

/* ── Number input, text input ── */
input[type="number"], input[type="text"] {
    border: 0.5px solid var(--border-s) !important;
    border-radius: var(--radius) !important;
    background: var(--surface) !important;
    font-family: var(--mono) !important;
}
input[type="number"]:focus, input[type="text"]:focus {
    border-color: var(--gold) !important;
    box-shadow: 0 0 0 3px rgba(184,134,11,.12) !important;
}

/* ── Buttons ── */
.stButton > button {
    font-family: var(--sans) !important;
    font-weight: 500 !important;
    font-size: 13px !important;
    border-radius: 100px !important;
    border: 0.5px solid var(--border-s) !important;
    background: var(--surface) !important;
    color: var(--ink) !important;
    transition: all .18s ease !important;
    padding: 0.35rem 1.1rem !important;
}
.stButton > button:hover {
    background: var(--surface3) !important;
    border-color: var(--border-s) !important;
    transform: translateY(-1px);
}
.stButton > button:active { transform: scale(0.97) !important; }

/* ── Listing card ── */
.scout-card {
    background: var(--surface);
    border: 0.5px solid var(--border-s);
    border-radius: var(--radius-l);
    overflow: hidden;
    transition: box-shadow .2s, transform .2s;
    height: 100%;
    display: flex;
    flex-direction: column;
}
.scout-card:hover {
    box-shadow: 0 6px 24px rgba(14,13,11,.09);
    transform: translateY(-2px);
}
.card-image-wrap {
    position: relative;
    aspect-ratio: 4/3;
    overflow: hidden;
    background: var(--surface2);
}
.card-image-wrap img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    display: block;
    transition: transform .35s ease;
}
.scout-card:hover .card-image-wrap img { transform: scale(1.04); }
.source-badge {
    position: absolute;
    top: 10px; left: 10px;
    font-family: var(--mono);
    font-size: 10px; font-weight: 500;
    padding: 3px 9px;
    border-radius: 100px;
    backdrop-filter: blur(8px);
    letter-spacing: 0.5px;
}
.source-ebay      { background: rgba(255,255,255,.88); color: #2c2c2c; border: 0.5px solid rgba(0,0,0,.12); }
.source-chrono24  { background: rgba(15,110,86,.85);   color: #fff; }
.source-grailed   { background: rgba(220,38,38,.82);   color: #fff; }
.source-stockx    { background: rgba(26,95,165,.85);   color: #fff; }
.freshness-badge {
    position: absolute;
    top: 10px; right: 10px;
    font-family: var(--mono);
    font-size: 10px; font-weight: 500;
    padding: 3px 8px;
    border-radius: 100px;
    background: rgba(15,110,86,.85);
    color: #fff;
}
.card-body {
    padding: 1rem 1.1rem;
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 6px;
}
.card-title {
    font-family: var(--sans);
    font-size: 13.5px;
    font-weight: 500;
    color: var(--ink);
    line-height: 1.4;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
}
.card-price {
    font-family: var(--mono);
    font-size: 18px;
    font-weight: 500;
    color: var(--ink);
    letter-spacing: -0.5px;
}
.card-meta {
    font-size: 11.5px;
    color: var(--ink3);
    display: flex;
    gap: 12px;
    flex-wrap: wrap;
}
.card-meta span { display: flex; align-items: center; gap: 4px; }

/* ── AI Analysis badge ── */
.ai-verdict {
    padding: 8px 12px;
    border-radius: var(--radius);
    margin-top: 8px;
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 12.5px;
    font-weight: 500;
}
.verdict-great  { background: var(--green-l); color: var(--green); border: 0.5px solid rgba(45,106,79,.2); }
.verdict-good   { background: var(--teal-l);  color: var(--teal);  border: 0.5px solid rgba(15,110,86,.2); }
.verdict-fair   { background: var(--gold-l);  color: var(--gold-d); border: 0.5px solid rgba(184,134,11,.25); }
.verdict-high   { background: var(--coral-l); color: var(--coral); border: 0.5px solid rgba(155,58,33,.2); }

/* ── View listing button ── */
.view-btn {
    display: block;
    text-align: center;
    padding: 9px 0;
    border-radius: 100px;
    font-size: 13px;
    font-weight: 500;
    text-decoration: none !important;
    background: var(--ink);
    color: #fff !important;
    margin-top: auto;
    transition: background .2s, transform .15s;
    border: none;
    cursor: pointer;
}
.view-btn:hover { background: var(--ink2); transform: translateY(-1px); }

/* ── Seller stars ── */
.seller-stars { color: var(--gold); font-size: 11px; }

/* ── Section header ── */
.section-header {
    display: flex;
    align-items: baseline;
    gap: 12px;
    margin-bottom: 1rem;
}
.section-header h3 {
    font-family: var(--serif) !important;
    font-size: 1.45rem !important;
    font-weight: 700 !important;
    letter-spacing: -0.5px;
    color: var(--ink) !important;
    margin: 0 !important;
}
.result-count {
    font-family: var(--mono);
    font-size: 11px;
    color: var(--ink3);
    background: var(--surface2);
    padding: 3px 9px;
    border-radius: 100px;
    border: 0.5px solid var(--border-s);
}

/* ── Stat pill strip ── */
.stat-strip {
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
    margin-bottom: 1.5rem;
}
.stat-pill {
    font-family: var(--mono);
    font-size: 11.5px;
    padding: 5px 12px;
    border-radius: 100px;
    background: var(--surface2);
    border: 0.5px solid var(--border-s);
    color: var(--ink2);
}
.stat-pill b { color: var(--ink); font-weight: 500; }

/* ── Source filter pills ── */
.filter-row { display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 1rem; }
.filter-pill {
    font-family: var(--mono);
    font-size: 11px; font-weight: 500;
    padding: 4px 12px;
    border-radius: 100px;
    cursor: pointer;
    border: 0.5px solid var(--border-s);
    background: var(--surface2);
    color: var(--ink2);
}
.filter-pill.active {
    background: var(--ink);
    color: #fff;
    border-color: var(--ink);
}

/* ── Hero brand bar ── */
.brand-bar {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 1.8rem;
    padding-bottom: 1.2rem;
    border-bottom: 0.5px solid var(--border);
}
.brand-name {
    font-family: var(--serif);
    font-size: 1.7rem;
    font-weight: 800;
    letter-spacing: -1px;
    color: var(--ink);
}
.brand-name span { color: var(--gold); }
.brand-tagline {
    font-size: 12.5px;
    color: var(--ink3);
    font-style: italic;
}
.brand-dot {
    width: 6px; height: 6px;
    border-radius: 50%;
    background: var(--gold);
}

/* ── Divider ── */
.divider { height: 0.5px; background: var(--border); margin: 1.2rem 0; }

/* ── Empty state ── */
.empty-state {
    text-align: center;
    padding: 4rem 2rem;
    color: var(--ink3);
}
.empty-state .icon { font-size: 3rem; margin-bottom: 1rem; }
.empty-state h4 {
    font-family: var(--serif) !important;
    font-size: 1.4rem !important;
    font-weight: 600 !important;
    color: var(--ink2) !important;
    margin-bottom: .5rem !important;
}
.empty-state p { font-size: 14px; }

/* ── Spinner override ── */
.stSpinner > div { border-top-color: var(--gold) !important; }

/* ── Selectbox ── */
[data-testid="stSelectbox"] > div > div {
    border: 0.5px solid var(--border-s) !important;
    border-radius: var(--radius) !important;
    background: var(--surface) !important;
}

/* ── Slider ── */
[data-testid="stSlider"] [data-baseweb="slider"] div[role="slider"] {
    background-color: var(--gold) !important;
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# 2.  DATA MODEL
# ─────────────────────────────────────────────

@dataclass
class Listing:
    """
    Normalised listing shape.
    Add / remove fields here as real APIs dictate.
    """
    id:             str
    title:          str
    price:          float
    currency:       str
    source:         str          # 'eBay' | 'Chrono24' | 'Grailed' | 'StockX'
    condition:      str          # 'New' | 'Excellent' | 'Good' | 'Fair' | 'Parts'
    seller_name:    str
    seller_rating:  float        # 0.0 – 5.0
    image_url:      str
    listing_url:    str
    listed_at:      datetime
    location:       str
    box_and_papers: bool = False
    ai_score:       Optional[float] = None   # 0–100, populated by AI engine
    extra:          dict = field(default_factory=dict)  # source-specific extras


# ─────────────────────────────────────────────
# 3.  MOCK SCRAPER LAYER
#     ──────────────────────────────────────────
#     Each function returns List[Listing].
#     To plug in a real API:
#       1. Replace the function body with real HTTP calls.
#       2. Map the API response to the Listing dataclass.
#       3. The rest of the app stays identical.
# ─────────────────────────────────────────────

# ── Shared image pool (Unsplash, free-to-use) ──
_WATCH_IMAGES = [
    "https://images.unsplash.com/photo-1523170335258-f5ed11844a49?w=600&q=80",
    "https://images.unsplash.com/photo-1587836374828-4dbafa94cf0e?w=600&q=80",
    "https://images.unsplash.com/photo-1548171915-f06caba21e29?w=600&q=80",
    "https://images.unsplash.com/photo-1491553895911-0055eca6402d?w=600&q=80",
    "https://images.unsplash.com/photo-1620625515032-6ed0c1790c75?w=600&q=80",
    "https://images.unsplash.com/photo-1612817288484-6f916006741a?w=600&q=80",
]
_SNEAKER_IMAGES = [
    "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=600&q=80",
    "https://images.unsplash.com/photo-1608231387042-66d1773070a5?w=600&q=80",
    "https://images.unsplash.com/photo-1556906781-9a412961a28c?w=600&q=80",
    "https://images.unsplash.com/photo-1600185365926-3a2ce3cdb9eb?w=600&q=80",
]
_GENERIC_IMAGES = [
    "https://images.unsplash.com/photo-1583394838336-acd977736f90?w=600&q=80",
    "https://images.unsplash.com/photo-1526170375885-4d8ecf77b99f?w=600&q=80",
]


def _pick_images(query: str) -> list[str]:
    q = query.lower()
    if any(k in q for k in ("rolex", "omega", "patek", "watch", "chrono")):
        return _WATCH_IMAGES
    if any(k in q for k in ("jordan", "nike", "yeezy", "sneaker", "shoe")):
        return _SNEAKER_IMAGES
    return _GENERIC_IMAGES


def _make_id(source: str, n: int) -> str:
    return f"{source.lower()[:3]}-{random.randint(100000, 999999)}-{n}"


def _relative_time(dt: datetime) -> str:
    delta = datetime.now() - dt
    if delta.seconds < 3600:
        return f"{delta.seconds // 60}m ago"
    if delta.days == 0:
        return f"{delta.seconds // 3600}h ago"
    return f"{delta.days}d ago"


# ── eBay mock ─────────────────────────────────────────────────────────────────
# FUTURE INTEGRATION: eBay Browse API
#   endpoint : GET https://api.ebay.com/buy/browse/v1/item_summary/search
#   params   : q=<query>, limit=20, filter=conditionIds:{1000|3000}
#   auth     : OAuth 2.0 client-credentials
#   docs     : https://developer.ebay.com/api-docs/buy/browse/overview.html

def scrape_ebay(query: str, max_results: int = 6) -> list[Listing]:
    """
    Mock eBay scraper. Returns realistic dummy listings.
    Replace the body with a real eBay Browse API call to go live.
    """
    images = _pick_images(query)
    base_price = _infer_base_price(query)
    conditions = ["Excellent", "Good", "Good", "Fair", "Excellent", "New"]
    locations = ["London, UK", "Manchester, UK", "New York, US", "Berlin, DE", "Tokyo, JP", "Paris, FR"]

    listings = []
    for i in range(max_results):
        # Realistic price variance: ±30% around base
        price = round(base_price * random.uniform(0.70, 1.30), 2)
        age_hours = random.randint(1, 168)
        listings.append(Listing(
            id            = _make_id("ebay", i),
            title         = _generate_title(query, "eBay", i),
            price         = price,
            currency      = "GBP",
            source        = "eBay",
            condition     = conditions[i % len(conditions)],
            seller_name   = f"seller_{random.randint(1000, 9999)}",
            seller_rating = round(random.uniform(4.2, 5.0), 1),
            image_url     = images[i % len(images)],
            listing_url   = f"https://www.ebay.co.uk/itm/{random.randint(100000000000, 999999999999)}",
            listed_at     = datetime.now() - timedelta(hours=age_hours),
            location      = locations[i % len(locations)],
            box_and_papers= random.random() > 0.55,
            extra         = {"bids": random.randint(0, 12), "watchers": random.randint(3, 40)},
        ))
    return listings


# ── Chrono24 mock ─────────────────────────────────────────────────────────────
# FUTURE INTEGRATION: Chrono24 Partner API
#   endpoint : GET https://api.chrono24.com/api/v1/listings
#   params   : query=<query>, currency=GBP, limit=20
#   auth     : API key header  X-ApiKey: <key>
#   docs     : https://api.chrono24.com/docs  (partner programme required)

def scrape_chrono24(query: str, max_results: int = 6) -> list[Listing]:
    """
    Mock Chrono24 scraper. Returns realistic dummy listings.
    Replace the body with a real Chrono24 Partner API call to go live.
    """
    images = _pick_images(query)
    base_price = _infer_base_price(query)
    # Chrono24 skews slightly higher (dealer market)
    conditions = ["New", "Excellent", "Excellent", "Good", "New", "Excellent"]
    dealers = ["Crown Watches", "The Watch Gallery", "Swiss Time", "LuxTime GmbH", "Elite Horology"]

    listings = []
    for i in range(max_results):
        price = round(base_price * random.uniform(0.85, 1.45), 2)
        age_days = random.randint(0, 30)
        listings.append(Listing(
            id            = _make_id("c24", i),
            title         = _generate_title(query, "Chrono24", i),
            price         = price,
            currency      = "GBP",
            source        = "Chrono24",
            condition     = conditions[i % len(conditions)],
            seller_name   = dealers[i % len(dealers)],
            seller_rating = round(random.uniform(4.5, 5.0), 1),
            image_url     = images[(i + 2) % len(images)],
            listing_url   = f"https://www.chrono24.com/search/detail.htm?id={random.randint(1000000, 9999999)}",
            listed_at     = datetime.now() - timedelta(days=age_days),
            location      = random.choice(["Zurich, CH", "London, UK", "Geneva, CH", "Munich, DE"]),
            box_and_papers= random.random() > 0.35,
            extra         = {"certified": random.random() > 0.6, "return_policy": "14 days"},
        ))
    return listings


# ── Helper: infer a plausible base price from the query string ──────────────

def _infer_base_price(query: str) -> float:
    q = query.lower()
    price_map = {
        "rolex":     9500,
        "patek":     25000,
        "omega":     3800,
        "ap ":       18000,
        "audemars":  18000,
        "jordan 1":  280,
        "jordan 4":  350,
        "yeezy":     220,
        "air force": 120,
        "dunk":      180,
        "chanel":    3200,
        "hermes":    6800,
        "louis vuitton": 1200,
        "supreme":   420,
    }
    for keyword, price in price_map.items():
        if keyword in q:
            return float(price)
    return 800.0   # sensible default


# ── Helper: generate realistic listing titles ────────────────────────────────

def _generate_title(query: str, source: str, idx: int) -> str:
    conditions = ["Excellent", "Good", "Near Mint", "Pre-owned", "Unworn"]
    qualifiers = [
        f"({conditions[idx % len(conditions)]})",
        "— Box & Papers",
        "Full Set",
        "Serviced",
        "Collector's Edition",
        "",
    ]
    years = ["2019", "2020", "2021", "2022", "2023"]
    refs = {
        "ebay":     ["116610LN", "326934", "5711", "15400ST", "311.30.42"],
        "chrono24": ["Ref. 116500LN", "Ref. 210.30", "Ref. 5726A", "Cal. 3135", "Ref. M116610"],
    }.get(source.lower(), [""])
    ref = refs[idx % len(refs)]
    year = years[idx % len(years)]
    qual = qualifiers[idx % len(qualifiers)]
    return f"{query} {ref} {year} {qual}".strip()


# ─────────────────────────────────────────────
# 4.  AGGREGATOR
#     Runs all scrapers in parallel (ThreadPool)
#     and deduplicates by URL hash.
# ─────────────────────────────────────────────

from concurrent.futures import ThreadPoolExecutor, as_completed


def aggregate_search(
    query: str,
    sources: list[str],
    max_per_source: int = 6,
) -> list[Listing]:
    """
    Fan-out search controller.
    Add new scraper functions to `scraper_map` to expand sources.
    """
    scraper_map = {
        "eBay":     scrape_ebay,
        "Chrono24": scrape_chrono24,
        # "Grailed":  scrape_grailed,   # ← add Phase 2 scrapers here
        # "StockX":   scrape_stockx,
    }

    results: list[Listing] = []
    seen_urls: set[str] = set()

    active_scrapers = {k: v for k, v in scraper_map.items() if k in sources}

    with ThreadPoolExecutor(max_workers=len(active_scrapers)) as pool:
        futures = {
            pool.submit(fn, query, max_per_source): source
            for source, fn in active_scrapers.items()
        }
        for future in as_completed(futures):
            try:
                for listing in future.result():
                    if listing.listing_url not in seen_urls:
                        seen_urls.add(listing.listing_url)
                        results.append(listing)
            except Exception as e:
                st.warning(f"Source error: {e}")

    return results


# ─────────────────────────────────────────────
# 5.  AI ANALYSIS ENGINE  (mock — Claude-ready)
#     ──────────────────────────────────────────
#     To connect Claude:
#       pip install anthropic
#       Replace analyse_listing() body with an
#       anthropic.messages.create() call using the
#       prompt template below.
# ─────────────────────────────────────────────

@dataclass
class AIVerdict:
    label:      str    # 'Great Deal' | 'Good Value' | 'Fair Price' | 'Overpriced'
    css_class:  str    # maps to CSS .verdict-* class
    emoji:      str
    diff_pct:   float  # % above/below target
    reasoning:  str


def analyse_listing(listing: Listing, target_price: float) -> AIVerdict:
    """
    Price intelligence analysis.

    FUTURE CLAUDE INTEGRATION — replace this function body:
    ─────────────────────────────────────────────────────────
    import anthropic
    client = anthropic.Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])

    prompt = f\"\"\"
    You are a luxury collectibles pricing expert.
    Analyse this listing and return ONLY valid JSON.

    Listing : {listing.title}
    Source  : {listing.source}
    Price   : £{listing.price:,.0f}
    Target  : £{target_price:,.0f}
    Condition: {listing.condition}
    B&P     : {listing.box_and_papers}
    Seller  : {listing.seller_rating}/5.0

    Output: {{
        "verdict": "great_deal"|"good_value"|"fair_price"|"overpriced",
        "confidence": 0.0-1.0,
        "reasoning": "<25 words>",
        "suggested_offer": <number>
    }}
    \"\"\"

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=300,
        messages=[{"role": "user", "content": prompt}]
    )
    data = json.loads(response.content[0].text)
    # … map data to AIVerdict …
    ─────────────────────────────────────────────────────────
    """
    diff_pct = ((listing.price - target_price) / target_price) * 100

    # Adjust thresholds for condition
    condition_adjustment = {
        "New":       -5,   # new items can command a small premium
        "Excellent": -2,
        "Good":       5,   # expect a slight discount for 'good'
        "Fair":      15,
        "Parts":     40,
    }.get(listing.condition, 0)

    adjusted_diff = diff_pct + condition_adjustment

    # Box & papers bonus
    if listing.box_and_papers and adjusted_diff < 10:
        adjusted_diff -= 5

    if adjusted_diff <= -12:
        return AIVerdict(
            label      = "Great Deal",
            css_class  = "verdict-great",
            emoji      = "🟢",
            diff_pct   = diff_pct,
            reasoning  = (
                f"Listed {abs(diff_pct):.0f}% below your target. "
                f"Exceptional value for {listing.condition.lower()} condition"
                f"{' with box & papers' if listing.box_and_papers else ''}."
            ),
        )
    elif adjusted_diff <= 0:
        return AIVerdict(
            label      = "Good Value",
            css_class  = "verdict-good",
            emoji      = "🔵",
            diff_pct   = diff_pct,
            reasoning  = (
                f"{abs(diff_pct):.0f}% under your target — solid market price "
                f"from a {listing.seller_rating:.1f}★ seller."
            ),
        )
    elif adjusted_diff <= 18:
        return AIVerdict(
            label      = "Fair Price",
            css_class  = "verdict-fair",
            emoji      = "🟡",
            diff_pct   = diff_pct,
            reasoning  = (
                f"{diff_pct:.0f}% above target. Typical market rate; "
                f"negotiate or wait for a better listing."
            ),
        )
    else:
        return AIVerdict(
            label      = "Overpriced",
            css_class  = "verdict-high",
            emoji      = "🔴",
            diff_pct   = diff_pct,
            reasoning  = (
                f"{diff_pct:.0f}% above your target. "
                f"Skip unless this specific provenance justifies the premium."
            ),
        )


# ─────────────────────────────────────────────
# 6.  UI HELPERS
# ─────────────────────────────────────────────

def _format_price(price: float, currency: str = "GBP") -> str:
    symbol = {"GBP": "£", "USD": "$", "EUR": "€", "CHF": "CHF "}.get(currency, currency + " ")
    return f"{symbol}{price:,.0f}"


def _stars(rating: float) -> str:
    full = int(rating)
    half = 1 if (rating - full) >= 0.5 else 0
    return "★" * full + ("½" if half else "") + "☆" * (5 - full - half)


def render_listing_card(listing: Listing, verdict: AIVerdict):
    """Render a single listing card using HTML + Streamlit fallback button."""

    freshness = _relative_time(listing.listed_at)
    source_cls = f"source-{listing.source.lower().replace(' ', '')}"

    st.markdown(f"""
    <div class="scout-card">
      <div class="card-image-wrap">
        <img src="{listing.image_url}" alt="{listing.title}" loading="lazy"
             onerror="this.src='https://images.unsplash.com/photo-1526170375885-4d8ecf77b99f?w=600&q=80'">
        <span class="source-badge {source_cls}">{listing.source}</span>
        <span class="freshness-badge">{freshness}</span>
      </div>
      <div class="card-body">
        <div class="card-title">{listing.title}</div>
        <div class="card-price">{_format_price(listing.price, listing.currency)}</div>
        <div class="card-meta">
          <span>📦 {listing.condition}</span>
          <span>📍 {listing.location}</span>
          {"<span>📄 B&amp;P</span>" if listing.box_and_papers else ""}
        </div>
        <div class="card-meta">
          <span class="seller-stars">{_stars(listing.seller_rating)}</span>
          <span>{listing.seller_name}</span>
        </div>
        <div class="ai-verdict {verdict.css_class}">
          <span>{verdict.emoji}</span>
          <div>
            <strong>{verdict.label}</strong> &nbsp;·&nbsp;
            <span style="font-weight:400;font-size:11.5px">{verdict.reasoning}</span>
          </div>
        </div>
        <div style="margin-top:10px">
          <a href="{listing.listing_url}" target="_blank" class="view-btn">
            View Listing →
          </a>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)


def render_stats_strip(listings: list[Listing], target_price: float):
    """Summary statistics bar above the results grid."""
    prices = [l.price for l in listings]
    if not prices:
        return
    median  = sorted(prices)[len(prices) // 2]
    lowest  = min(prices)
    highest = max(prices)
    below   = sum(1 for p in prices if p <= target_price)

    st.markdown(f"""
    <div class="stat-strip">
      <div class="stat-pill">🔍 <b>{len(listings)}</b> listings found</div>
      <div class="stat-pill">📉 Lowest: <b>{_format_price(lowest)}</b></div>
      <div class="stat-pill">📊 Median: <b>{_format_price(median)}</b></div>
      <div class="stat-pill">📈 Highest: <b>{_format_price(highest)}</b></div>
      <div class="stat-pill">✅ <b>{below}</b> at or below your target</div>
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# 7.  SIDEBAR CONFIGURATION
# ─────────────────────────────────────────────

with st.sidebar:
    st.markdown("""
    <div style="margin-bottom:1.5rem">
      <div style="font-family:'Fraunces',serif;font-size:1.6rem;font-weight:800;
                  letter-spacing:-1px;color:#0e0d0b;line-height:1">
        Nexus<span style="color:#b8860b">Scout</span>
      </div>
      <div style="font-size:11px;color:#6b6860;font-style:italic;margin-top:2px">
        AI Personal Shopper — MVP v0.1
      </div>
    </div>
    <div style="height:0.5px;background:rgba(14,13,11,.1);margin-bottom:1.5rem"></div>
    """, unsafe_allow_html=True)

    st.markdown("## Search Settings")

    target_price = st.number_input(
        "Your target price (£)",
        min_value   = 10,
        max_value   = 500_000,
        value       = 8_500,
        step        = 100,
        help        = "The AI will benchmark every listing against this price.",
    )

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    sources_selected = st.multiselect(
        "Sources to search",
        options  = ["eBay", "Chrono24"],
        default  = ["eBay", "Chrono24"],
        help     = "More sources coming in Phase 2: Grailed, StockX, Reddit",
    )

    results_per_source = st.slider(
        "Results per source",
        min_value = 2,
        max_value = 12,
        value     = 6,
    )

    sort_by = st.selectbox(
        "Sort results by",
        ["Price: Low to High", "Price: High to Low", "AI Score: Best First", "Newest First"],
    )

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    st.markdown("""
    <div style="height:0.5px;background:rgba(14,13,11,.1);margin:8px 0 16px"></div>
    <div style="font-family:'DM Mono',monospace;font-size:10px;color:#6b6860;
                text-transform:uppercase;letter-spacing:1px;margin-bottom:8px">Filters</div>
    """, unsafe_allow_html=True)

    show_bp_only    = st.checkbox("Box & Papers only",  value=False)
    min_seller      = st.slider("Min seller rating ★",  min_value=1.0, max_value=5.0, value=4.0, step=0.1)
    max_price_filter = st.number_input(
        "Max price (£) — 0 = no limit",
        min_value=0, max_value=500_000, value=0, step=500,
    )

    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
    st.markdown("""
    <div style="font-family:'DM Mono',monospace;font-size:10px;color:#6b6860;line-height:1.7">
      🔌 Real API keys go in<br>
      <code style="background:#eae8e1;padding:1px 4px;border-radius:3px">.streamlit/secrets.toml</code>
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# 8.  MAIN CONTENT
# ─────────────────────────────────────────────

# ── Brand bar ─────────────────────────────────
st.markdown("""
<div class="brand-bar">
  <div class="brand-dot"></div>
  <div>
    <span class="brand-name">Nexus<span>Scout</span></span>
    &nbsp;
    <span class="brand-tagline">AI-powered collectibles search</span>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Search bar ────────────────────────────────
search_col, btn_col = st.columns([5, 1])

with search_col:
    query = st.text_input(
        label       = "Search",
        placeholder = "Try 'Vintage Rolex Submariner', 'Air Jordan 1 Chicago', 'Patek Philippe'…",
        label_visibility = "collapsed",
    )

with btn_col:
    search_clicked = st.button("🔭  Scout", use_container_width=True)

st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# 9.  SEARCH EXECUTION & RESULTS
# ─────────────────────────────────────────────

# Initialise session state
if "listings" not in st.session_state:
    st.session_state.listings = []
if "last_query" not in st.session_state:
    st.session_state.last_query = ""

# Trigger search on button click or Enter
if search_clicked and query.strip():
    if not sources_selected:
        st.warning("Please select at least one source in the sidebar.")
    else:
        with st.spinner(f"Scouting {', '.join(sources_selected)} for **{query}**…"):
            time.sleep(0.8)  # simulate network latency; remove with real APIs
            raw_listings = aggregate_search(
                query           = query,
                sources         = sources_selected,
                max_per_source  = results_per_source,
            )

        # ── Apply sidebar filters ──────────────────────
        filtered = raw_listings

        if show_bp_only:
            filtered = [l for l in filtered if l.box_and_papers]

        filtered = [l for l in filtered if l.seller_rating >= min_seller]

        if max_price_filter > 0:
            filtered = [l for l in filtered if l.price <= max_price_filter]

        # ── Sorting ───────────────────────────────────
        if sort_by == "Price: Low to High":
            filtered.sort(key=lambda l: l.price)
        elif sort_by == "Price: High to Low":
            filtered.sort(key=lambda l: l.price, reverse=True)
        elif sort_by == "Newest First":
            filtered.sort(key=lambda l: l.listed_at, reverse=True)
        elif sort_by == "AI Score: Best First":
            # Sort by proximity to target price (best deal first)
            filtered.sort(key=lambda l: l.price - target_price)

        st.session_state.listings = filtered
        st.session_state.last_query = query


# ── Render results ─────────────────────────────────────────────────────────────

if st.session_state.listings:
    listings = st.session_state.listings

    # Stats strip
    render_stats_strip(listings, target_price)

    # Section header
    st.markdown(f"""
    <div class="section-header">
      <h3>Results for "{st.session_state.last_query}"</h3>
      <span class="result-count">{len(listings)} listings</span>
    </div>
    """, unsafe_allow_html=True)

    # Cards grid — 3 columns
    cols_per_row = 3
    rows = [listings[i:i+cols_per_row] for i in range(0, len(listings), cols_per_row)]

    for row in rows:
        cols = st.columns(cols_per_row, gap="medium")
        for col, listing in zip(cols, row):
            verdict = analyse_listing(listing, target_price)
            with col:
                render_listing_card(listing, verdict)
        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    # ── Insights panel ────────────────────────────────────────────────
    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

    with st.expander("📊  Market Intelligence Report", expanded=False):
        verdicts = [analyse_listing(l, target_price) for l in listings]

        great  = sum(1 for v in verdicts if v.label == "Great Deal")
        good   = sum(1 for v in verdicts if v.label == "Good Value")
        fair   = sum(1 for v in verdicts if v.label == "Fair Price")
        over   = sum(1 for v in verdicts if v.label == "Overpriced")
        bp     = sum(1 for l in listings if l.box_and_papers)
        prices = [l.price for l in listings]
        avg_p  = sum(prices) / len(prices)
        med_p  = sorted(prices)[len(prices) // 2]

        ic1, ic2, ic3, ic4 = st.columns(4)
        ic1.metric("Great Deals", great,  delta=f"of {len(listings)}")
        ic2.metric("Good Value",  good,   delta=f"of {len(listings)}")
        ic3.metric("Fair / High",  fair + over, delta=None)
        ic4.metric("With B&P",    bp,     delta=f"{bp/len(listings)*100:.0f}%")

        st.markdown("---")

        best = min(listings, key=lambda l: l.price)
        st.markdown(f"""
        <div style="font-size:13.5px;color:#3a3830;line-height:1.75">
          <b>Average price</b>: {_format_price(avg_p)} &nbsp;·&nbsp;
          <b>Median price</b>: {_format_price(med_p)} &nbsp;·&nbsp;
          <b>Your target</b>: {_format_price(target_price)}<br>
          <b>Best listing</b>: {best.title} at {_format_price(best.price)} on {best.source}
        </div>
        """, unsafe_allow_html=True)

        if avg_p < target_price * 0.85:
            st.success("✅ The market is currently **below** your target price. Good time to buy.")
        elif avg_p > target_price * 1.15:
            st.warning("⚠️ Market prices are **above** your target. Consider waiting or raising your budget.")
        else:
            st.info("ℹ️ Prices are **in line** with your target. A few negotiable listings are available.")

elif search_clicked and not query.strip():
    st.warning("Enter a product name to start scouting.")

else:
    # ── Empty state ─────────────────────────────────────────────────────
    st.markdown("""
    <div class="empty-state">
      <div class="icon">🔭</div>
      <h4>Ready to Scout</h4>
      <p>Enter a product above — e.g. <em>"Vintage Rolex Submariner"</em>,
         <em>"Air Jordan 1 Bred"</em>, or <em>"Patek Philippe Nautilus"</em> —
         and set your target price in the sidebar.</p>
    </div>
    """, unsafe_allow_html=True)
