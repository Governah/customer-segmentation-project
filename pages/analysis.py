"""
pages/analysis.py — Cluster Analysis. No emojis, Lucide SVG icons.
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
CLUSTER_INSIGHTS = {
    0: "Low-Value customers have modest credit limits and fewer cards. They represent growth potential through targeted credit limit increase campaigns.",
    1: "High-Value customers carry the highest credit limits and card counts. Premium service offerings will deepen retention.",
    2: "Loyal customers show long account tenure. Retention programmes and anniversary rewards will reinforce their commitment.",
    3: "Mixed-profile customers display varied behaviours. Personalised products and behavioural nudges will improve engagement.",
}

SVG_INFO = '<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="var(--accent)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M12 16v-4"/><path d="M12 8h.01"/></svg>'

@st.cache_data(show_spinner=False)
def load_data():
    df = pd.read_csv(CLUSTERED_CSV)
    df["Cluster"] = df["Cluster"].astype(int)
    return df

def dark():
    return st.session_state.get("dark_mode", True)

def theme(fig):
    bg    = "#111827" if dark() else "#FFFFFF"
    grid  = "#1E293B" if dark() else "#F1F5F9"
    text  = "#F1F5F9" if dark() else "#0F172A"
    muted = "#64748B"
    fig.update_layout(
        paper_bgcolor=bg, plot_bgcolor=bg,
        font=dict(family="Inter, sans-serif", color=text, size=12),
        margin=dict(l=0, r=10, t=10, b=0),
        xaxis=dict(gridcolor=grid, linecolor=grid,
                   tickfont=dict(color=muted, size=11), zeroline=False),
        yaxis=dict(gridcolor=grid, linecolor=grid,
                   tickfont=dict(color=muted, size=11), zeroline=False),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=muted, size=11)),
        hoverlabel=dict(bgcolor=bg, bordercolor=grid,
                        font=dict(family="Inter", size=12, color=text)),
    )
    return fig

def insight(text):
    return f"""<div class="insight-box">{SVG_INFO}<span>{text}</span></div>"""

@st.cache_data(show_spinner=False)
def pca_scatter(df):
    from sklearn.decomposition import PCA
    from sklearn.preprocessing import StandardScaler
    features = [c for c in ["credit_limit","num_cards_issued","account_age",
                             "pin_age","has_chip","card_brand_encoded"] if c in df.columns]
    X = df[features].dropna()
    coords = PCA(n_components=2).fit_transform(StandardScaler().fit_transform(X))
    plot_df = pd.DataFrame({"PC1":coords[:,0],"PC2":coords[:,1],
                             "Cluster":df.loc[X.index,"Cluster"].values})
    fig = go.Figure()
    for c in sorted(plot_df["Cluster"].unique()):
        sub = plot_df[plot_df["Cluster"]==c]
        fig.add_trace(go.Scatter(
            x=sub["PC1"], y=sub["PC2"], mode="markers",
            name=CLUSTER_LABELS.get(c,f"Cluster {c}"),
            marker=dict(color=CLUSTER_COLORS.get(c,"#6B7280"),
                        size=4, opacity=0.65, line=dict(width=0)),
            hovertemplate=f"<b>{CLUSTER_LABELS.get(c,'')}</b><br>PC1: %{{x:.2f}}<br>PC2: %{{y:.2f}}<extra></extra>",
        ))
    theme(fig)
    fig.update_layout(height=400,
                      xaxis_title="Principal Component 1",
                      yaxis_title="Principal Component 2",
                      legend=dict(orientation="h",y=-0.12))
    return fig

def credit_boxplot(df):
    fig = go.Figure()
    for c in sorted(df["Cluster"].unique()):
        sub = df[df["Cluster"]==c]["credit_limit"].dropna()
        fig.add_trace(go.Box(
            y=sub, name=CLUSTER_LABELS.get(c,f"Cluster {c}"),
            marker_color=CLUSTER_COLORS.get(c,"#6B7280"),
            line_color=CLUSTER_COLORS.get(c,"#6B7280"),
            fillcolor=CLUSTER_COLORS.get(c,"#6B7280"),
            opacity=0.65, boxmean=True,
        ))
    theme(fig)
    fig.update_layout(height=360, showlegend=False)
    fig.update_yaxes(tickprefix="$", tickformat=",.0f")
    return fig

def cards_hist(df):
    fig = go.Figure()
    for c in sorted(df["Cluster"].unique()):
        sub = df[df["Cluster"]==c]["num_cards_issued"].dropna()
        fig.add_trace(go.Histogram(
            x=sub, name=CLUSTER_LABELS.get(c,f"Cluster {c}"),
            marker_color=CLUSTER_COLORS.get(c,"#6B7280"),
            opacity=0.65, nbinsx=15,
        ))
    theme(fig)
    fig.update_layout(height=340, barmode="overlay",
                      legend=dict(orientation="h",y=-0.18))
    fig.update_xaxes(title_text="Number of Cards Issued")
    fig.update_yaxes(title_text="Count")
    return fig

def age_bar(df):
    agg = df.groupby("Cluster")["account_age"].mean().reset_index()
    agg["label"] = agg["Cluster"].map(CLUSTER_LABELS)
    agg["color"] = agg["Cluster"].map(CLUSTER_COLORS)
    fig = go.Figure(go.Bar(
        x=agg["label"], y=agg["account_age"],
        marker=dict(color=agg["color"].tolist(), line=dict(width=0)),
        text=[f"{v:.1f} yrs" for v in agg["account_age"]],
        textposition="outside", textfont=dict(size=11),
        hovertemplate="<b>%{x}</b><br>Avg Age: %{y:.1f} yrs<extra></extra>",
    ))
    theme(fig)
    fig.update_layout(height=320)
    fig.update_yaxes(title_text="Years")
    return fig

def render():
    df = load_data()

    st.markdown("""
    <div class="page-header">
        <div class="page-title">Cluster Analysis</div>
        <div class="page-sub">Deep-dive into segment behaviour, distributions, and patterns.</div>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "PCA Scatter", "Summary", "Credit Limit", "Cards Issued", "Account Age"
    ])

    with tab1:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        with st.spinner("Running PCA…"):
            st.plotly_chart(pca_scatter(df), width='stretch',
                            config={"displayModeBar":False})
        st.markdown(insight(
            "PCA reduces all features to 2 dimensions so clusters can be visualised. "
            "Well-separated regions indicate strong cluster distinctiveness. "
            "Overlapping areas represent borderline customer profiles."
        ), unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with tab2:
        agg = df.groupby("Cluster").agg(
            Count=("Cluster","count"),
            Avg_Credit=("credit_limit","mean"),
            Avg_Cards=("num_cards_issued","mean"),
            Avg_Age=("account_age","mean"),
        ).reset_index()
        agg["Segment"]   = agg["Cluster"].map(CLUSTER_LABELS)
        agg["Share (%)"] = (agg["Count"]/len(df)*100).round(1)
        agg["Avg_Credit"] = agg["Avg_Credit"].map(lambda x:f"${x:,.0f}")
        agg["Avg_Cards"]  = agg["Avg_Cards"].round(2)
        agg["Avg_Age"]    = agg["Avg_Age"].round(1)
        agg = agg[["Cluster","Segment","Count","Share (%)","Avg_Credit","Avg_Cards","Avg_Age"]]
        agg.columns = ["Cluster","Segment","Count","Share (%)","Avg Credit","Avg Cards","Avg Age (yrs)"]
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.dataframe(agg, width='stretch', hide_index=True)
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)
        cols = st.columns(2)
        for i, (c_id, ins) in enumerate(CLUSTER_INSIGHTS.items()):
            with cols[i%2]:
                color = CLUSTER_COLORS.get(c_id,"#6B7280")
                st.markdown(f"""
                <div class="kpi-card" style="margin-bottom:0.75rem;">
                    <div class="kpi-bar" style="top:0;bottom:auto;height:3px;
                         border-radius:var(--radius) var(--radius) 0 0;background:{color};"></div>
                    <div class="kpi-label" style="margin-top:0.4rem;">
                        Cluster {c_id}
                    </div>
                    <div class="kpi-value" style="font-size:1rem;margin-bottom:0.4rem;">
                        {CLUSTER_LABELS.get(c_id,'')}
                    </div>
                    <div class="kpi-sub" style="line-height:1.65;">{ins}</div>
                </div>
                """, unsafe_allow_html=True)

    with tab3:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.plotly_chart(credit_boxplot(df), width='stretch',
                        config={"displayModeBar":False})
        st.markdown(insight(
            "The boxplot shows the spread and median credit limit within each segment. "
            "High variance clusters may benefit from personalised limit adjustments. "
            "Outliers represent exceptional customers worth further investigation."
        ), unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with tab4:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.plotly_chart(cards_hist(df), width='stretch',
                        config={"displayModeBar":False})
        st.markdown(insight(
            "Overlapping histograms reveal how card issuance differs across segments. "
            "Clusters concentrated at low card counts are strong cross-sell candidates."
        ), unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with tab5:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.plotly_chart(age_bar(df), width='stretch',
                        config={"displayModeBar":False})
        st.markdown(insight(
            "Account age is a strong proxy for loyalty. Segments with longer average tenure "
            "carry lower churn risk. Short-tenure segments need onboarding programmes to "
            "increase lifetime value."
        ), unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)