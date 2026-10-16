import streamlit as st


def apply_lumo_styles():
    st.markdown("""
    <style>
    /* Hide Streamlit branding (header stays so the sidebar toggle works on mobile) */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header[data-testid="stHeader"] {background: transparent;}

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
    [data-testid="stSidebar"] .block-container {
        padding-top: 1rem;
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

    /* Buttons: base */
    div.stButton > button {
        border-radius: 8px;
        font-weight: 500;
        transition: all 0.15s ease;
    }
    div.stButton > button:hover {
        transform: translateY(-1px);
    }

    /* Buttons: primary (also the active sidebar page) */
    div.stButton > button[kind="primary"] {
        background-color: #6366f1;
        color: white;
        border: none;
        font-weight: 600;
    }
    div.stButton > button[kind="primary"]:hover {
        background-color: #4f46e5;
    }

    /* Sidebar nav buttons: left aligned, subtle */
    [data-testid="stSidebar"] div.stButton > button[kind="secondary"] {
        background: transparent;
        border: 1px solid transparent;
        justify-content: flex-start;
        text-align: left;
    }
    [data-testid="stSidebar"] div.stButton > button[kind="secondary"]:hover {
        background: rgba(99, 102, 241, 0.12);
        border-color: rgba(99, 102, 241, 0.35);
    }
    [data-testid="stSidebar"] div.stButton > button[kind="primary"] {
        justify-content: flex-start;
        text-align: left;
    }

    /* Inputs */
    div[data-baseweb="input"] > div,
    div[data-baseweb="select"] > div {
        border-radius: 8px;
    }

    /* Chat bubbles */
    [data-testid="stChatMessage"] {
        background: rgba(24, 24, 27, 0.55);
        border: 1px solid #27272a;
        border-radius: 12px;
        padding: 12px 16px;
        margin-bottom: 8px;
    }

    /* Tabs */
    button[data-baseweb="tab"] {
        font-weight: 600;
    }

    /* Mobile */
    @media (max-width: 640px) {
        .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
            padding-top: 1rem;
        }
        .sf-card { padding: 12px 14px; }
    }

    /* Focus Mode full screen override */
    .focus-mode-active .block-container {
        max-width: 100% !important;
        padding: 0 !important;
    }
    </style>
    """, unsafe_allow_html=True)


CARD_CSS = """
<style>
.sf-card {
    background: rgba(128, 128, 128, 0.08);
    border: 1px solid rgba(128, 128, 128, 0.2);
    border-radius: 14px;
    padding: 16px 20px;
    margin-bottom: 12px;
    transition: transform 0.15s ease, box-shadow 0.15s ease;
}
.sf-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 18px rgba(0, 0, 0, 0.15);
}
.sf-card h4 { margin: 0 0 6px 0; }
.sf-card p { margin: 0; opacity: 0.85; }
</style>
"""
