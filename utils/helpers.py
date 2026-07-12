"""
pages/dashboard.py — Main dashboard overview page.

Sections:
1. Page header with live status badge
2. KPI cards row (Total Customers, Clusters, Avg Credit Limit, Avg Account Age)
3. Cluster Distribution (donut)  +  Credit Limit by Cluster (bar)
4. Cards Issued by Cluster (bar)  +  Account Age Distribution (violin)
5. Cluster size summary table
"""

from __future__ import annotations

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

from utils.helpers import (
    load_clustered,
    apply_theme,
    cluster_color,
    cluster_label,
    CLUSTER_COLORS,
    kpi_card,
    insight_box,
    fmt_currency,
    fmt_number,
    section_header,
)


# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────
def _dark() -> bool:
    return st.session_state.get("dark_mode", False)


def _cluster_display(df: pd.DataFrame) -> pd.DataFrame:
    """Add a human-readable cluster label column."""
    df = df.copy()
    df["Cluster Label"] = df["Cluster"].apply(cluster_label)
    return df


# ─────────────────────────────────────────────
# CHART BUILDERS
# ─────────────────────────────────────────────
def _donut_chart(df: pd.DataFrame) -> go.Figure:
    """Cluster distribution donut chart."""
    counts = df["Cluster"].value_counts().sort_index()
    labels = [cluster_label(c) for c in counts.index]
    colors = [cluster_color(c) for c in counts.index]

    fig = go.Figure(go.Pie(
        labels=labels,
        values=counts.values,
        hole=0.62,
        marker=dict(colors=colors, line=dict(width=2, color="rgba(0,0,0,0)")),
        textinfo="percent",
        textfont=dict(size=12, family="Inter"),
        hovertemplate="<b>%{label}</b><br>Customers: %{value:,}<br>Share: %{percent}<extra></extra>",
    ))

    # Centre annotation
    total = len(df)
    fig.add_annotation(
        text=f"<b>{fmt_number(total)}</b><br><span style='font-size:10px'>customers</span>",
        x=0.5, y=0.5,
        showarrow=False,
        font=dict(size=16, family="Inter"),
    )

    apply_theme(fig, dark=_dark(), title="Cluster Distribution")
    fig.update_layout(
        legend=dict(orientation="h", x=0.5, xanchor="center", y=-0.05),
        margin=dict(l=10, r=10, t=40, b=20),
        height=320,
    )
    return fig


def _credit_limit_bar(df: pd.DataFrame) -> go.Figure:
    """Average credit limit per cluster — horizontal bar."""
    # Detect credit limit column flexibly
    col = _find_col(df, ["credit_limit", "Credit_Limit", "CreditLimit", "credit limit"])
    if col is None:
        return _empty_fig("No Credit Limit column found")

    agg = (
        df.groupby("Cluster")[col]
        .mean()
        .reset_index()
        .rename(columns={col: "Avg Credit Limit"})
    )
    agg["Label"] = agg["Cluster"].apply(cluster_label)
    agg["Color"] = agg["Cluster"].apply(cluster_color)
    agg = agg.sort_values("Cluster")

    fig = go.Figure(go.Bar(
        y=agg["Label"],
        x=agg["Avg Credit Limit"],
        orientation="h",
        marker_color=agg["Color"].tolist(),
        marker_line_width=0,
        hovertemplate="<b>%{y}</b><br>Avg Credit Limit: $%{x:,.0f}<extra></extra>",
        text=[fmt_currency(v) for v in agg["Avg Credit Limit"]],
        textposition="outside",
        textfont=dict(size=11),
    ))

    apply_theme(fig, dark=_dark(), title="Avg Credit Limit by Cluster")
    fig.update_layout(height=320, margin=dict(l=10, r=60, t=40, b=10))
    fig.update_xaxes(tickprefix="$", tickformat=",.0f")
    return fig


