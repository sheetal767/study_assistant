import json
import streamlit as st
import streamlit.components.v1 as components

def _wave(color: str, alpha: float) -> str:
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

_AURORA_CSS = """
<style>
html { background: #02050b !important; }
body { background: transparent !important; }
.stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"], [data-testid="stHeader"] { background: transparent !important; }
.aurora-bg { position: fixed; inset: 0; z-index: -1; pointer-events: none; overflow: hidden; background: linear-gradient(180deg, #02050b 0%, #04101a 45%, #06201f 100%); }
.aurora-bg .stars { position: absolute; inset: 0; background-repeat: repeat; }
.aurora-bg .s1 { background-image: radial-gradient(1.5px 1.5px at 20px 30px, #fff 0, transparent 100%), radial-gradient(1px 1px at 120px 80px, #fff 0, transparent 100%), radial-gradient(2px 2px at 220px 160px, #fff 0, transparent 100%), radial-gradient(1px 1px at 320px 40px, #fff 0, transparent 100%), radial-gradient(1.5px 1.5px at 420px 200px, #fff 0, transparent 100%), radial-gradient(1px 1px at 80px 260px, #fff 0, transparent 100%), radial-gradient(1.5px 1.5px at 260px 300px, #fff 0, transparent 100%), radial-gradient(1px 1px at 480px 120px, #fff 0, transparent 100%); background-size: 520px 340px; animation: star-twinkle 4s ease-in-out infinite alternate; }
.aurora-bg .s2 { background-image: radial-gradient(1px 1px at 60px 50px, #cfe8ff 0, transparent 100%), radial-gradient(1.5px 1.5px at 170px 140px, #fff 0, transparent 100%), radial-gradient(1px 1px at 290px 90px, #cfe8ff 0, transparent 100%), radial-gradient(2px 2px at 360px 230px, #fff 0, transparent 100%), radial-gradient(1px 1px at 120px 250px, #cfe8ff 0, transparent 100%), radial-gradient(1.5px 1.5px at 390px 20px, #fff 0, transparent 100%); background-size: 430px 290px; animation: star-twinkle 6.5s ease-in-out infinite alternate-reverse; animation-delay: -2s; }
@keyframes star-twinkle { from { opacity: 0.3; } to { opacity: 1; } }
.aurora-bg .sway { position: absolute; left: 0; right: 0; }
.aurora-bg .sway.a { top: 4vh;  height: 62vh; animation: aurora-sway 16s ease-in-out infinite alternate; }
.aurora-bg .sway.b { top: 16vh; height: 55vh; animation: aurora-sway 22s ease-in-out infinite alternate-reverse; }
.aurora-bg .sway.c { top: 28vh; height: 50vh; animation: aurora-sway 28s ease-in-out infinite alternate; }
@keyframes aurora-sway { from { transform: translateY(-3vh) scaleY(0.92); } to { transform: translateY(3vh) scaleY(1.1); } }
.aurora-bg .wave { position: absolute; top: 0; left: 0; height: 100%; width: calc(100% + var(--tile)); background-repeat: repeat-x; background-size: var(--tile) 100%; filter: blur(6px); will-change: transform, opacity; }
.aurora-bg .w1 { --tile: 900px; background-image: __WAVE1__; animation: wave-slide 70s linear infinite, wave-pulse 9s ease-in-out infinite alternate; }
.aurora-bg .w2 { --tile: 700px; background-image: __WAVE2__; animation: wave-slide 55s linear infinite reverse, wave-pulse 12s ease-in-out infinite alternate-reverse; }
.aurora-bg .w3 { --tile: 1100px; background-image: __WAVE3__; animation: wave-slide 90s linear infinite, wave-pulse 15s ease-in-out infinite alternate; }
@keyframes wave-slide { from { transform: translateX(0); } to { transform: translateX(calc(var(--tile) * -1)); } }
@keyframes wave-pulse { from { opacity: 0.55; } to { opacity: 1; } }
.aurora-bg .trees { position: absolute; left: 0; right: 0; bottom: 0; height: 170px; background-image: __TREES__; background-repeat: repeat-x; background-position: bottom left; background-size: auto 100%; }
@media (prefers-reduced-motion: reduce) { .aurora-bg .stars, .aurora-bg .sway, .aurora-bg .wave { animation: none !important; } }
</style>
"""
_AURORA_MOBILE_CSS = "<style>@media (max-width: 640px) { .aurora-bg .wave { filter: blur(4px); } .aurora-bg .trees { height: 120px; } }</style>"
_AURORA_HTML = '<div class="aurora-bg"><div class="stars s1"></div><div class="stars s2"></div><div class="sway a"><div class="wave w1"></div></div><div class="sway b"><div class="wave w2"></div></div><div class="sway c"><div class="wave w3"></div></div><div class="trees"></div></div>'
_FONT_LINK = '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Newsreader:wght@500;600&display=swap">'

