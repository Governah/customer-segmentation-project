"""
app.py — SegmentIQ entry point.
Modern banking dashboard with Lucide icons, proper dark/light mode.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st

st.set_page_config(
    page_title="Foryna· Banking Analytics ",
    layout="wide",
    initial_sidebar_state="expanded",
)

if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = True
if "page" not in st.session_state:
    st.session_state.page = "dashboard"


def inject_css(dark: bool) -> None:
    if dark:
        bg          = "#0A0F1E"
        surface     = "#111827"
        surface2    = "#1A2236"
        surface3    = "#243044"
        border      = "#1E293B"
        border2     = "#2D3F5C"
        text        = "#F1F5F9"
        text_muted  = "#64748B"
        text_soft   = "#94A3B8"
        accent      = "#10B981"
        accent_dim  = "rgba(16,185,129,0.12)"
        blue        = "#3B82F6"
        blue_dim    = "rgba(59,130,246,0.12)"
        shadow      = "rgba(0,0,0,0.5)"
        shadow_lg   = "rgba(0,0,0,0.7)"
        nav_hover   = "#1A2236"
        nav_active  = "#1A2236"
        input_bg    = "#1A2236"
    else:
        bg          = "#F8FAFC"
        surface     = "#FFFFFF"
        surface2    = "#F1F5F9"
        surface3    = "#E8EFF7"
        border      = "#E2E8F0"
        border2     = "#CBD5E1"
        text        = "#0F172A"
        text_muted  = "#64748B"
        text_soft   = "#475569"
        accent      = "#059669"
        accent_dim  = "rgba(5,150,105,0.08)"
        blue        = "#2563EB"
        blue_dim    = "rgba(37,99,235,0.08)"
        shadow      = "rgba(15,23,42,0.08)"
        shadow_lg   = "rgba(15,23,42,0.16)"
        nav_hover   = "#F1F5F9"
        nav_active  = "#EEF2FF"
        input_bg    = "#F8FAFC"

    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

    :root {{
        --bg:         {bg};
        --surface:    {surface};
        --surface2:   {surface2};
        --surface3:   {surface3};
        --border:     {border};
        --border2:    {border2};
        --text:       {text};
        --muted:      {text_muted};
        --soft:       {text_soft};
        --accent:     {accent};
        --accent-dim: {accent_dim};
        --blue:       {blue};
        --blue-dim:   {blue_dim};
        --shadow:     {shadow};
        --shadow-lg:  {shadow_lg};
        --nav-hover:  {nav_hover};
        --nav-active: {nav_active};
        --input-bg:   {input_bg};
        --radius:     12px;
        --radius-sm:  8px;
        --radius-xs:  6px;
    }}

    /* ── Reset ── */
    *, *::before, *::after {{ box-sizing: border-box; }}
    html, body, [class*="css"] {{
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
        background-color: var(--bg) !important;
        color: var(--text) !important;
        -webkit-font-smoothing: antialiased;
    }}
    #MainMenu, footer, header {{ visibility: hidden; }}
    .block-container {{
        padding: 2rem 2.5rem 4rem !important;
        max-width: 1380px;
    }}

    /* ── Sidebar ── */
    section[data-testid="stSidebar"] {{
        background: var(--surface) !important;
        border-right: 1px solid var(--border) !important;
        padding: 0 !important;
    }}
    section[data-testid="stSidebar"] > div {{
        padding: 0 !important;
    }}
    section[data-testid="stSidebar"] * {{
        color: var(--text) !important;
    }}

    /* ── Sidebar buttons ── */
section[data-testid="stSidebar"] .stButton > button {{
        background: transparent !important;
        border: none !important;
        border-radius: var(--radius-sm) !important;
        color: var(--muted) !important;
        font-size: 0.9rem !important;
        font-weight: 500 !important;
        text-align: left !important;
        padding: 0.75rem 1rem !important;
        margin-bottom: 10px !important;
        width: 100% !important;
        transition: background 0.15s ease, color 0.15s ease !important;
        box-shadow: none !important;
        justify-content: flex-start !important;
    }}
    section[data-testid="stSidebar"] .stButton > button:hover {{
        background: var(--nav-hover) !important;
        color: var(--text) !important;
    }}

    /* ── KPI cards ── */
    .kpi-card {{
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: var(--radius);
        padding: 1.5rem;
        position: relative;
        overflow: hidden;
        transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
        cursor: default;
    }}
    .kpi-card:hover {{
        transform: translateY(-2px);
        box-shadow: 0 8px 24px var(--shadow-lg);
        border-color: var(--border2);
    }}
    .kpi-icon-wrap {{
        width: 40px; height: 40px;
        border-radius: var(--radius-sm);
        display: flex; align-items: center; justify-content: center;
        margin-bottom: 1rem;
    }}
    .kpi-icon-wrap svg {{ width: 20px; height: 20px; }}
    .kpi-label {{
        font-size: 0.72rem;
        font-weight: 600;
        letter-spacing: 0.07em;
        text-transform: uppercase;
        color: var(--muted);
        margin-bottom: 0.35rem;
    }}
    .kpi-value {{
        font-size: 1.9rem;
        font-weight: 800;
        color: var(--text);
        line-height: 1;
        letter-spacing: -0.02em;
    }}
    .kpi-sub {{
        font-size: 0.76rem;
        color: var(--muted);
        margin-top: 0.4rem;
    }}
    .kpi-bar {{
        position: absolute;
        bottom: 0; left: 0; right: 0;
        height: 3px;
        border-radius: 0 0 var(--radius) var(--radius);
    }}

    /* ── Chart card ── */
    .chart-card {{
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: var(--radius);
        padding: 1.5rem;
        margin-bottom: 1.25rem;
    }}
    .chart-title {{
        font-size: 0.875rem;
        font-weight: 600;
        color: var(--text);
        margin-bottom: 0.25rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }}
    .chart-title svg {{ width:16px; height:16px; color: var(--muted); }}
    .chart-sub {{
        font-size: 0.775rem;
        color: var(--muted);
        margin-bottom: 1rem;
    }}

    /* ── Insight box ── */
    .insight-box {{
        background: var(--accent-dim);
        border: 1px solid rgba(16,185,129,0.2);
        border-radius: var(--radius-sm);
        padding: 0.875rem 1rem;
        margin-top: 1rem;
        font-size: 0.8rem;
        color: var(--soft);
        line-height: 1.7;
        display: flex;
        gap: 0.6rem;
        align-items: flex-start;
    }}
    .insight-box svg {{
        width: 15px; height: 15px;
        color: var(--accent);
        flex-shrink: 0;
        margin-top: 2px;
    }}

    /* ── Page header ── */
    .page-header {{
        margin-bottom: 1.75rem;
    }}
    .page-title {{
        font-size: 1.5rem;
        font-weight: 800;
        color: var(--text);
        letter-spacing: -0.025em;
        line-height: 1.2;
    }}
    .page-sub {{
        font-size: 0.85rem;
        color: var(--muted);
        margin-top: 0.3rem;
    }}

    /* ── Badge ── */
    .badge {{
        display: inline-flex;
        align-items: center;
        gap: 0.35rem;
        padding: 0.2rem 0.65rem;
        border-radius: 999px;
        font-size: 0.7rem;
        font-weight: 600;
        letter-spacing: 0.04em;
    }}
    .badge-green  {{ background:rgba(16,185,129,0.12); color:#10B981; border:1px solid rgba(16,185,129,0.2); }}
    .badge-blue   {{ background:rgba(59,130,246,0.12); color:#3B82F6; border:1px solid rgba(59,130,246,0.2); }}
    .badge-orange {{ background:rgba(249,115,22,0.12); color:#F97316; border:1px solid rgba(249,115,22,0.2); }}
    .badge-purple {{ background:rgba(139,92,246,0.12); color:#8B5CF6; border:1px solid rgba(139,92,246,0.2); }}
    .badge-live   {{ background:rgba(16,185,129,0.12); color:#10B981; border:1px solid rgba(16,185,129,0.2); }}
    .badge-dot    {{ width:6px; height:6px; border-radius:50%; background:currentColor; }}

    /* ── Predict result ── */
    .predict-result {{
        background: linear-gradient(135deg, #0D9968 0%, #1D4ED8 100%);
        border-radius: var(--radius);
        padding: 2.5rem;
        text-align: center;
        color: #fff;
    }}
    .predict-result .pr-eyebrow {{
        font-size: 0.7rem;
        font-weight: 600;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        opacity: 0.75;
        margin-bottom: 0.5rem;
    }}
    .predict-result .pr-cluster {{
        font-size: 3.5rem;
        font-weight: 800;
        letter-spacing: -0.03em;
        line-height: 1;
    }}
    .predict-result .pr-label {{
        font-size: 1rem;
        font-weight: 500;
        opacity: 0.85;
        margin-top: 0.4rem;
    }}

    /* ── Strategy card ── */
    .strategy-card {{
        background: var(--surface2);
        border: 1px solid var(--border);
        border-radius: var(--radius-sm);
        padding: 1rem 1.1rem;
        margin-bottom: 0.75rem;
    }}
    .strategy-title {{
        font-size: 0.85rem;
        font-weight: 600;
        color: var(--text);
        margin-bottom: 0.3rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }}
    .strategy-body {{
        font-size: 0.8rem;
        color: var(--muted);
        line-height: 1.65;
    }}

    /* ── Roadmap card ── */
    .roadmap-card {{
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: var(--radius-sm);
        padding: 1.1rem;
        position: relative;
        overflow: hidden;
    }}
    .roadmap-quarter {{
        font-size: 0.7rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        margin-bottom: 0.2rem;
    }}
    .roadmap-phase {{
        font-size: 0.875rem;
        font-weight: 600;
        color: var(--text);
        margin-bottom: 0.4rem;
    }}
    .roadmap-desc {{
        font-size: 0.775rem;
        color: var(--muted);
        line-height: 1.6;
    }}
    .roadmap-accent {{
        position: absolute;
        top: 0; left: 0;
        width: 100%; height: 3px;
        border-radius: var(--radius-sm) var(--radius-sm) 0 0;
    }}

    /* ── Streamlit overrides ── */
    .stDataFrame {{ border-radius: var(--radius) !important; overflow: hidden; }}
    .stDataFrame table {{ font-size: 0.82rem !important; }}

    .stSelectbox > div > div,
    .stNumberInput > div > div > input,
    .stTextInput > div > div > input {{
        background: var(--input-bg) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--radius-sm) !important;
        color: var(--text) !important;
        font-size: 0.875rem !important;
    }}
    .stSelectbox > div > div:focus-within,
    .stNumberInput > div > div > input:focus,
    .stTextInput > div > div > input:focus {{
        border-color: var(--accent) !important;
        box-shadow: 0 0 0 3px var(--accent-dim) !important;
        outline: none !important;
    }}
    label[data-testid="stWidgetLabel"] p {{
        font-size: 0.8rem !important;
        font-weight: 500 !important;
        color: var(--soft) !important;
    }}

    /* Primary button */
    .stButton > button[kind="primary"],
    button[data-testid="baseButton-primary"] {{
        background: var(--accent) !important;
        border: none !important;
        border-radius: var(--radius-sm) !important;
        color: #fff !important;
        font-weight: 600 !important;
        font-size: 0.875rem !important;
        padding: 0.6rem 1.5rem !important;
        transition: opacity 0.15s ease, transform 0.15s ease !important;
        box-shadow: 0 1px 3px var(--shadow) !important;
    }}
    .stButton > button[kind="primary"]:hover {{
        opacity: 0.9 !important;
        transform: translateY(-1px) !important;
    }}

    /* Download button */
    .stDownloadButton > button {{
        background: var(--surface2) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--radius-sm) !important;
        color: var(--text) !important;
        font-weight: 500 !important;
        font-size: 0.875rem !important;
    }}

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {{
        background: var(--surface2) !important;
        border-radius: var(--radius-sm) !important;
        padding: 4px !important;
        gap: 2px !important;
        border: 1px solid var(--border) !important;
    }}
    .stTabs [data-baseweb="tab"] {{
        background: transparent !important;
        border: none !important;
        border-radius: 6px !important;
        font-size: 0.82rem !important;
        font-weight: 500 !important;
        color: var(--muted) !important;
        padding: 0.4rem 1rem !important;
    }}
    .stTabs [aria-selected="true"] {{
        background: var(--surface) !important;
        color: var(--text) !important;
        box-shadow: 0 1px 4px var(--shadow) !important;
    }}

    /* Expander */
    .streamlit-expanderHeader {{
        background: var(--surface2) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--radius-sm) !important;
        font-size: 0.875rem !important;
        font-weight: 600 !important;
        color: var(--text) !important;
        padding: 0.75rem 1rem !important;
    }}
    .streamlit-expanderContent {{
        border: 1px solid var(--border) !important;
        border-top: none !important;
        border-radius: 0 0 var(--radius-sm) var(--radius-sm) !important;
        background: var(--surface) !important;
        padding: 1rem !important;
    }}

    /* Divider */
    hr {{ border: none; border-top: 1px solid var(--border); margin: 1.5rem 0; }}

    /* Spinner */
    .stSpinner > div {{ border-top-color: var(--accent) !important; }}

    /* Number input buttons */
    .stNumberInput button {{
        background: var(--surface2) !important;
        border-color: var(--border) !important;
        color: var(--text) !important;
    }}

    /* Footer */
    .app-footer {{
        text-align: center;
        font-size: 0.72rem;
        color: var(--muted);
        padding: 2rem 0 0.5rem;
        border-top: 1px solid var(--border);
        margin-top: 3rem;
        letter-spacing: 0.02em;
    }}

    /* Scrollbar */
    ::-webkit-scrollbar {{ width: 6px; height: 6px; }}
    ::-webkit-scrollbar-track {{ background: transparent; }}
    ::-webkit-scrollbar-thumb {{ background: var(--border2); border-radius: 999px; }}
    ::-webkit-scrollbar-thumb:hover {{ background: var(--muted); }}
    </style>
    """, unsafe_allow_html=True)


