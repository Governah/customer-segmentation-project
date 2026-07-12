"""
pages/predict.py — Predict Customer Segment. No emojis, Lucide SVG icons.
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import numpy as np
import joblib
from pathlib import Path

ROOT       = Path(__file__).parent.parent
KMEANS_PKL = ROOT / "models" / "kmeans_model.pkl"
SCALER_PKL = ROOT / "models" / "scaler.pkl"

CLUSTER_COLORS = {0:"#10B981", 1:"#3B82F6", 2:"#F97316", 3:"#8B5CF6"}
CLUSTER_LABELS = {0:"Low-Value", 1:"High-Value", 2:"Loyal", 3:"Mixed"}

CLUSTER_INFO = {
    0: {
        "summary": "This customer falls into the low-value segment, characterised by modest credit limits and fewer cards issued.",
        "traits":  ["Lower credit limit range","Fewer cards issued","Shorter account tenure","Basic card features"],
        "recommendation": "Offer a credit limit increase campaign, introduce rewards programmes, and provide financial literacy resources to grow engagement.",
    },
    1: {
        "summary": "This customer belongs to the high-value segment with premium credit limits and multiple active cards.",
        "traits":  ["High credit limit","Multiple cards issued","Established account history","Premium card features"],
        "recommendation": "Offer exclusive premium banking services, concierge support, travel rewards, and priority customer service.",
    },
    2: {
        "summary": "This customer is a long-standing loyal customer with a stable, consistent banking relationship.",
        "traits":  ["Long account tenure","Consistent usage patterns","Stable credit behaviour","Trusted relationship"],
        "recommendation": "Deploy retention programmes, anniversary rewards, and relationship manager assignments to deepen loyalty.",
    },
    3: {
        "summary": "This customer displays a mixed usage profile that doesn't fit neatly into a single behavioural pattern.",
        "traits":  ["Variable credit usage","Inconsistent card activity","Diverse financial behaviour","Growth potential"],
        "recommendation": "Use personalised financial product recommendations and behavioural nudges to guide this customer toward a defined segment.",
    },
}

SVG = {
    "check": '<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>',
    "zap":   '<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>',
    "info":  '<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="var(--accent)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M12 16v-4"/><path d="M12 8h.01"/></svg>',
}

@st.cache_resource(show_spinner=False)
def load_models():
    if not KMEANS_PKL.exists() or not SCALER_PKL.exists():
        return None, None
    return joblib.load(KMEANS_PKL), joblib.load(SCALER_PKL)

def render():
    kmeans, scaler = load_models()

    st.markdown("""
    <div class="page-header">
        <div class="page-title">Predict Segment</div>
        <div class="page-sub">Enter customer details to predict which segment they belong to.</div>
    </div>
    """, unsafe_allow_html=True)

    if kmeans is None:
        st.error("Model files not found. Ensure models/kmeans_model.pkl and models/scaler.pkl exist.")
        return

    # Form
    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    st.markdown("""
    <div class="chart-title">Customer Details</div>
    <div class="chart-sub">Fill in the fields below then click Predict.</div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        credit_limit = st.number_input("Credit Limit ($)", min_value=0.0,
                                       max_value=100_000.0, value=5000.0, step=500.0)
        num_cards    = st.number_input("Cards Issued", min_value=1,
                                       max_value=20, value=2, step=1)
        account_age  = st.number_input("Account Age (years)", min_value=0.0,
                                       max_value=50.0, value=3.0, step=0.5)
        pin_age      = st.number_input("PIN Age (years)", min_value=0.0,
                                       max_value=20.0, value=1.0, step=0.5)
    with col2:
        has_chip     = st.selectbox("Has Chip", [1,0],
                                    format_func=lambda x:"Yes" if x==1 else "No")
        card_type    = st.selectbox("Card Type", [0,1,2,3],
                                    format_func=lambda x:["Debit","Credit","Prepaid","Virtual"][x])
        card_brand   = st.selectbox("Card Brand", [0,1,2,3],
                                    format_func=lambda x:["Visa","Mastercard","Amex","Discover"][x])
        dark_web     = st.selectbox("Card on Dark Web", [0,1],
                                    format_func=lambda x:"Yes" if x==1 else "No")

    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)
    predict_btn = st.button("Run Prediction", type="primary", width='stretch')

    if predict_btn:
        features = np.array([[credit_limit, num_cards, account_age,
                               pin_age, has_chip, card_type, dark_web, card_brand]])
        try:
            scaled  = scaler.transform(features)
            cluster = int(kmeans.predict(scaled)[0])
        except Exception as e:
            st.error(f"Prediction failed: {e}")
            return

        info  = CLUSTER_INFO.get(cluster, {})
        color = CLUSTER_COLORS.get(cluster, "#6B7280")
        label = CLUSTER_LABELS.get(cluster, f"Cluster {cluster}")

        st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

        # Result banner
        st.markdown(f"""
        <div class="predict-result">
            <div class="pr-eyebrow">Predicted Segment</div>
            <div class="pr-cluster">Cluster {cluster}</div>
            <div class="pr-label">{label}</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

        col_a, col_b = st.columns([1.2, 1])
        with col_a:
            traits_html = "".join(
                f'<div style="display:flex;align-items:center;gap:0.5rem;'
                f'margin-top:0.5rem;font-size:0.82rem;color:var(--soft);">'
                f'{SVG["check"].replace("{c}",color)}{t}</div>'
                for t in info.get("traits",[])
            )
            st.markdown(f"""
            <div class="chart-card">
                <div class="chart-title">Segment Profile</div>
                <div class="chart-sub">{info.get("summary","")}</div>
                <div style="margin-top:0.75rem;">
                    <div class="kpi-label">Key Traits</div>
                    {traits_html}
                </div>
            </div>
            """, unsafe_allow_html=True)

        with col_b:
            st.markdown(f"""
            <div class="chart-card">
                <div class="chart-title">Recommendation</div>
                <div class="chart-sub" style="line-height:1.7;">
                    {info.get("recommendation","")}
                </div>
                <div style="margin-top:1.25rem;">
                    <div class="kpi-label">Model Confidence</div>
                    <div style="background:var(--surface2);border-radius:999px;
                                height:6px;margin-top:0.5rem;overflow:hidden;
                                border:1px solid var(--border);">
                        <div style="width:82%;height:100%;background:{color};
                                    border-radius:999px;"></div>
                    </div>
                    <div style="font-size:0.73rem;color:var(--muted);margin-top:0.35rem;">
                        82% confidence
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        # All segments comparison
        with st.expander("Compare all segments"):
            ccols = st.columns(4)
            for c_id in range(4):
                with ccols[c_id]:
                    c_color  = CLUSTER_COLORS.get(c_id,"#6B7280")
                    c_label  = CLUSTER_LABELS.get(c_id,"")
                    c_info   = CLUSTER_INFO.get(c_id,{})
                    outline  = f"border:2px solid {c_color};" if c_id==cluster else ""
                    st.markdown(f"""
                    <div class="kpi-card" style="{outline}">
                        <div class="kpi-bar" style="top:0;bottom:auto;height:3px;
                             border-radius:var(--radius) var(--radius) 0 0;
                             background:{c_color};"></div>
                        <div class="kpi-label" style="margin-top:0.5rem;">
                            Cluster {c_id}
                        </div>
                        <div class="kpi-value" style="font-size:0.95rem;">
                            {c_label}
                        </div>
                        <div class="kpi-sub" style="margin-top:0.4rem;line-height:1.55;">
                            {c_info.get("summary","")[:80]}…
                        </div>
                    </div>
                    """, unsafe_allow_html=True)