_THEME_CSS = """
<style>
#MainMenu {visibility: hidden;} footer {visibility: hidden;}
:root {
    --lumo-bg: #02050b; --lumo-plate: rgba(2, 5, 11, 0.72); --lumo-plate-strong: rgba(2, 5, 11, 0.88);
    --lumo-sidebar: rgba(2, 5, 11, 0.80); --lumo-border: #1c2536; --lumo-border-input: #6b7894;
    --lumo-accent: #6366f1; --lumo-accent-fill: #4f46e5; --lumo-accent-fill-hover: #4338ca;
    --lumo-accent-text: #818cf8; --lumo-text: #e8ecf5; --lumo-muted: #a5b0c6;
    --lumo-radius: 8px; --lumo-font-head: 'Newsreader', Georgia, 'Times New Roman', serif;
    --lumo-aurora-line: linear-gradient(90deg, #4ade80 0%, #2dd4bf 50%, #a78bfa 100%);
}
.stApp { color: var(--lumo-text); }
.block-container { max-width: 760px; margin-left: auto; margin-right: auto; padding: 2.5rem 1.5rem 2rem; }
[data-testid="stSidebar"] { background: var(--lumo-sidebar) !important; border-right: 1px solid var(--lumo-border); }
.stApp h1, .stApp h2, .stApp h3, .stApp h4 { font-family: var(--lumo-font-head) !important; font-weight: 600; color: var(--lumo-text); letter-spacing: -0.01em;}

/* Buttons */
.stApp :is(button[kind="primary"]) { background: var(--lumo-accent-fill) !important; color: #ffffff !important; border-radius: var(--lumo-radius); border: none !important; transition: all 0.15s ease; box-shadow: 0 4px 14px rgba(79, 70, 229, 0.3) !important;}
.stApp :is(button[kind="primary"]):hover { transform: translateY(-2px); background: var(--lumo-accent-fill-hover) !important; }
.stApp :is(button[kind="secondary"]) { background: var(--lumo-plate) !important; color: var(--lumo-text) !important; border: 1px solid var(--lumo-border) !important; border-radius: var(--lumo-radius); }

/* Glass Surfaces */
.lumo-card, [data-testid="stChatMessage"], [data-testid="stForm"], [data-testid="stVerticalBlockBorderWrapper"] {
    background: rgba(6, 12, 22, 0.66) !important;
    -webkit-backdrop-filter: blur(14px) saturate(140%); backdrop-filter: blur(14px) saturate(140%);
    border: 1px solid rgba(148, 163, 255, 0.18) !important; border-radius: 12px !important;
    box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.05), 0 10px 30px rgba(0,0,0,0.3) !important;
}

/* Chat Styling */
[data-testid="stChatMessage"] { padding: 14px 18px; margin-bottom: 12px; }
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) { background: linear-gradient(135deg, rgba(79, 70, 229, 0.24), rgba(6, 12, 22, 0.70)) !important; border-left: 3px solid var(--lumo-accent-text) !important; }
[data-testid="stChatInput"] { border-radius: 16px !important; background: var(--lumo-plate-strong) !important; border: 1px solid var(--lumo-border-input) !important; }

/* Mac-Style Code Blocks */
[data-testid="stMarkdownContainer"] pre { background: #09111f !important; border: 1px solid rgba(148, 163, 255, 0.18) !important; border-radius: 12px !important; padding: 1rem !important; box-shadow: inset 0 2px 10px rgba(0,0,0,0.5); }
[data-testid="stMarkdownContainer"] code { color: #a78bfa !important; background: rgba(167, 139, 250, 0.1) !important; padding: 2px 6px !important; border-radius: 6px !important; }
[data-testid="stMarkdownContainer"] pre code { color: #e8ecf5 !important; background: transparent !important; padding: 0 !important; }

/* Custom Spinner */
.stSpinner > div > div { border-color: var(--lumo-accent-text) !important; border-bottom-color: transparent !important; }
.stSpinner span { color: var(--lumo-accent-text) !important; font-family: var(--lumo-font-head) !important; font-size: 1rem !important; }

/* Radio/Quiz Options */
div[role="radiogroup"] > label { padding: 10px 14px; transition: all 0.2s ease; border-radius: 8px; border: 1px solid rgba(148, 163, 255, 0.18);}
div[role="radiogroup"] > label:has(input:checked) { box-shadow: inset 3px 0 0 var(--lumo-accent-text); background: rgba(99, 102, 241, 0.15);}

/* Ring Stats */
.lumo-ring-wrap { display: flex; align-items: center; gap: 24px; padding: 20px 24px; margin: 4px 0 16px; background: rgba(6, 12, 22, 0.66); border: 1px solid rgba(148, 163, 255, 0.18); border-radius: var(--lumo-radius); box-shadow: inset 0 1px 0 rgba(255,255,255,0.05), 0 10px 30px rgba(0,0,0,0.3); backdrop-filter: blur(14px); }
.lumo-ring { --pct: 0; flex: none; width: 128px; height: 128px; border-radius: 50%; display: grid; place-items: center; background: conic-gradient(#4ade80 0%, #2dd4bf calc(var(--pct) * 0.5%), #a78bfa calc(var(--pct) * 1%), rgba(255, 255, 255, 0.09) calc(var(--pct) * 1%)); filter: drop-shadow(0 0 16px rgba(45, 212, 191, 0.30)); }
.lumo-ring-inner { width: 100px; height: 100px; border-radius: 50%; background: #060c17; display: flex; flex-direction: column; align-items: center; justify-content: center; }
.lumo-ring-num { font-family: var(--lumo-font-head); font-size: 1.9rem; font-weight: 600; line-height: 1; }
.lumo-ring-label { font-size: 0.72rem; color: var(--lumo-muted); margin-top: 4px; }
.lumo-ring-title { font-family: var(--lumo-font-head); font-size: 1.5rem; font-weight: 600; margin-bottom: 4px; }
.lumo-ring-side p { margin: 0; color: var(--lumo-muted); }

/* Bottom Nav for Mobile */
.mobile-nav-container { display: none !important; }
@media (max-width: 768px) {
    .mobile-nav-container { display: flex !important; position: fixed !important; bottom: 0 !important; left: 0 !important; right: 0 !important; height: max(72px, env(safe-area-inset-bottom)) !important; background: rgba(6, 12, 22, 0.85) !important; backdrop-filter: blur(20px) !important; -webkit-backdrop-filter: blur(20px) !important; border-top: 1px solid rgba(148, 163, 255, 0.18) !important; z-index: 999999 !important; padding-bottom: env(safe-area-inset-bottom) !important; justify-content: space-around !important; align-items: center !important; box-shadow: 0 -10px 40px rgba(0,0,0,0.5); }
    .mobile-nav-container button { background: transparent !important; border: none !important; box-shadow: none !important; color: var(--lumo-muted) !important; display: flex; flex-direction: column; align-items: center; gap: 4px; font-size: 0.65rem; }
    .mobile-nav-container button:hover, .mobile-nav-container button:active { color: var(--lumo-accent-text) !important; transform: scale(1.1); }
    .block-container { padding-bottom: 100px !important; }
}
</style>
"""

_EARLY_CSS = "<style>html{background:#02050b!important}.stApp,[data-testid=\"stAppViewContainer\"],[data-testid=\"stMain\"],[data-testid=\"stHeader\"]{background:transparent!important}</style>"
CARD_CSS = "<style></style>"

def apply_lumo_styles():
    st.markdown(_EARLY_CSS, unsafe_allow_html=True)
    aurora_css = _AURORA_CSS.replace("__WAVE1__", _wave("%234ade80", 0.55)).replace("__WAVE2__", _wave("%232dd4bf", 0.45)).replace("__WAVE3__", _wave("%23a78bfa", 0.38)).replace("__TREES__", _TREES)
    payload = json.dumps(_FONT_LINK + _AURORA_HTML + aurora_css + _AURORA_MOBILE_CSS + _THEME_CSS)
    components.html(
        f"<script>(function(){{ var d = window.parent.document; var old = d.getElementById('lumo-aurora'); if(old) old.remove(); var holder = d.createElement('div'); holder.id = 'lumo-aurora'; holder.innerHTML = {payload}; d.body.appendChild(holder); }})();</script>",
        height=0,
    )
