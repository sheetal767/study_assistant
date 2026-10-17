import streamlit as st


def _wave(color: str, alpha: float) -> str:
    """Seamlessly tiling aurora wave, as an inline SVG background."""
    svg = (
        "%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 800 300' preserveAspectRatio='none'%3E"
        "%3Cdefs%3E%3ClinearGradient id='g' x1='0' y1='0' x2='0' y2='1'%3E"
        f"%3Cstop offset='0.25' stop-color='{color}' stop-opacity='{alpha}'/%3E"
        f"%3Cstop offset='1' stop-color='{color}' stop-opacity='0'/%3E"
        "%3C/linearGradient%3E%3C/defs%3E"
        "%3Cpath d='M0 150 C133 50 267 50 400 150 S667 250 800 150 L800 300 L0 300 Z' fill='url(%23g)'/%3E"
        "%3C/svg%3E"
    )
    return f'url("data:image/svg+xml,{svg}")'


_TREE = "60,70 78,110 69,110 88,150 76,150 98,200 22,200 44,150 32,150 51,110 42,110"
_TREES = (
    'url("data:image/svg+xml,'
    "%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 600 220'%3E"
    "%3Cg fill='%2303080d'%3E"
    f"%3Cpolygon transform='translate(0 20)' points='{_TREE}'/%3E"
    f"%3Cpolygon transform='translate(72 -40) scale(1.3)' points='{_TREE}'/%3E"
    f"%3Cpolygon transform='translate(222 60) scale(0.8)' points='{_TREE}'/%3E"
    f"%3Cpolygon transform='translate(300 -80) scale(1.5)' points='{_TREE}'/%3E"
    f"%3Cpolygon transform='translate(430 20)' points='{_TREE}'/%3E"
    f"%3Cpolygon transform='translate(480 -10) scale(1.15)' points='{_TREE}'/%3E"
    "%3Crect y='212' width='600' height='8'/%3E"
    '%3C/g%3E%3C/svg%3E")'
)

