import streamlit as st


def apply_lumo_styles():
    st.markdown("""
    <style>
    /* Hide Streamlit Branding */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}

    /* Clean Layout */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }

    /* SaaS Sidebar */
    [data-testid="stSidebar"] {
        background-color: #09090b;
        border-right: 1px solid #27272a;
    }

    /* Glassmorphism Cards */
    .lumo-card {
        background: rgba(24, 24, 27, 0.7);
        border: 1px solid #27272a;
        border-radius: 12px;
        padding: 24px;
        backdrop-filter: blur(10px);
        margin-bottom: 1rem;
    }

    /* Button overrides */
    div.stButton > button[kind="primary"] {
        background-color: #6366f1;
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: 600;
    }
    div.stButton > button[kind="primary"]:hover {
        background-color: #4f46e5;
    }

    /* Focus Mode full screen override */
    .focus-mode-active .block-container {
        max-width: 100% !important;
        padding: 0 !important;
    }
    </style>
    """, unsafe_allow_html=True)
