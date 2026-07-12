"""
pages/explorer.py — Dataset Explorer. No emojis, Lucide SVG icons.
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import pandas as pd
from pathlib import Path

ROOT          = Path(__file__).parent.parent
CLUSTERED_CSV = ROOT / "data" / "clustered_data.csv"
CLUSTER_LABELS = {0:"Low-Value", 1:"High-Value", 2:"Loyal", 3:"Mixed"}

SVG = {
    "search":   '<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="var(--muted)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/></svg>',
    "filter":   '<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="var(--muted)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3"/></svg>',
    "download": '<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" x2="12" y1="15" y2="3"/></svg>',
    "rows":     '<svg xmlns="http://www.w3.org/2000/svg" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="var(--muted)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="8" x2="21" y1="6" y2="6"/><line x1="8" x2="21" y1="12" y2="12"/><line x1="8" x2="21" y1="18" y2="18"/><line x1="3" x2="3.01" y1="6" y2="6"/><line x1="3" x2="3.01" y1="12" y2="12"/><line x1="3" x2="3.01" y1="18" y2="18"/></svg>',
    "info":     '<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="var(--accent)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M12 16v-4"/><path d="M12 8h.01"/></svg>',
}

@st.cache_data(show_spinner=False)
def load_data():
    df = pd.read_csv(CLUSTERED_CSV)
    df["Cluster"] = df["Cluster"].astype(int)
    return df

def render():
    df = load_data()

    st.markdown("""
    <div class="page-header">
        <div class="page-title">Dataset Explorer</div>
        <div class="page-sub">Search, filter, sort, and export your customer data.</div>
    </div>
    """, unsafe_allow_html=True)

    # Controls
    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns([2.5, 1.5, 1.5, 1])
    with c1:
        search = st.text_input("Search", placeholder="Filter any column…",
                               label_visibility="collapsed")
    with c2:
        opts = ["All Clusters"] + [
            f"Cluster {c} — {CLUSTER_LABELS.get(c,'')}"
            for c in sorted(df["Cluster"].unique())
        ]
        cluster_filter = st.selectbox("Cluster", opts, label_visibility="collapsed")
    with c3:
        sort_col = st.selectbox("Sort by", df.columns.tolist(),
                                label_visibility="collapsed")
    with c4:
        asc = st.radio("Order", ["Asc", "Desc"], horizontal=True,
                       label_visibility="collapsed")
    st.markdown("</div>", unsafe_allow_html=True)

    # Apply filters
    filtered = df.copy()
    if cluster_filter != "All Clusters":
        c_id = int(cluster_filter.split()[1])
        filtered = filtered[filtered["Cluster"] == c_id]
    if search:
        mask = filtered.apply(
            lambda col: col.astype(str).str.contains(search, case=False, na=False)
        ).any(axis=1)
        filtered = filtered[mask]
    filtered = filtered.sort_values(by=sort_col, ascending=(asc == "Asc"))

    # Stats bar
    st.markdown(f"""
    <div style="display:flex;gap:1.5rem;align-items:center;
                padding:0.75rem 0;font-size:0.8rem;color:var(--muted);">
        <span style="display:flex;align-items:center;gap:0.4rem;">
            {SVG['rows']}
            <b style="color:var(--text);">{len(filtered):,}</b>&nbsp;rows
        </span>
        <span style="display:flex;align-items:center;gap:0.4rem;">
            {SVG['filter']}
            <b style="color:var(--text);">{filtered['Cluster'].nunique()}</b>&nbsp;clusters
        </span>
        <span style="display:flex;align-items:center;gap:0.4rem;">
            <b style="color:var(--text);">{len(filtered.columns)}</b>&nbsp;columns
        </span>
    </div>
    """, unsafe_allow_html=True)

    # Pagination
    PAGE_SIZE   = 20
    total_pages = max(1, (len(filtered) - 1) // PAGE_SIZE + 1)
    pc1, pc2, pc3 = st.columns([1,2,1])
    with pc2:
        page = st.number_input(f"Page (1–{total_pages})", min_value=1,
                               max_value=total_pages, value=1, step=1,
                               label_visibility="collapsed")

    start   = (page - 1) * PAGE_SIZE
    end     = start + PAGE_SIZE
    page_df = filtered.iloc[start:end].copy()
    page_df.insert(
        page_df.columns.get_loc("Cluster") + 1,
        "Segment",
        page_df["Cluster"].map(CLUSTER_LABELS),
    )

    st.dataframe(page_df, width='stretch', hide_index=True)
    st.caption(f"Rows {start+1}–{min(end,len(filtered))} of {len(filtered):,}")

    # Download
    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
    st.download_button(
        label="Download filtered CSV",
        data=filtered.to_csv(index=False).encode("utf-8"),
        file_name="segmentiq_filtered.csv",
        mime="text/csv",
    )

    # Column descriptions
    with st.expander("Column descriptions"):
        descs = {
            "credit_limit":       "Maximum credit limit assigned to the customer.",
            "num_cards_issued":   "Total number of cards issued to the customer.",
            "account_age":        "Number of years the customer has held the account.",
            "pin_age":            "Age of the customer's current PIN in years.",
            "has_chip":           "Whether the card has an EMV chip (1 = Yes, 0 = No).",
            "card_type":          "Encoded card type (e.g. debit, credit).",
            "card_on_dark_web":   "Whether the card has appeared on the dark web (1 = Yes).",
            "card_brand_encoded": "Encoded card brand (Visa, Mastercard, etc.).",
            "Cluster":            "KMeans cluster assignment (0–3).",
        }
        for col, desc in descs.items():
            if col in df.columns:
                st.markdown(
                    f"<div style='font-size:0.8rem;padding:0.3rem 0;"
                    f"border-bottom:1px solid var(--border);color:var(--soft);'>"
                    f"<code style='color:var(--accent);font-size:0.78rem;'>{col}</code>"
                    f"&nbsp;&nbsp;{desc}</div>",
                    unsafe_allow_html=True,
                )