_CSS = """
<style>
/* Hide Streamlit branding (header stays so the sidebar toggle works on mobile) */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}

/* ===== NORTHERN LIGHTS BACKGROUND ===== */
.stApp {
    background: linear-gradient(180deg, #02050b 0%, #04101a 45%, #06201f 100%) !important;
}
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
[data-testid="stHeader"] {
    background: transparent !important;
}
[data-testid="stAppViewContainer"] {
    position: relative;
    z-index: 0;
}

.aurora-bg {
    position: fixed;
    inset: 0;
    z-index: -1;
    pointer-events: none;
    overflow: hidden;
}

/* Twinkling stars */
.aurora-bg .stars {
    position: absolute;
    inset: 0;
    background-repeat: repeat;
}
.aurora-bg .s1 {
    background-image:
        radial-gradient(1.5px 1.5px at 20px 30px, #fff 0, transparent 100%),
        radial-gradient(1px 1px at 120px 80px, #fff 0, transparent 100%),
        radial-gradient(2px 2px at 220px 160px, #fff 0, transparent 100%),
        radial-gradient(1px 1px at 320px 40px, #fff 0, transparent 100%),
        radial-gradient(1.5px 1.5px at 420px 200px, #fff 0, transparent 100%),
        radial-gradient(1px 1px at 80px 260px, #fff 0, transparent 100%),
        radial-gradient(1.5px 1.5px at 260px 300px, #fff 0, transparent 100%),
        radial-gradient(1px 1px at 480px 120px, #fff 0, transparent 100%);
    background-size: 520px 340px;
    animation: star-twinkle 4s ease-in-out infinite alternate;
}
.aurora-bg .s2 {
    background-image:
        radial-gradient(1px 1px at 60px 50px, #cfe8ff 0, transparent 100%),
        radial-gradient(1.5px 1.5px at 170px 140px, #fff 0, transparent 100%),
        radial-gradient(1px 1px at 290px 90px, #cfe8ff 0, transparent 100%),
        radial-gradient(2px 2px at 360px 230px, #fff 0, transparent 100%),
        radial-gradient(1px 1px at 120px 250px, #cfe8ff 0, transparent 100%),
        radial-gradient(1.5px 1.5px at 390px 20px, #fff 0, transparent 100%);
    background-size: 430px 290px;
    animation: star-twinkle 6.5s ease-in-out infinite alternate-reverse;
    animation-delay: -2s;
}
@keyframes star-twinkle {
    from { opacity: 0.3; }
    to   { opacity: 1; }
}

/* Aurora waves */
.aurora-bg .sway {
    position: absolute;
    left: 0;
    right: 0;
}
.aurora-bg .sway.a { top: 4vh;  height: 62vh; animation: aurora-sway 16s ease-in-out infinite alternate; }
.aurora-bg .sway.b { top: 16vh; height: 55vh; animation: aurora-sway 22s ease-in-out infinite alternate-reverse; }
.aurora-bg .sway.c { top: 28vh; height: 50vh; animation: aurora-sway 28s ease-in-out infinite alternate; }
@keyframes aurora-sway {
    from { transform: translateY(-3vh) scaleY(0.92); }
    to   { transform: translateY(3vh)  scaleY(1.1); }
}

.aurora-bg .wave {
    position: absolute;
    top: 0;
    left: 0;
    height: 100%;
    width: calc(100% + var(--tile));
    background-repeat: repeat-x;
    background-size: var(--tile) 100%;
    filter: blur(6px);
    will-change: transform, opacity;
}
.aurora-bg .w1 {
    --tile: 900px;
    background-image: __WAVE1__;
    animation: wave-slide 70s linear infinite, wave-pulse 9s ease-in-out infinite alternate;
}
.aurora-bg .w2 {
    --tile: 700px;
    background-image: __WAVE2__;
    animation: wave-slide 55s linear infinite reverse, wave-pulse 12s ease-in-out infinite alternate-reverse;
}
.aurora-bg .w3 {
    --tile: 1100px;
    background-image: __WAVE3__;
    animation: wave-slide 90s linear infinite, wave-pulse 15s ease-in-out infinite alternate;
}
@keyframes wave-slide {
    from { transform: translateX(0); }
    to   { transform: translateX(calc(var(--tile) * -1)); }
}
@keyframes wave-pulse {
    from { opacity: 0.55; }
    to   { opacity: 1; }
}

/* Pine tree silhouettes */
.aurora-bg .trees {
    position: absolute;
    left: 0;
    right: 0;
    bottom: 0;
    height: 170px;
    background-image: __TREES__;
    background-repeat: repeat-x;
    background-position: bottom left;
    background-size: auto 100%;
}

@media (prefers-reduced-motion: reduce) {
    .aurora-bg .stars, .aurora-bg .sway, .aurora-bg .wave { animation: none !important; }
}
/* ===== END NORTHERN LIGHTS ===== */

/* Clean Layout */
.block-container {
    padding-top: 2.5rem;
    padding-bottom: 2rem;
    max-width: 1200px;
}

/* SaaS Sidebar */
[data-testid="stSidebar"] {
    background-color: rgba(5, 10, 18, 0.88);
    border-right: 1px solid rgba(255, 255, 255, 0.08);
    backdrop-filter: blur(12px);
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
[data-testid="stSidebar"] div.stButton > button {
    justify-content: flex-start;
}
[data-testid="stSidebar"] div.stButton > button > div,
[data-testid="stSidebar"] div.stButton > button p {
    justify-content: flex-start;
    text-align: left;
    width: 100%;
}
[data-testid="stSidebar"] div.stButton > button[kind="secondary"] {
    background: transparent;
    border: 1px solid transparent;
}
[data-testid="stSidebar"] div.stButton > button[kind="secondary"]:hover {
    background: rgba(99, 102, 241, 0.14);
    border-color: rgba(99, 102, 241, 0.4);
}

/* Floating timer button (the clock at the top) */
div[data-testid="stPopover"] {
    position: fixed;
    top: 0.6rem;
    right: 10rem;
    z-index: 1000000;
    width: auto;
}
div[data-testid="stPopover"] button {
    border-radius: 999px;
    background: rgba(10, 16, 28, 0.7);
    border: 1px solid rgba(255, 255, 255, 0.2);
    backdrop-filter: blur(10px);
    padding: 0.2rem 0.9rem;
}
div[data-testid="stPopover"] button:hover {
    border-color: rgba(99, 102, 241, 0.7);
}
[data-testid="stElementContainer"]:has(> [data-testid="stPopover"]) {
    height: 0;
    min-height: 0;
    margin-bottom: -1rem;
}
div[data-testid="stPopoverBody"] {
    min-width: min(320px, 90vw);
    background: rgba(8, 14, 26, 0.92);
    backdrop-filter: blur(14px);
}

/* Inputs */
div[data-baseweb="input"] > div,
div[data-baseweb="select"] > div {
    border-radius: 8px;
}

/* Chat bubbles (slightly solid so text stays readable over the aurora) */
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
        padding-top: 2.5rem;
    }
    .sf-card { padding: 12px 14px; }
    .aurora-bg .wave { filter: blur(4px); }
    .aurora-bg .trees { height: 120px; }
}

/* Focus Mode full screen override */
.focus-mode-active .block-container {
    max-width: 100% !important;
    padding: 0 !important;
}
</style>
"""

_AURORA_HTML = """
<div class="aurora-bg">
<div class="stars s1"></div>
<div class="stars s2"></div>
<div class="sway a"><div class="wave w1"></div></div>
<div class="sway b"><div class="wave w2"></div></div>
<div class="sway c"><div class="wave w3"></div></div>
<div class="trees"></div>
</div>
"""


def apply_lumo_styles():
    css = (
        _CSS
        .replace("__WAVE1__", _wave("%234ade80", 0.55))
        .replace("__WAVE2__", _wave("%232dd4bf", 0.45))
        .replace("__WAVE3__", _wave("%23a78bfa", 0.38))
        .replace("__TREES__", _TREES)
    )
    try:
        st.html(_AURORA_HTML + css)
    except AttributeError:
        st.markdown(css + _AURORA_HTML, unsafe_allow_html=True)


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