def _cards_issued_bar(df: pd.DataFrame) -> go.Figure:
    """Total / average cards issued per cluster — vertical bar."""
    col = _find_col(df, ["num_credit_cards", "NumCreditCards", "cards_issued",
                         "Cards_Issued", "number_of_cards", "NumberOfCards"])
    if col is None:
        return _empty_fig("No Cards Issued column found")

    agg = (
        df.groupby("Cluster")[col]
        .mean()
        .reset_index()
        .rename(columns={col: "Avg Cards Issued"})
    )
    agg["Label"] = agg["Cluster"].apply(cluster_label)
    agg["Color"] = agg["Cluster"].apply(cluster_color)

    fig = go.Figure(go.Bar(
        x=agg["Label"],
        y=agg["Avg Cards Issued"],
        marker_color=agg["Color"].tolist(),
        marker_line_width=0,
        hovertemplate="<b>%{x}</b><br>Avg Cards: %{y:.2f}<extra></extra>",
        text=[f"{v:.2f}" for v in agg["Avg Cards Issued"]],
        textposition="outside",
        textfont=dict(size=11),
    ))

    apply_theme(fig, dark=_dark(), title="Avg Cards Issued by Cluster")
    fig.update_layout(height=300, margin=dict(l=10, r=10, t=40, b=10))
    return fig


def _account_age_violin(df: pd.DataFrame) -> go.Figure:
    """Account age distribution per cluster — violin / box."""
    col = _find_col(df, ["account_age", "AccountAge", "acct_age",
                         "years_as_customer", "account_tenure"])
    if col is None:
        return _empty_fig("No Account Age column found")

    fig = go.Figure()
    for cluster_id in sorted(df["Cluster"].unique()):
        subset = df[df["Cluster"] == cluster_id][col].dropna()
        fig.add_trace(go.Violin(
            y=subset,
            name=cluster_label(cluster_id),
            box_visible=True,
            meanline_visible=True,
            fillcolor=cluster_color(cluster_id),
            line_color=cluster_color(cluster_id),
            opacity=0.7,
            hoverinfo="y+name",
        ))

    apply_theme(fig, dark=_dark(), title="Account Age Distribution by Cluster")
    fig.update_layout(height=300, violinmode="group",
                      legend=dict(orientation="h", y=-0.15))
    fig.update_yaxes(title_text="Account Age (yrs)")
    return fig


# ─────────────────────────────────────────────
# UTILITY
# ─────────────────────────────────────────────
def _find_col(df: pd.DataFrame, candidates: list[str]) -> str | None:
    """Return the first matching column name (case-insensitive)."""
    lower_map = {c.lower(): c for c in df.columns}
    for cand in candidates:
        if cand.lower() in lower_map:
            return lower_map[cand.lower()]
    return None


def _empty_fig(msg: str) -> go.Figure:
    fig = go.Figure()
    fig.add_annotation(text=msg, x=0.5, y=0.5, showarrow=False,
                       font=dict(size=13, color="#64748B"))
    apply_theme(fig, dark=_dark())
    return fig


