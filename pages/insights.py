"""
pages/insights.py — Business Insights & Recommendations. No emojis, Lucide SVG icons.
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path

ROOT          = Path(__file__).parent.parent
CLUSTERED_CSV = ROOT / "data" / "clustered_data.csv"

CLUSTER_COLORS = {0:"#10B981", 1:"#3B82F6", 2:"#F97316", 3:"#8B5CF6"}
CLUSTER_LABELS = {0:"Low-Value", 1:"High-Value", 2:"Loyal", 3:"Mixed"}
BADGE_CLASS    = {0:"badge-green", 1:"badge-blue", 2:"badge-orange", 3:"badge-purple"}

INSIGHTS = {
    0: {
        "label": "Low-Value",
        "color": "#10B981",
        "description": "Customers in this segment have lower credit limits and fewer cards. They are early in their banking journey and represent untapped growth potential.",
        "strategies": [
            ("Credit Limit Campaign",  "Offer incremental credit limit increases tied to on-time payment milestones to build trust and spending capacity."),
            ("Introductory Rewards",   "Introduce a cashback or points programme to incentivise card usage and build positive spending habits."),
            ("Digital Onboarding",     "Deploy targeted in-app messages and financial tips to improve product adoption and digital engagement."),
            ("Credit Education",       "Provide credit score monitoring tools and personalised tips to help customers improve their financial health."),
        ],
        "kpis": ["Target: +20% credit limit uptake", "Goal: Increase avg cards 1 → 2", "Timeline: 6 months"],
    },
    1: {
        "label": "High-Value",
        "color": "#3B82F6",
        "description": "These customers hold the highest credit limits and the most cards. They generate significant interchange revenue and have deep product engagement.",
        "strategies": [
            ("Premium Banking Tier",   "Introduce a premium tier with dedicated relationship managers, priority support, and exclusive benefits."),
            ("Travel Rewards",         "Offer airline miles, airport lounge access, and travel insurance as loyalty perks."),
            ("Investment Products",    "Cross-sell wealth management and investment products to capture a larger share of wallet."),
            ("Fraud Protection Plus",  "Provide enhanced fraud monitoring and zero-liability guarantees to reinforce security confidence."),
        ],
        "kpis": ["Target: 95% retention rate", "Goal: +1 product per customer", "Timeline: Ongoing"],
    },
    2: {
        "label": "Loyal",
        "color": "#F97316",
        "description": "Long-standing customers who have maintained consistent relationships with the bank. They are low churn risk but may be under-engaged with newer products.",
        "strategies": [
            ("Anniversary Rewards",    "Recognise account milestones with bonus points, fee waivers, or exclusive gifts to celebrate loyalty."),
            ("Relationship Manager",   "Assign dedicated relationship managers to high-tenure customers to deepen the personal connection."),
            ("Product Refresh",        "Proactively upgrade older card products to modern chip-and-tap versions with better benefits."),
            ("Referral Programme",     "Leverage their loyalty with a structured referral programme — loyal customers are the best brand ambassadors."),
        ],
        "kpis": ["Target: <5% churn rate", "Goal: 80% NPS score", "Timeline: 12 months"],
    },
    3: {
        "label": "Mixed",
        "color": "#8B5CF6",
        "description": "Customers with mixed behavioural signals that don't fit neatly into one segment. They require personalised approaches to guide their journey.",
        "strategies": [
            ("Personalised Offers",    "Use ML-driven next-best-action models to serve the most relevant offer at the right moment."),
            ("Behavioural Nudges",     "Send timely in-app notifications that encourage positive financial behaviours like on-time payments."),
            ("Needs Assessment",       "Conduct digital surveys or in-branch consultations to better understand their financial goals."),
            ("Bundled Products",       "Offer curated product bundles (e.g. savings + credit) that simplify decision-making."),
        ],
        "kpis": ["Target: Migrate segment within 12mo", "Goal: +15% product adoption", "Timeline: 9 months"],
    },
}

ROADMAP = [
    ("Q1", "Foundation",   "#10B981", "Deploy credit limit campaigns for Cluster 0. Launch premium tier for Cluster 1."),
    ("Q2", "Engagement",   "#3B82F6", "Roll out loyalty anniversary programme for Cluster 2. Begin behavioural nudge campaigns for Cluster 3."),
    ("Q3", "Optimisation", "#F97316", "Measure NPS and churn across all segments. A/B test personalised offers for Cluster 3."),
    ("Q4", "Growth",       "#8B5CF6", "Re-segment customers on updated data. Launch referral programme. Review KPI targets."),
]

# ── Inline SVG ────────────────────────────────
SVG = {
    "info":        '<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="var(--accent)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M12 16v-4"/><path d="M12 8h.01"/></svg>',
    "check":       '<svg xmlns="http://www.w3.org/2000/svg" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>',
    "arrow-right": '<svg xmlns="http://www.w3.org/2000/svg" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14"/><path d="m12 5 7 7-7 7"/></svg>',
    "bar-chart":   '<svg xmlns="http://www.w3.org/2000/svg" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="var(--muted)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" x2="12" y1="20" y2="10"/><line x1="18" x2="18" y1="20" y2="4"/><line x1="6" x2="6" y1="20" y2="16"/></svg>',
    "map":         '<svg xmlns="http://www.w3.org/2000/svg" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="var(--muted)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="3 6 9 3 15 6 21 3 21 18 15 21 9 18 3 21"/><line x1="9" x2="9" y1="3" y2="18"/><line x1="15" x2="15" y1="6" y2="21"/></svg>',
}

def insight(text):
    return f'<div class="insight-box">{SVG["info"]}<span>{text}</span></div>'

@st.cache_data(show_spinner=False)
def load_data():
    df = pd.read_csv(CLUSTERED_CSV)
    df["Cluster"] = df["Cluster"].astype(int)
    return df

def dark():
    return st.session_state.get("dark_mode", True)

def revenue_chart(df):
    agg = df.groupby("Cluster").agg(
        Count=("Cluster","count"),
        Avg_Credit=("credit_limit","mean"),
    ).reset_index()
    agg["Revenue_K"] = (agg["Count"] * agg["Avg_Credit"] * 0.015 / 1000).round(1)
    agg["label"]     = agg["Cluster"].map(CLUSTER_LABELS)
    agg["color"]     = agg["Cluster"].map(CLUSTER_COLORS)

    bg    = "#111827" if dark() else "#FFFFFF"
    grid  = "#1E293B" if dark() else "#F1F5F9"
    text  = "#F1F5F9" if dark() else "#0F172A"
    muted = "#64748B"

    fig = go.Figure(go.Bar(
        x=agg["label"], y=agg["Revenue_K"],
        marker=dict(color=agg["color"].tolist(), line=dict(width=0)),
        text=[f"${v:.1f}K" for v in agg["Revenue_K"]],
        textposition="outside", textfont=dict(size=11),
        hovertemplate="<b>%{x}</b><br>Est. Revenue: $%{y:.1f}K<extra></extra>",
    ))
    fig.update_layout(
        paper_bgcolor=bg, plot_bgcolor=bg,
        font=dict(family="Inter, sans-serif", color=text, size=12),
        margin=dict(l=0, r=10, t=10, b=0),
        height=300,
        xaxis=dict(gridcolor=grid, linecolor=grid,
                   tickfont=dict(color=muted, size=11), showgrid=False),
        yaxis=dict(gridcolor=grid, linecolor=grid,
                   tickfont=dict(color=muted, size=11),
                   tickprefix="$", ticksuffix="K"),
        hoverlabel=dict(bgcolor=bg, bordercolor=grid,
                        font=dict(family="Inter", size=12, color=text)),
    )
    return fig

def render():
    df = load_data()

    st.markdown("""
    <div class="page-header">
        <div class="page-title">Business Insights</div>
        <div class="page-sub">Strategic recommendations and revenue opportunities per segment.</div>
    </div>
    """, unsafe_allow_html=True)

    # ── Revenue opportunity chart ─────────────
    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="chart-title">
        {SVG["bar-chart"]} Estimated Revenue Opportunity by Segment
    </div>
    <div class="chart-sub">
        Approximated at 1.5% of average credit limit × customer count per cluster.
    </div>
    """, unsafe_allow_html=True)
    st.plotly_chart(revenue_chart(df), width='stretch',
                    config={"displayModeBar": False})
    st.markdown(insight(
        "High-value and loyal segments typically drive the majority of interchange and "
        "interest income. Investing in retention for these clusters has the highest ROI."
    ), unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

    # ── Per-cluster strategy sections ─────────
    for c_id, info in INSIGHTS.items():
        color      = info["color"]
        badge_cls  = BADGE_CLASS.get(c_id, "badge-green")

        with st.expander(
            f"Cluster {c_id}  —  {info['label']}",
            expanded=(c_id == 0),
        ):
            # Description row
            st.markdown(f"""
            <div style="display:flex;align-items:flex-start;gap:0.75rem;
                        margin-bottom:1.1rem;">
                <span class="badge {badge_cls}" style="margin-top:2px;flex-shrink:0;">
                    Cluster {c_id}
                </span>
                <span style="font-size:0.83rem;color:var(--soft);line-height:1.65;">
                    {info["description"]}
                </span>
            </div>
            """, unsafe_allow_html=True)

            # Strategy cards — 2 columns
            s_cols = st.columns(2)
            for i, (title, body) in enumerate(info["strategies"]):
                with s_cols[i % 2]:
                    arrow = SVG["arrow-right"].replace("{c}", color)
                    st.markdown(f"""
                    <div class="strategy-card">
                        <div class="strategy-title">
                            {arrow}
                            {title}
                        </div>
                        <div class="strategy-body">{body}</div>
                    </div>
                    """, unsafe_allow_html=True)

            # KPI targets
            st.markdown("<div style='height:0.6rem'></div>", unsafe_allow_html=True)
            k_cols = st.columns(len(info["kpis"]))
            for i, kpi in enumerate(info["kpis"]):
                with k_cols[i]:
                    st.markdown(f"""
                    <div style="background:var(--surface2);border:1px solid var(--border);
                                border-radius:var(--radius-sm);padding:0.65rem 1rem;
                                text-align:center;">
                        <div style="font-size:0.75rem;font-weight:600;color:{color};">
                            {kpi}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

        st.markdown("<div style='height:0.4rem'></div>", unsafe_allow_html=True)

    # ── Strategic roadmap ─────────────────────
    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="chart-title">
        {SVG["map"]} Strategic Roadmap
    </div>
    <div class="chart-sub">12-month execution plan across all segments.</div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)
    r_cols = st.columns(4)
    for i, (quarter, phase, color, desc) in enumerate(ROADMAP):
        with r_cols[i]:
            st.markdown(f"""
            <div class="roadmap-card">
                <div class="roadmap-accent" style="background:{color};"></div>
                <div class="roadmap-quarter" style="color:{color};margin-top:0.5rem;">
                    {quarter}
                </div>
                <div class="roadmap-phase">{phase}</div>
                <div class="roadmap-desc">{desc}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)