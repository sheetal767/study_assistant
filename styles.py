import streamlit as st


def apply_lumo_styles():
    st.markdown("""
    <style>
    /* Hide Streamlit branding (header stays so the sidebar toggle works on mobile) */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header[data-testid="stHeader"] {background: transparent;}

    /* ===== NORTHERN LIGHTS BACKGROUND ===== */
    .stApp {
        background-color: #050a14;
        background-image:
            radial-gradient(1.5px 1.5px at 12% 18%, rgba(255,255,255,0.9), transparent),
            radial-gradient(1px 1px at 28% 62%, rgba(255,255,255,0.7), transparent),
            radial-gradient(1.5px 1.5px at 45% 12%, rgba(255,255,255,0.8), transparent),
            radial-gradient(1px 1px at 63% 38%, rgba(255,255,255,0.6), transparent),
            radial-gradient(1.5px 1.5px at 78% 70%, rgba(255,255,255,0.8), transparent),
            radial-gradient(1px 1px at 90% 22%, rgba(255,255,255,0.7), transparent),
            radial-gradient(1px 1px at 8% 85%, rgba(255,255,255,0.6), transparent),
            radial-gradient(1.5px 1.5px at 55% 88%, rgba(255,255,255,0.7), transparent),
            linear-gradient(180deg, #050a14 0%, #0a1628 60%, #07111f 100%);
    }

    /* Green curtains */
    .stApp::before {
        content: "";
        position: fixed;
        inset: -20%;
        z-index: 0;
        pointer-events: none;
        background:
            radial-gradient(ellipse 35% 65% at 30% 35%, rgba(74, 222, 128, 0.38), transparent 70%),
            radial-gradient(ellipse 28% 75% at 58% 28%, rgba(52, 211, 153, 0.32), transparent 70%),
            radial-gradient(ellipse 32% 55% at 82% 45%, rgba(45, 212, 191, 0.26), transparent 70%);
        filter: blur(45px);
        animation: aurora-drift 18s ease-in-out infinite alternate;
    }

    /* Purple / blue glow */
    .stApp::after {
        content: "";
        position: fixed;
        inset: -20%;
        z-index: 0;
        pointer-events: none;
        background:
            radial-gradient(ellipse 38% 50% at 18% 60%, rgba(129, 140, 248, 0.24), transparent 70%),
            radial-gradient(ellipse 30% 60% at 72% 62%, rgba(167, 139, 250, 0.2), transparent 70%);
        filter: blur(55px);
        animation: aurora-sway 26s ease-in-out infinite alternate-reverse;
    }

    @keyframes aurora-drift {
        0%   { transform: translateX(-7%) skewX(-6deg) scaleY(1);    opacity: 0.7; }
        50%  { transform: translateX(4%)  skewX(5deg)  scaleY(1.15); opacity: 1; }
        100% { transform: translateX(9%)  skewX(-3deg) scaleY(0.95); opacity: 0.8; }
    }
    @keyframes aurora-sway {
        0%   { transform: translateX(6%)  translateY(-3%) scale(1);    opacity: 0.6; }
        50%  { transform: translateX(-5%) translateY(2%)  scale(1.12); opacity: 0.95; }
        100% { transform: translateX(-9%) translateY(-2%) scale(1.04); opacity: 0.7; }
    }

    /* Keep app content above the aurora layers */
    [data-testid="stAppViewContainer"],
    [data-testid="stMain"] {
        background: transparent !important;
        position: relative;
        z-index: 1;
    }
    [data-testid="stSidebar"] { position: relative; z-index: 2; }

    /* Respect "reduce motion" device setting */
    @media (prefers-reduced-motion: reduce) {
        .stApp::before, .stApp::after { animation: none; }
    }
    /* ===== END NORTHERN LIGHTS ===== */

    /* Clean Layout */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }

    /* SaaS Sidebar */
    [data-testid="stSidebar"] {
        background-color: rgba(9, 9, 11, 0.92);
        border-right: 1px solid #27272a;
    }
    [data-testid="stSidebar"] .block-container {
        padding-top: 1rem;
    }

    /* Glassmorphism Cards */
    .lumo-card {
        background: rgba(10, 16, 28, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 24px;
        backdrop-filter: blur(12px);
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

    /* Chat bubbles (a bit more solid so text stays readable over the aurora) */
    [data-testid="stChatMessage"] {
        background: rgba(8, 14, 26, 0.62);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 12px 16px;
        margin-bottom: 8px;
        backdrop-filter: blur(10px);
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
        .stApp::before, .stApp::after { filter: blur(30px); }
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
    background: rgba(10, 16, 28, 0.6);
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 14px;
    padding: 16px 20px;
    margin-bottom: 12px;
    backdrop-filter: blur(10px);
    transition: transform 0.15s ease, box-shadow 0.15s ease;
}
.sf-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 18px rgba(0, 0, 0, 0.3);
}
.sf-card h4 { margin: 0 0 6px 0; }
.sf-card p { margin: 0; opacity: 0.85; }
</style>
"""