# ─────────────────────────────────────────────
# MAIN RENDER
# ─────────────────────────────────────────────
def render() -> None:
    df = load_clustered()
    df = _cluster_display(df)
    dark = _dark()

    # ── Page header ───────────────────────────
    col_h1, col_badge = st.columns([6, 1])
    with col_h1:
        st.markdown("""
        <div style="margin-bottom:0.2rem;">
            <span style="font-size:1.6rem;font-weight:800;letter-spacing:-0.02em;">
                Dashboard
            </span>
        </div>
        <div style="font-size:0.85rem;color:var(--text-muted);margin-bottom:1.5rem;">
            Real-time overview of customer segmentation across all clusters.
        </div>
        """, unsafe_allow_html=True)
    with col_badge:
        st.markdown("""
        <div style="padding-top:0.5rem;text-align:right;">
            <span class="badge badge-green">● Live</span>
        </div>
        """, unsafe_allow_html=True)

    # ── KPI Cards ─────────────────────────────
    total_customers = len(df)
    num_clusters    = df["Cluster"].nunique()

    credit_col      = _find_col(df, ["credit_limit"])
    age_col         = _find_col(df, ["account_age"])

    avg_credit  = df[credit_col].mean() if credit_col else 0
    avg_age     = df[age_col].mean()    if age_col    else 0

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(kpi_card(
            "👥", "Total Customers", fmt_number(total_customers),
            sub=f"Across {num_clusters} segments",
            accent_color="#10B981",
        ), unsafe_allow_html=True)
    with c2:
        st.markdown(kpi_card(
            "🗂️", "Segments (Clusters)", str(num_clusters),
            sub="KMeans clustering",
            accent_color="#3B82F6",
        ), unsafe_allow_html=True)
    with c3:
        st.markdown(kpi_card(
            "💳", "Avg Credit Limit",
            fmt_currency(avg_credit) if credit_col else "N/A",
            sub="Mean across all customers",
            accent_color="#F97316",
        ), unsafe_allow_html=True)
    with c4:
        st.markdown(kpi_card(
            "📅", "Avg Account Age",
            f"{avg_age:.1f} yrs" if age_col else "N/A",
            sub="Mean customer tenure",
            accent_color="#8B5CF6",
        ), unsafe_allow_html=True)

    st.markdown("<div style='height:1.4rem'></div>", unsafe_allow_html=True)

    # ── Row 1: Donut + Credit Limit Bar ───────
    col_l, col_r = st.columns([1, 1.4])

    with col_l:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.plotly_chart(_donut_chart(df), width='stretch', config={"displayModeBar": False})
        st.markdown(
            insight_box(
                "The donut chart reveals each segment's share of the customer base. "
                "A dominant cluster may indicate an untapped opportunity in smaller segments."
            ),
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)

    with col_r:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.plotly_chart(_credit_limit_bar(df), width='stretch', config={"displayModeBar": False})
        st.markdown(
            insight_box(
                "Higher average credit limits correlate with premium segment membership. "
                "Segments with lower limits are prime targets for upsell campaigns."
            ),
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)

    # ── Row 2: Cards Issued + Account Age ─────
    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.plotly_chart(_cards_issued_bar(df), width='stretch', config={"displayModeBar": False})
        st.markdown(
            insight_box(
                "Customers holding more cards typically generate higher interchange revenue. "
                "Low-card clusters present cross-sell opportunities for additional card products."
            ),
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)

    with col_b:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.plotly_chart(_account_age_violin(df), width='stretch', config={"displayModeBar": False})
        st.markdown(
            insight_box(
                "Longer account tenure signals loyalty and lower churn risk. "
                "Clusters with younger accounts need early-engagement retention strategies."
            ),
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)

    # ── Cluster summary table ─────────────────
    st.markdown("<div style='height:0.6rem'></div>", unsafe_allow_html=True)
    section_header("📋 Cluster Summary", "Aggregate statistics per segment")

    agg_dict: dict = {"Cluster": "count"}
    if credit_col:
        agg_dict[credit_col] = "mean"
    if age_col:
        agg_dict[age_col] = "mean"

    cards_col = _find_col(df, ["num_credit_cards", "NumCreditCards", "cards_issued",
                                "Cards_Issued", "number_of_cards", "NumberOfCards"])
    if cards_col:
        agg_dict[cards_col] = "mean"

    summary = df.groupby("Cluster").agg(agg_dict).reset_index()
    summary.columns = (
        ["Cluster", "Count"]
        + (["Avg Credit Limit ($)"] if credit_col else [])
        + (["Avg Account Age (yrs)"] if age_col else [])
        + (["Avg Cards Issued"] if cards_col else [])
    )
    summary.insert(1, "Segment", summary["Cluster"].apply(cluster_label))
    summary.insert(2, "Share (%)", (summary["Count"] / total_customers * 100).round(1))

    # Round numeric columns
    for col in summary.columns[4:]:
        summary[col] = summary[col].round(2)

    st.dataframe(
        summary,
        width='stretch',
        hide_index=True,
    )