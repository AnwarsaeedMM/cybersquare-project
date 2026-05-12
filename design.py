import streamlit as st

def load_css():
    st.markdown("""
    <style>
    .kpi-card {
        background: linear-gradient(135deg,#1e293b,#0f172a);
        padding: 18px;
        border-radius: 12px;
        color: white;
        box-shadow: 0 8px 25px rgba(0,0,0,0.2);
    }
    .kpi-title {
        font-size: 14px;
        color: #94a3b8;
    }
    .kpi-value {
        font-size: 28px;
        font-weight: bold;
    }
    .section-title {
        font-size: 22px;
        font-weight: 700;
        margin-top: 20px;
    }
    </style>
    """, unsafe_allow_html=True)


def kpi(title, value):
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">{title}</div>
        <div class="kpi-value">{value}</div>
    </div>
    """, unsafe_allow_html=True)