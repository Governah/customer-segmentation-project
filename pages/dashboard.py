"""
pages/dashboard.py — Dashboard page with Lucide SVG icons, no emojis.
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

# ── Inline SVG icons (subset) ─────────────────
SVG = {
    "users":       '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>',
    "layers":      '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m12.83 2.18a2 2 0 0 0-1.66 0L2.6 6.08a1 1 0 0 0 0 1.83l8.58 3.91a2 2 0 0 0 1.66 0l8.58-3.9a1 1 0 0 0 0-1.83Z"/><path d="m22 17.65-9.17 4.16a2 2 0 0 1-1.66 0L2 17.65"/><path d="m22 12.65-9.17 4.16a2 2 0 0 1-1.66 0L2 12.65"/></svg>',
    "credit-card": '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="20" height="14" x="2" y="5" rx="2"/><line x1="2" x2="22" y1="10" y2="10"/></svg>',
    "calendar":    '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="18" height="18" x="3" y="4" rx="2" ry="2"/><line x1="16" x2="16" y1="2" y2="6"/><line x1="8" x2="8" y1="2" y2="6"/><line x1="3" x2="21" y1="10" y2="10"/></svg>',
    "info":        '<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M12 16v-4"/><path d="M12 8h.01"/></svg>',
    "pie-chart":   '<svg xmlns="http://www.w3.org/2000/svg" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21.21 15.89A10 10 0 1 1 8 2.83"/><path d="M22 12A10 10 0 0 0 12 2v10z"/></svg>',
    "bar-chart":   '<svg xmlns="http://www.w3.org/2000/svg" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" x2="12" y1="20" y2="10"/><line x1="18" x2="18" y1="20" y2="4"/><line x1="6" x2="6" y1="20" y2="16"/></svg>',
    "activity":    '<svg xmlns="http://www.w3.org/2000/svg" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>',
    "table":       '<svg xmlns="http://www.w3.org/2000/svg" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3H5a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M8 21V9"/><path d="M3 9h18"/></svg>',
}

def si(name, color="var(--muted)"):
    return SVG.get(name, "").replace("{c}", color)

def dark():
    return st.session_state.get("dark_mode", True)

def fmt_currency(v):
    if v >= 1_000_000: return f"${v/1_000_000:.1f}M"
    if v >= 1_000:     return f"${v/1_000:.1f}K"
    return f"${v:,.0f}"

def fmt_number(v):
    if v >= 1_000_000: return f"{v/1_000_000:.1f}M"
    if v >= 1_000:     return f"{v/1_000:.1f}K"
    return f"{int(v):,}"

@st.cache_data(show_spinner=False)
def load_data():
    df = pd.read_csv(CLUSTERED_CSV)
    df["Cluster"] = df["Cluster"].astype(int)
    return df

def theme(fig, title=""):
    bg    = "#111827" if dark() else "#FFFFFF"
    grid  = "#1E293B" if dark() else "#F1F5F9"
    text  = "#F1F5F9" if dark() else "#0F172A"
    muted = "#64748B"
    fig.update_layout(
        paper_bgcolor=bg, plot_bgcolor=bg,
        font=dict(family="Inter, sans-serif", color=text, size=12),
        title=dict(text=title, font=dict(size=13, color=text), x=0),
        margin=dict(l=0, r=10, t=36 if title else 10, b=0),
        xaxis=dict(gridcolor=grid, linecolor=grid,
                   tickfont=dict(color=muted, size=11), zeroline=False),
        yaxis=dict(gridcolor=grid, linecolor=grid,
                   tickfont=dict(color=muted, size=11), zeroline=False),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=muted, size=11)),
        hoverlabel=dict(bgcolor=bg, bordercolor=grid,
                        font=dict(family="Inter", size=12, color=text)),
    )
    return fig

def kpi_card(icon_name, label, value, sub, bg_color, icon_color):
    return f"""
    <div class="kpi-card">
        <div class="kpi-icon-wrap" style="background:{bg_color};">
            {si(icon_name, icon_color)}
        </div>
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        <div class="kpi-sub">{sub}</div>
        <div class="kpi-bar" style="background:{icon_color};opacity:0.6;"></div>
    </div>
    """

def insight(text):
    info_svg = si("info", "var(--accent)")
    return f"""
    <div class="insight-box">
        {info_svg}
        <span>{text}</span>
    </div>
    """

def chart_header(icon_name, title, subtitle=""):
    sub_html = f'<div class="chart-sub">{subtitle}</div>' if subtitle else ""
    return f"""
    <div class="chart-title">
        {si(icon_name, "var(--muted)")}
        {title}
    </div>
    {sub_html}
    """

# ── Charts ────────────────────────────────────
def donut_chart(df):
    counts = df["Cluster"].value_counts().sort_index()
    labels = [CLUSTER_LABELS.get(c, f"Cluster {c}") for c in counts.index]
    colors = [CLUSTER_COLORS.get(c, "#6B7280") for c in counts.index]
    fig = go.Figure(go.Pie(
        labels=labels, values=counts.values, hole=0.65,
        marker=dict(colors=colors, line=dict(width=0)),
        textinfo="percent", textfont=dict(size=11, family="Inter"),
        hovertemplate="<b>%{label}</b><br>%{value:,} customers<br>%{percent}<extra></extra>",
        direction="clockwise",
    ))
    fig.add_annotation(
        text=f"<b>{fmt_number(len(df))}</b>",
        x=0.5, y=0.55, showarrow=False,
        font=dict(size=22, family="Inter", color="#F1F5F9" if dark() else "#0F172A"),
    )
    fig.add_annotation(
        text="customers",
        x=0.5, y=0.38, showarrow=False,
        font=dict(size=11, family="Inter", color="#64748B"),
    )
    theme(fig)
    fig.update_layout(
        height=300,
        showlegend=True,
        legend=dict(orientation="h", x=0.5, xanchor="center", y=-0.08),
        margin=dict(l=0, r=0, t=0, b=30),
    )
    return fig

def credit_bar(df):
    agg = df.groupby("Cluster")["credit_limit"].mean().reset_index()
    agg["label"] = agg["Cluster"].map(CLUSTER_LABELS)
    agg["color"] = agg["Cluster"].map(CLUSTER_COLORS)
    agg = agg.sort_values("credit_limit")
    fig = go.Figure(go.Bar(
        y=agg["label"], x=agg["credit_limit"], orientation="h",
        marker=dict(color=agg["color"].tolist(), line=dict(width=0)),
        text=[fmt_currency(v) for v in agg["credit_limit"]],
        textposition="outside", textfont=dict(size=11),
        hovertemplate="<b>%{y}</b><br>Avg Credit Limit: $%{x:,.0f}<extra></extra>",
    ))
    theme(fig)
    fig.update_layout(height=300, margin=dict(l=0, r=70, t=10, b=0))
    fig.update_xaxes(tickprefix="$", tickformat=",.0f", showgrid=True)
    fig.update_yaxes(showgrid=False)
    return fig

def cards_bar(df):
    agg = df.groupby("Cluster")["num_cards_issued"].mean().reset_index()
    agg["label"] = agg["Cluster"].map(CLUSTER_LABELS)
    agg["color"] = agg["Cluster"].map(CLUSTER_COLORS)
    fig = go.Figure(go.Bar(
        x=agg["label"], y=agg["num_cards_issued"],
        marker=dict(color=agg["color"].tolist(), line=dict(width=0)),
        text=[f"{v:.1f}" for v in agg["num_cards_issued"]],
        textposition="outside", textfont=dict(size=11),
        hovertemplate="<b>%{x}</b><br>Avg Cards: %{y:.2f}<extra></extra>",
    ))
    theme(fig)
    fig.update_layout(height=300, margin=dict(l=0, r=0, t=10, b=0))
    fig.update_yaxes(title_text="Avg Cards", showgrid=True)
    fig.update_xaxes(showgrid=False)
    return fig

def age_violin(df):
    fig = go.Figure()
    for c in sorted(df["Cluster"].unique()):
        vals = df[df["Cluster"] == c]["account_age"].dropna()
        fig.add_trace(go.Violin(
            y=vals, name=CLUSTER_LABELS.get(c, f"Cluster {c}"),
            box_visible=True, meanline_visible=True,
            fillcolor=CLUSTER_COLORS.get(c, "#6B7280"),
            line_color=CLUSTER_COLORS.get(c, "#6B7280"),
            opacity=0.65,
        ))
    theme(fig)
    fig.update_layout(
        height=300, violinmode="group",
        showlegend=False,
        margin=dict(l=0, r=0, t=10, b=0),
    )
    fig.update_yaxes(title_text="Years", showgrid=True)
    return fig

def summary_table(df):
    agg = df.groupby("Cluster").agg(
        Count=("Cluster","count"),
        Avg_Credit=("credit_limit","mean"),
        Avg_Cards=("num_cards_issued","mean"),
        Avg_Age=("account_age","mean"),
    ).reset_index()
    total = len(df)
    agg.insert(1, "Segment",   agg["Cluster"].map(CLUSTER_LABELS))
    agg.insert(2, "Share (%)", (agg["Count"] / total * 100).round(1))
    agg["Avg_Credit"] = agg["Avg_Credit"].map(lambda x: f"${x:,.0f}")
    agg["Avg_Cards"]  = agg["Avg_Cards"].round(2)
    agg["Avg_Age"]    = agg["Avg_Age"].round(1)
    agg.columns = ["Cluster","Segment","Share (%)","Count",
                   "Avg Credit Limit","Avg Cards Issued","Avg Account Age (yrs)"]
    return agg

# ── Render ────────────────────────────────────
def render():
    df = load_data()

    # Header
    col_h, col_b = st.columns([5, 1])
    with col_h:
        st.markdown("""
        <div class="page-header">
            <div class="page-title">Dashboard</div>
            <div class="page-sub">
                Real-time overview of customer segmentation across all clusters.
            </div>
        </div>
        """, unsafe_allow_html=True)
    with col_b:
        st.markdown("""
        <div style="padding-top:0.75rem;text-align:right;">
            <span class="badge badge-live">
                <span class="badge-dot"></span>Live
            </span>
        </div>
        """, unsafe_allow_html=True)

    # KPI row
    total      = len(df)
    n_clusters = df["Cluster"].nunique()
    avg_credit = df["credit_limit"].mean()
    avg_age    = df["account_age"].mean()

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(kpi_card(
            "users","Total Customers", fmt_number(total),
            f"Across {n_clusters} segments",
            "rgba(16,185,129,0.12)","#10B981",
        ), unsafe_allow_html=True)
    with k2:
        st.markdown(kpi_card(
            "layers","Segments", str(n_clusters),
            "KMeans clustering",
            "rgba(59,130,246,0.12)","#3B82F6",
        ), unsafe_allow_html=True)
    with k3:
        st.markdown(kpi_card(
            "credit-card","Avg Credit Limit", fmt_currency(avg_credit),
            "Mean across all customers",
            "rgba(249,115,22,0.12)","#F97316",
        ), unsafe_allow_html=True)
    with k4:
        st.markdown(kpi_card(
            "calendar","Avg Account Age", f"{avg_age:.1f} yrs",
            "Mean customer tenure",
            "rgba(139,92,246,0.12)","#8B5CF6",
        ), unsafe_allow_html=True)

    st.markdown("<div style='height:1.25rem'></div>", unsafe_allow_html=True)

    # Row 1
    col_l, col_r = st.columns([1, 1.5])
    with col_l:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.markdown(chart_header("pie-chart","Cluster Distribution",
                                 "Share of customers per segment"),
                    unsafe_allow_html=True)
        st.plotly_chart(donut_chart(df), width='stretch',
                        config={"displayModeBar":False})
        st.markdown(insight(
            "The dominant cluster holds the largest share of customers. "
            "Smaller clusters often represent high-value or high-potential sub-groups worth targeted investment."
        ), unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col_r:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.markdown(chart_header("bar-chart","Average Credit Limit by Cluster",
                                 "Mean credit limit assigned per segment"),
                    unsafe_allow_html=True)
        st.plotly_chart(credit_bar(df), width='stretch',
                        config={"displayModeBar":False})
        st.markdown(insight(
            "Higher average credit limits indicate premium segment membership. "
            "Clusters with lower limits are prime candidates for upsell and limit-increase campaigns."
        ), unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # Row 2
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.markdown(chart_header("credit-card","Cards Issued by Cluster",
                                 "Average number of cards per customer"),
                    unsafe_allow_html=True)
        st.plotly_chart(cards_bar(df), width='stretch',
                        config={"displayModeBar":False})
        st.markdown(insight(
            "Customers with more cards generate higher interchange revenue. "
            "Low-card clusters are strong cross-sell candidates for additional card products."
        ), unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col_b:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.markdown(chart_header("activity","Account Age Distribution",
                                 "Spread of customer tenure by segment"),
                    unsafe_allow_html=True)
        st.plotly_chart(age_violin(df), width='stretch',
                        config={"displayModeBar":False})
        st.markdown(insight(
            "Longer tenure signals loyalty and lower churn risk. "
            "Segments with younger accounts need early-engagement retention strategies."
        ), unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # Summary table
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown(f'<div class="chart-title">{si("table","var(--muted)")} Cluster Summary</div>',
                unsafe_allow_html=True)
    st.markdown('<div class="chart-sub">Aggregate statistics per segment</div>',
                unsafe_allow_html=True)
    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
    st.dataframe(summary_table(df), width='stretch', hide_index=True)