# ── Lucide icon helper ─────────────────────────────────────────────────────────
# We inline SVG paths directly — no CDN needed, fully offline.
ICONS = {
    "layout-dashboard": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="7" height="9" x="3" y="3" rx="1"/><rect width="7" height="5" x="3" y="15" rx="1"/><rect width="7" height="5" x="14" y="3" rx="1"/><rect width="7" height="9" x="14" y="12" rx="1"/></svg>',
    "table":            '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3H5a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M8 21V9"/><path d="M3 9h18"/><path d="M16 3h5v5"/><path d="m21 3-9 9"/></svg>',
    "scatter-chart":    '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="7.5" cy="7.5" r="1.5"/><circle cx="18.5" cy="5.5" r="1.5"/><circle cx="11.5" cy="11.5" r="1.5"/><circle cx="7.5" cy="16.5" r="1.5"/><circle cx="17.5" cy="14.5" r="1.5"/><path d="M3 3v18h18"/></svg>',
    "target":           '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/></svg>',
    "lightbulb":        '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M15 14c.2-1 .7-1.7 1.5-2.5 1-.9 1.5-2.2 1.5-3.5A6 6 0 0 0 6 8c0 1 .2 2.2 1.5 3.5.7.7 1.3 1.5 1.5 2.5"/><path d="M9 18h6"/><path d="M10 22h4"/></svg>',
    "users":            '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>',
    "layers":           '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m12.83 2.18a2 2 0 0 0-1.66 0L2.6 6.08a1 1 0 0 0 0 1.83l8.58 3.91a2 2 0 0 0 1.66 0l8.58-3.9a1 1 0 0 0 0-1.83Z"/><path d="m22 17.65-9.17 4.16a2 2 0 0 1-1.66 0L2 17.65"/><path d="m22 12.65-9.17 4.16a2 2 0 0 1-1.66 0L2 12.65"/></svg>',
    "credit-card":      '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="20" height="14" x="2" y="5" rx="2"/><line x1="2" x2="22" y1="10" y2="10"/></svg>',
    "calendar":         '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="18" height="18" x="3" y="4" rx="2" ry="2"/><line x1="16" x2="16" y1="2" y2="6"/><line x1="8" x2="8" y1="2" y2="6"/><line x1="3" x2="21" y1="10" y2="10"/></svg>',
    "sun":              '<svg xmlns="http://www.w3.org/2000/svg" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M6.34 17.66l-1.41 1.41M19.07 4.93l-1.41 1.41"/></svg>',
    "moon":             '<svg xmlns="http://www.w3.org/2000/svg" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z"/></svg>',
    "info":             '<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M12 16v-4"/><path d="M12 8h.01"/></svg>',
    "trending-up":      '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="22 7 13.5 15.5 8.5 10.5 2 17"/><polyline points="16 7 22 7 22 13"/></svg>',
    "bar-chart":        '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" x2="12" y1="20" y2="10"/><line x1="18" x2="18" y1="20" y2="4"/><line x1="6" x2="6" y1="20" y2="16"/></svg>',
    "download":         '<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" x2="12" y1="15" y2="3"/></svg>',
    "building":         '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="16" height="20" x="4" y="2" rx="2" ry="2"/><path d="M9 22v-4h6v4"/><path d="M8 6h.01"/><path d="M16 6h.01"/><path d="M12 6h.01"/><path d="M12 10h.01"/><path d="M12 14h.01"/><path d="M16 10h.01"/><path d="M16 14h.01"/><path d="M8 10h.01"/><path d="M8 14h.01"/></svg>',
}

def icon(name: str, color: str = "currentColor", size: int = 16) -> str:
    svg = ICONS.get(name, "")
    if not svg:
        return ""
    return svg.replace('stroke="currentColor"', f'stroke="{color}"') \
              .replace('width="16"', f'width="{size}"') \
              .replace('height="16"', f'height="{size}"') \
              .replace('width="18"', f'width="{size}"') \
              .replace('height="18"', f'height="{size}"') \
              .replace('width="20"', f'width="{size}"') \
              .replace('height="20"', f'height="{size}"') \
              .replace('width="15"', f'width="{size}"') \
              .replace('height="15"', f'height="{size}"') \
              .replace('width="14"', f'width="{size}"') \
              .replace('height="14"', f'height="{size}"')


def render_sidebar() -> str:
    with st.sidebar:
        # Logo
        st.markdown(f"""
        <div style="padding:1.5rem 1.25rem 1rem;border-bottom:1px solid var(--border);">
            <div style="display:flex;align-items:center;gap:0.7rem;">
                <div style="width:36px;height:36px;
                            background:linear-gradient(135deg,#10B981 0%,#2563EB 100%);
                            border-radius:10px;display:flex;align-items:center;
                            justify-content:center;flex-shrink:0;">
                    {icon("building", "#fff", 18)}
                </div>
                <div>
                    <div style="font-size:0.95rem;font-weight:700;
                                color:var(--text);letter-spacing:-0.01em;">
                        SegmentIQ
                    </div>
                    <div style="font-size:0.65rem;color:var(--muted);
                                letter-spacing:0.07em;font-weight:500;">
                        BANKING ANALYTICS
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div style="padding:0.75rem 1rem 0.5rem;">
            <div style="font-size:0.68rem;font-weight:600;color:var(--muted);
                        letter-spacing:0.08em;text-transform:uppercase;">
                Navigation
            </div>
        </div>
        """, unsafe_allow_html=True)

        nav_items = [
            ("dashboard", "layout-dashboard", "Dashboard"),
            ("explorer",  "table",            "Dataset Explorer"),
            ("analysis",  "scatter-chart",    "Cluster Analysis"),
            ("predict",   "target",           "Predict Segment"),
            ("insights",  "lightbulb",        "Business Insights"),
        ]

        for key, icon_name, label in nav_items:
            is_active = st.session_state.page == key
            active_style = (
                "background:var(--nav-active);color:var(--accent);"
                if is_active else ""
            )
            # Use a button per nav item
            if st.button(
                label,
                key=f"nav_{key}",
                width='stretch',
            ):
                st.session_state.page = key
                st.rerun()

        st.markdown("""
        <div style="padding:0.5rem 1rem;">
            <div style="height:1px;background:var(--border);"></div>
        </div>
        """, unsafe_allow_html=True)

        # Theme toggle
        mode_icon = icon("sun", "currentColor", 15) if st.session_state.dark_mode else icon("moon", "currentColor", 15)
        mode_text = "Light Mode" if st.session_state.dark_mode else "Dark Mode"
        if st.button(f"{mode_text}", key="theme_toggle", width='stretch'):
            st.session_state.dark_mode = not st.session_state.dark_mode
            st.rerun()

        st.markdown("""
        <div style="margin-top:2rem;
                    padding:1.25rem;border-top:1px solid var(--border);">
            <div style="font-size:0.8rem;color:var(--muted);line-height:1.8;">
                AI-Driven Customer Segmentation<br>
                <span style="color:var(--muted);">Final Year Project · 2026</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    return st.session_state.page



def main():
    inject_css(st.session_state.dark_mode)
    page = render_sidebar()

    if page == "dashboard":
        from pages.dashboard import render
        render()
    elif page == "explorer":
        try:
            from pages.explorer import render
            render()
        except Exception as e:
            st.error(f"Explorer error: {e}")
    elif page == "analysis":
        try:
            from pages.analysis import render
            render()
        except Exception as e:
            st.error(f"Analysis error: {e}")
    elif page == "predict":
        try:
            from pages.predict import render
            render()
        except Exception as e:
            st.error(f"Predict error: {e}")
    elif page == "insights":
        try:
            from pages.insights import render
            render()
        except Exception as e:
            st.error(f"Insights error: {e}")

    st.markdown("""
    <div class="app-footer">
        SegmentIQ &nbsp;&middot;&nbsp; AI-Driven Customer Segmentation
        &nbsp;&middot;&nbsp; Built with Streamlit &amp; Scikit-learn
        &nbsp;&middot;&nbsp; Final Year Project 2026
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
