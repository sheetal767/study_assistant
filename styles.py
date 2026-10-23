import json
import streamlit as st
import streamlit.components.v1 as components


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

# ---------------------------------------------------------------------------
# AURORA LIGHTS: copied unchanged from the original file (waves, stars, forest,
# timings, colors, stacking). Do not edit without a design decision.
# ---------------------------------------------------------------------------
_AURORA_CSS = """
<style>
/* ===== NORTHERN LIGHTS BACKGROUND ===== */
html { background: #02050b !important; }
body { background: transparent !important; }
.stApp,
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
[data-testid="stHeader"] {
    background: transparent !important;
}

.aurora-bg {
    position: fixed;
    inset: 0;
    z-index: -1;
    pointer-events: none;
    overflow: hidden;
    background: linear-gradient(180deg, #02050b 0%, #04101a 45%, #06201f 100%);
}
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

.aurora-bg .sway { position: absolute; left: 0; right: 0; }
.aurora-bg .sway.a { top: 4vh;  height: 62vh; animation: aurora-sway 16s ease-in-out infinite alternate; }
.aurora-bg .sway.b { top: 16vh; height: 55vh; animation: aurora-sway 22s ease-in-out infinite alternate-reverse; }
.aurora-bg .sway.c { top: 28vh; height: 50vh; animation: aurora-sway 28s ease-in-out infinite alternate; }
@keyframes aurora-sway {
    from { transform: translateY(-3vh) scaleY(0.92); }
    to   { transform: translateY(3vh) scaleY(1.1); }
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
</style>
"""

# Phone-size Aurora tweaks, also unchanged from the original.
_AURORA_MOBILE_CSS = """
<style>
@media (max-width: 640px) {
    .aurora-bg .wave { filter: blur(4px); }
    .aurora-bg .trees { height: 120px; }
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

# ---------------------------------------------------------------------------
# APP THEME (Lumo: indigo accent, frosted-glass surfaces, Newsreader headings)
# Layered over the Aurora. Nothing below changes the Aurora's look or motion.
# Body text keeps Streamlit's own Source Sans (see .streamlit/config.toml).
# ---------------------------------------------------------------------------
_HOLDER_VERSION = "6"  # bump this to make already-open tabs replace old CSS

_FONT_LINK = (
    '<link rel="stylesheet" '
    'href="https://fonts.googleapis.com/css2?family=Newsreader:wght@500;600&display=swap">'
)

_THEME_CSS = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}

/* ===== TOKENS ===== */
:root {
    --lumo-bg: #02050b;
    --lumo-plate: rgba(2, 5, 11, 0.72);
    --lumo-plate-strong: rgba(2, 5, 11, 0.88);
    --lumo-sidebar: rgba(2, 5, 11, 0.80);
    --lumo-border: #1c2536;
    --lumo-border-input: #6b7894;
    --lumo-accent: #6366f1;
    --lumo-accent-fill: #4f46e5;
    --lumo-accent-fill-hover: #4338ca;
    --lumo-accent-text: #818cf8;
    --lumo-text: #e8ecf5;
    --lumo-muted: #a5b0c6;
    --lumo-ok: #4ade80;
    --lumo-warn: #fbbf24;
    --lumo-err: #f87171;
    --lumo-radius: 8px;
    --lumo-font-head: 'Newsreader', Georgia, 'Times New Roman', serif;
}

/* ===== LAYOUT ===== */
.stApp { color: var(--lumo-text); }
.block-container {
    max-width: 760px;               /* centred reading column (app.py can widen per page) */
    margin-left: auto;
    margin-right: auto;
    padding: 2.5rem 1.5rem 2rem;
}
[data-testid="stSidebar"] {
    background: var(--lumo-sidebar) !important;
    border-right: 1px solid var(--lumo-border);
}
[data-testid="stSidebar"] .block-container { padding-top: 1rem; }

/* ===== TYPE ===== */
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li {
    font-size: 1.0625rem;
    line-height: 1.65;
    max-width: 72ch;
}
[data-testid="stWidgetLabel"] p {
    font-size: 0.875rem !important;
    font-weight: 600;
    line-height: 1.43;
}
[data-testid="stCaptionContainer"],
[data-testid="stCaptionContainer"] p {
    color: var(--lumo-muted) !important;
    font-size: 0.875rem !important;
    line-height: 1.43 !important;
}
.stApp h1, .stApp h2, .stApp h3, .stApp h4 {
    font-family: var(--lumo-font-head) !important;
    font-weight: 600;
    letter-spacing: -0.01em;
    color: var(--lumo-text);
}
.stApp h1:not([style*="font-size"]) {
    font-size: 2.25rem !important;
    line-height: 1.17 !important;
    letter-spacing: -0.02em;
}
.stApp h2, .stApp h3, .stApp h4 {
    font-size: 1.375rem !important;
    line-height: 1.27 !important;
}
/* Timer digits (headings with their own inline size): plain sans, aligned numerals */
.stApp h1[style*="font-size"] {
    font-family: inherit !important;
    font-variant-numeric: tabular-nums;
    font-weight: 600;
}
[data-testid="stMarkdownContainer"] a { color: var(--lumo-accent-text); }

/* Page header (ui.page_header): subtitle sits on a flat plate so it stays readable over the Aurora */
.stApp h1[style*="margin-bottom"] { padding: 0.25rem 0 0.25rem; }
[data-testid="stMarkdownContainer"] h1[style*="margin-bottom"] + p {
    display: inline-block;
    background: var(--lumo-plate);
    border-radius: var(--lumo-radius);
    padding: 4px 10px;
    margin: 4px 0 16px 0 !important;
}

/* Page headers are centred in the column, like the Claude home screen */
[data-testid="stMarkdownContainer"]:has(> h1[style*="margin-bottom"]),
[data-testid="stMarkdownContainer"]:has(h1[style*="margin-bottom"]) { text-align: center; }
[data-testid="stMarkdownContainer"] h1[style*="margin-bottom"] + p { margin-left: auto; margin-right: auto; }

/* Chat box: compact, rounded, same width as the column */
[data-testid="stChatInput"] {
    border-radius: 16px !important;
    max-width: 100%;
    background: var(--lumo-plate-strong) !important;
    border: 1px solid var(--lumo-border-input) !important;
}
[data-testid="stChatInput"] > div,
[data-testid="stChatInput"] div[data-baseweb] {
    background: transparent !important;
    border: none !important;
    border-radius: 16px !important;
}
[data-testid="stChatInput"] textarea { font-size: 1rem !important; }

/* Opening screen helpers (used by app.py) */
.lumo-login-hero { text-align: center; margin: 9vh 0 24px 0; }
.lumo-login-hero .lumo-hero-title { text-align: center; }
.lumo-login-hero .lumo-card { margin: 0 auto; max-width: 100%; }
.lumo-login-hero .lumo-lede { text-align: center; margin: 0 auto; }
.lumo-hero-title {
    font-family: var(--lumo-font-head);
    font-weight: 600;
    font-size: 3.5rem;
    line-height: 1.07;
    letter-spacing: -0.02em;
    margin: 0 0 12px 0;
    color: var(--lumo-text);
}
.lumo-lede {
    font-size: 1.0625rem;
    line-height: 1.65;
    max-width: 60ch;
    color: var(--lumo-text);
    margin: 0;
}

/* ===== SURFACES (base; the POLISH LAYER at the end adds the glass finish) ===== */
.lumo-card, .sf-card,
[data-testid="stChatMessage"],
[data-testid="stExpander"],
[data-testid="stForm"],
[data-testid="stVerticalBlockBorderWrapper"] {
    background: var(--lumo-plate);
    border: 1px solid var(--lumo-border);
    border-radius: var(--lumo-radius);
}
.lumo-card, .sf-card { padding: 16px 20px; margin-bottom: 12px; }
.lumo-card { padding: 24px; }
.sf-card h4 { margin: 0 0 6px 0; }
.sf-card p { margin: 0; color: var(--lumo-muted); }
[data-testid="stChatMessage"] {
    padding: 12px 16px;
    margin-bottom: 8px;
    max-width: 760px;
}
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]),
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
    border-left: 3px solid var(--lumo-accent-text);
}
[data-testid="stExpander"] details { border: none; }
[data-testid="stFileUploaderDropzone"] {
    background: var(--lumo-plate);
    border: 1px dashed var(--lumo-border-input);
    border-radius: var(--lumo-radius);
}
[data-testid="stAlert"],
[data-testid="stAlertContainer"] {
    border-radius: var(--lumo-radius);
    background-image: linear-gradient(var(--lumo-plate), var(--lumo-plate)); /* flat dark layer, keeps text readable */
}

/* ===== BUTTONS ===== */
.stApp :is(
    button[kind="primary"], button[data-testid="stBaseButton-primary"],
    button[kind="primaryFormSubmit"], button[data-testid="stBaseButton-primaryFormSubmit"],
    button[kind="secondary"], button[data-testid="stBaseButton-secondary"],
    button[kind="secondaryFormSubmit"], button[data-testid="stBaseButton-secondaryFormSubmit"]
) {
    border-radius: var(--lumo-radius);
    font-weight: 600;
    min-height: 44px;
    box-shadow: none !important;
    transition: background-color 0.12s ease, border-color 0.12s ease;
}
.stApp :is(
    button[kind="primary"], button[data-testid="stBaseButton-primary"],
    button[kind="primaryFormSubmit"], button[data-testid="stBaseButton-primaryFormSubmit"]
) {
    background: var(--lumo-accent-fill) !important;
    color: #ffffff !important;
    border: 1px solid var(--lumo-accent-fill) !important;
}
.stApp :is(
    button[kind="primary"], button[data-testid="stBaseButton-primary"],
    button[kind="primaryFormSubmit"], button[data-testid="stBaseButton-primaryFormSubmit"]
):hover {
    background: var(--lumo-accent-fill-hover) !important;
    border-color: var(--lumo-accent-fill-hover) !important;
}
.stApp :is(
    button[kind="secondary"], button[data-testid="stBaseButton-secondary"],
    button[kind="secondaryFormSubmit"], button[data-testid="stBaseButton-secondaryFormSubmit"]
) {
    background: var(--lumo-plate) !important;
    color: var(--lumo-text) !important;
    border: 1px solid var(--lumo-border-input) !important;
}
.stApp :is(
    button[kind="secondary"], button[data-testid="stBaseButton-secondary"],
    button[kind="secondaryFormSubmit"], button[data-testid="stBaseButton-secondaryFormSubmit"]
):hover {
    background: rgba(99, 102, 241, 0.16) !important;
    border-color: var(--lumo-accent-text) !important;
}

/* Sidebar navigation: quiet text rows, the active page is the accent fill */
[data-testid="stSidebar"] div.stButton > button { justify-content: flex-start; }
[data-testid="stSidebar"] div.stButton > button > div,
[data-testid="stSidebar"] div.stButton > button p {
    justify-content: flex-start;
    text-align: left;
    width: 100%;
}
[data-testid="stSidebar"] :is(
    button[kind="secondary"], button[data-testid="stBaseButton-secondary"]
) {
    background: transparent !important;
    border-color: transparent !important;
}
[data-testid="stSidebar"] :is(
    button[kind="secondary"], button[data-testid="stBaseButton-secondary"]
):hover {
    background: rgba(99, 102, 241, 0.16) !important;
    border-color: var(--lumo-accent-text) !important;
}

/* ===== TIMER (popover) ===== */
div[data-testid="stPopover"] {
    position: fixed;
    top: 0.6rem;
    right: 10rem;
    z-index: 1000000;
    width: auto;
}
div[data-testid="stPopover"] button {
    border-radius: var(--lumo-radius);
    background: var(--lumo-plate-strong) !important;
    border: 1px solid var(--lumo-border-input) !important;
    padding: 0.2rem 0.9rem;
    min-height: 44px;
}
div[data-testid="stPopover"] button:hover { border-color: var(--lumo-accent-text) !important; }
[data-testid="stElementContainer"]:has(> [data-testid="stPopover"]) {
    height: 0;
    min-height: 0;
    margin-bottom: -1rem;
}
div[data-testid="stPopoverBody"] {
    min-width: min(320px, 90vw);
    background: var(--lumo-plate-strong);
    border: 1px solid var(--lumo-border);
}
@media (max-width: 768px) {
    div[data-testid="stPopover"] { left: 3.5rem; right: auto; }
}

/* ===== INPUTS ===== */
div[data-baseweb="input"] > div,
div[data-baseweb="textarea"],
div[data-baseweb="select"] > div {
    background: rgba(2, 5, 11, 0.80) !important;
    border: 1px solid var(--lumo-border-input) !important;
    border-radius: var(--lumo-radius) !important;
}
input::placeholder, textarea::placeholder { color: var(--lumo-muted) !important; opacity: 1; }

/* ===== FOCUS (solid outline, never a glow) ===== */
div[data-baseweb="input"]:focus-within > div,
div[data-baseweb="textarea"]:focus-within,
div[data-baseweb="select"]:focus-within > div {
    border-color: var(--lumo-accent-text) !important;
    outline: 2px solid var(--lumo-accent-text);
    outline-offset: 2px;
}
[data-testid="stChatInput"]:focus-within {
    outline: 2px solid var(--lumo-accent-text);
    outline-offset: 2px;
}
.stApp :is(button, a, summary, [role="tab"]):focus-visible {
    outline: 2px solid var(--lumo-accent-text) !important;
    outline-offset: 2px;
}
div[role="radiogroup"] > label:has(input:focus-visible),
label[data-baseweb="checkbox"]:has(input:focus-visible) {
    outline: 2px solid var(--lumo-accent-text);
    outline-offset: 2px;
}

/* ===== QUIZ / RADIO OPTIONS AS TAPPABLE ROWS ===== */
div[role="radiogroup"] > label {
    background: var(--lumo-plate);
    border: 1px solid var(--lumo-border);
    border-radius: var(--lumo-radius);
    padding: 8px 14px;
    margin-bottom: 6px;
    transition: border-color 0.12s ease, background-color 0.12s ease;
}
div[role="radiogroup"] > label:hover {
    border-color: var(--lumo-accent-text);
    background: rgba(99, 102, 241, 0.14);
}
div[role="radiogroup"] > label:has(input:checked) {
    border-color: var(--lumo-accent-text);
    background: rgba(99, 102, 241, 0.22);
}

button[data-baseweb="tab"] { font-weight: 600; min-height: 44px; }

/* ===== PHONE / TABLET PAGE MENU =====
   app.py puts <span class="lumo-navmark"></span> right before a "Go to page"
   dropdown. Hidden on desktop, where the sidebar is used. Shown at 768px and
   below, where Streamlit collapses the sidebar. */
[data-testid="stElementContainer"]:has(.lumo-navmark) { display: none; }
@media (min-width: 769px) {
    [data-testid="stElementContainer"]:has(.lumo-navmark) + [data-testid="stElementContainer"] {
        display: none;
    }
}

/* ===== SCROLLBARS ===== */
::-webkit-scrollbar { width: 8px; height: 8px; }
::-webkit-scrollbar-thumb { background: rgba(255, 255, 255, 0.18); border-radius: 8px; }
::-webkit-scrollbar-track { background: transparent; }

/* ===== PHONES ===== */
@media (max-width: 640px) {
    .block-container {
        padding-left: 1rem;
        padding-right: 1rem;
        padding-top: 2.5rem;
    }
    [data-testid="stMarkdownContainer"] p,
    [data-testid="stMarkdownContainer"] li { font-size: 1rem; line-height: 1.625; }
    .stApp h1:not([style*="font-size"]) { font-size: 1.75rem !important; line-height: 1.21 !important; }
    .stApp h2, .stApp h3, .stApp h4 { font-size: 1.125rem !important; line-height: 1.44 !important; }
    .lumo-hero-title { font-size: 2.5rem; line-height: 1.1; }
    .lumo-login-hero { margin: 4vh 0 16px 0; }
    .lumo-login-hero .lumo-card { padding: 12px 14px !important; }
    [data-testid="stChatInput"] { border-radius: 14px !important; }
    .stApp :is(
        button[kind="primary"], button[data-testid="stBaseButton-primary"],
        button[kind="primaryFormSubmit"], button[data-testid="stBaseButton-primaryFormSubmit"],
        button[kind="secondary"], button[data-testid="stBaseButton-secondary"],
        button[kind="secondaryFormSubmit"], button[data-testid="stBaseButton-secondaryFormSubmit"]
    ) { min-height: 48px; }
    [data-testid="stChatMessage"] { padding: 10px 12px; }
}

/* =====================================================================
   POLISH LAYER: frosted glass, aurora-coloured accents, softer shapes.
   Sits on top of everything above. To undo the whole look, delete from
   here to the "END POLISH LAYER" marker.
   ===================================================================== */
:root {
    --lumo-radius: 12px;
    --lumo-glass: rgba(6, 12, 22, 0.66);
    --lumo-glass-strong: rgba(6, 12, 22, 0.82);
    --lumo-glass-edge: rgba(148, 163, 255, 0.18);
    --lumo-aurora-line: linear-gradient(90deg, #4ade80 0%, #2dd4bf 50%, #a78bfa 100%);
    --lumo-accent-grad: linear-gradient(135deg, #4f46e5 0%, #6d4cf0 100%);
    --lumo-accent-grad-hover: linear-gradient(135deg, #4338ca 0%, #5b3fe0 100%);
    --lumo-lift: 0 10px 30px rgba(0, 0, 0, 0.30);
}
::selection { background: rgba(99, 102, 241, 0.45); color: #fff; }

/* Glass surfaces: the aurora shows softly through, text stays on a dark plate */
.lumo-card, .sf-card,
[data-testid="stChatMessage"],
[data-testid="stExpander"],
[data-testid="stForm"],
[data-testid="stMetric"],
[data-testid="stVerticalBlockBorderWrapper"]:not(:has([data-testid="stPopover"])) {
    background: var(--lumo-glass);
    -webkit-backdrop-filter: blur(14px) saturate(140%);
    backdrop-filter: blur(14px) saturate(140%);
    border: 1px solid var(--lumo-glass-edge);
    border-radius: var(--lumo-radius);
    box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.05), var(--lumo-lift);
}
.sf-card { transition: border-color 0.15s ease; }
.sf-card:hover { border-color: rgba(129, 140, 248, 0.5); }
.sf-card h4 { margin-bottom: 4px; }

/* Messages: Lumo's replies sit on glass, yours carry an indigo tint */
[data-testid="stChatMessage"] { padding: 14px 18px; margin-bottom: 10px; }
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]),
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
    background: linear-gradient(135deg, rgba(79, 70, 229, 0.24), rgba(6, 12, 22, 0.70));
    border-left: 3px solid var(--lumo-accent-text);
}

/* Chat box */
[data-testid="stChatInput"] {
    background: var(--lumo-glass-strong) !important;
    -webkit-backdrop-filter: blur(14px);
    backdrop-filter: blur(14px);
    border: 1px solid var(--lumo-glass-edge) !important;
    border-radius: 16px !important;
    box-shadow: var(--lumo-lift);
}
button[data-testid="stChatInputSubmitButton"] {
    background: var(--lumo-accent-grad) !important;
    color: #fff !important;
    border-radius: 10px !important;
}
button[data-testid="stChatInputSubmitButton"]:disabled { opacity: 0.4; }

/* Buttons: soft indigo gradient, gentle lift on hover */
.stApp :is(
    button[kind="primary"], button[data-testid="stBaseButton-primary"],
    button[kind="primaryFormSubmit"], button[data-testid="stBaseButton-primaryFormSubmit"]
) {
    background: var(--lumo-accent-grad) !important;
    border-color: transparent !important;
    transition: transform 0.15s ease, box-shadow 0.15s ease, filter 0.15s ease;
}
.stApp :is(
    button[kind="primary"], button[data-testid="stBaseButton-primary"],
    button[kind="primaryFormSubmit"], button[data-testid="stBaseButton-primaryFormSubmit"]
):hover:not(:disabled) {
    background: var(--lumo-accent-grad-hover) !important;
    transform: translateY(-1px);
    box-shadow: 0 8px 22px rgba(79, 70, 229, 0.38) !important;
}
.stApp :is(
    button[kind="primary"], button[data-testid="stBaseButton-primary"],
    button[kind="primaryFormSubmit"], button[data-testid="stBaseButton-primaryFormSubmit"]
):active:not(:disabled) { transform: translateY(0); box-shadow: none !important; }
.stApp :is(button[kind="secondary"], button[data-testid="stBaseButton-secondary"]) {
    background: var(--lumo-glass) !important;
    border-color: var(--lumo-glass-edge) !important;
}
.stApp :is(button[kind="secondary"], button[data-testid="stBaseButton-secondary"]):hover:not(:disabled) {
    background: rgba(99, 102, 241, 0.18) !important;
    border-color: var(--lumo-accent-text) !important;
}
.stApp button:disabled { opacity: 0.45; }

/* Sidebar: glass panel, the active page glows softly */
[data-testid="stSidebar"] {
    background: rgba(2, 5, 11, 0.66) !important;
    -webkit-backdrop-filter: blur(16px);
    backdrop-filter: blur(16px);
}
[data-testid="stSidebar"] :is(button[kind="primary"], button[data-testid="stBaseButton-primary"]) {
    box-shadow: 0 6px 18px rgba(79, 70, 229, 0.30) !important;
}

/* Tabs: aurora underline marks the open tab */
div[data-baseweb="tab-highlight"] {
    background: var(--lumo-aurora-line) !important;
    height: 3px !important;
    border-radius: 3px;
}
div[data-baseweb="tab-border"] { background: var(--lumo-border) !important; }
button[data-baseweb="tab"][aria-selected="true"] { color: var(--lumo-text) !important; }

/* Progress and numbers (Progress page) */
[data-testid="stProgress"] [role="progressbar"] > div > div { background: var(--lumo-aurora-line) !important; }
[data-testid="stMetric"] { padding: 14px 18px; }
[data-testid="stMetricLabel"] p { color: var(--lumo-muted); }
[data-testid="stMetricValue"] { font-family: var(--lumo-font-head); font-weight: 600; }

/* Quiz answers: the chosen row gets an indigo edge */
div[role="radiogroup"] > label {
    background: var(--lumo-glass);
    border-color: var(--lumo-glass-edge);
    padding: 10px 14px;
}
div[role="radiogroup"] > label:has(input:checked) {
    box-shadow: inset 3px 0 0 var(--lumo-accent-text);
}

/* Upload box */
[data-testid="stFileUploaderDropzone"] {
    background: var(--lumo-glass);
    border: 1px dashed rgba(165, 176, 198, 0.55);
    border-radius: var(--lumo-radius);
    transition: border-color 0.15s ease, background-color 0.15s ease;
}
[data-testid="stFileUploaderDropzone"]:hover {
    border-color: var(--lumo-accent-text);
    background: rgba(99, 102, 241, 0.12);
}

/* The one memorable moment: the Lumo wordmark glows like the sky behind it */
.lumo-hero-title {
    font-size: 4rem;
    letter-spacing: -0.03em;
    background: linear-gradient(180deg, #ffffff 25%, #b9f5dc 100%);
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
    color: transparent;
    filter: drop-shadow(0 0 28px rgba(45, 212, 191, 0.28));
}
.lumo-login-hero .lumo-card { padding: 18px 22px; }
.lumo-login-hero .lumo-lede { color: var(--lumo-muted); }

/* Lighter effects on phones (smoother scrolling, less battery) */
@media (max-width: 640px) {
    .lumo-hero-title { font-size: 2.75rem; }
    .lumo-card, .sf-card, [data-testid="stChatMessage"], [data-testid="stExpander"],
    [data-testid="stForm"], [data-testid="stMetric"], [data-testid="stChatInput"],
    [data-testid="stSidebar"],
    [data-testid="stVerticalBlockBorderWrapper"]:not(:has([data-testid="stPopover"])) {
        -webkit-backdrop-filter: blur(8px);
        backdrop-filter: blur(8px);
    }
}
/* Browsers without blur support get a more solid plate so text stays readable */
@supports not ((backdrop-filter: blur(1px)) or (-webkit-backdrop-filter: blur(1px))) {
    :root { --lumo-glass: rgba(6, 12, 22, 0.88); --lumo-glass-strong: rgba(6, 12, 22, 0.92); }
}

/* ---- Round 2: more presence, same night-sky identity ---- */

/* Sidebar brand: a small glowing orb (a "lumen") beside the wordmark */
.lumo-brand { display: flex; align-items: center; gap: 10px; margin: 2px 0 14px; }
.lumo-brand-mark {
    width: 30px; height: 30px; border-radius: 50%; flex: none;
    background: radial-gradient(circle at 35% 30%, #d9fff0 0%, #2dd4bf 42%, #4f46e5 100%);
    box-shadow: 0 0 20px rgba(45, 212, 191, 0.55), 0 0 2px rgba(255, 255, 255, 0.6) inset;
}
.lumo-brand-name {
    font-family: var(--lumo-font-head); font-size: 1.75rem; font-weight: 600;
    letter-spacing: -0.02em; color: var(--lumo-text); line-height: 1;
}
.lumo-user {
    display: flex; align-items: center; gap: 10px; padding: 10px 12px; margin-bottom: 14px;
    background: var(--lumo-glass); border: 1px solid var(--lumo-glass-edge);
    border-radius: var(--lumo-radius);
}
.lumo-avatar {
    width: 34px; height: 34px; border-radius: 50%; flex: none;
    display: grid; place-items: center; font-weight: 700; color: #fff;
    background: var(--lumo-accent-grad);
}
.lumo-user-text { min-width: 0; }
.lumo-user-hi { font-size: 0.75rem; color: var(--lumo-muted); line-height: 1.2; }
.lumo-user-name {
    font-weight: 700; line-height: 1.25;
    overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}

/* Sidebar pages: the open page gets an aurora edge, others slide in on hover */
[data-testid="stSidebar"] :is(button[kind="primary"], button[data-testid="stBaseButton-primary"]) {
    box-shadow: inset 3px 0 0 #2dd4bf, 0 6px 18px rgba(79, 70, 229, 0.30) !important;
}
[data-testid="stSidebar"] :is(button[kind="secondary"], button[data-testid="stBaseButton-secondary"]) {
    transition: transform 0.15s ease, background-color 0.15s ease, border-color 0.15s ease;
}
[data-testid="stSidebar"] :is(button[kind="secondary"], button[data-testid="stBaseButton-secondary"]):hover {
    transform: translateX(3px);
}

/* Page headers: bigger, with an aurora underline */
.stApp h1[style*="margin-bottom"] { font-size: 2.75rem !important; line-height: 1.1 !important; }
.stApp h1[style*="margin-bottom"]::after {
    content: ""; display: block; width: 64px; height: 3px; border-radius: 3px;
    background: var(--lumo-aurora-line); margin: 14px auto 6px;
}

/* Start page cards: each takes one aurora colour on its top edge, and lifts on hover */
:is([data-testid="stColumn"], [data-testid="column"]) [data-testid="stVerticalBlockBorderWrapper"] {
    position: relative; overflow: hidden;
    --card-a: #4ade80; --card-b: #2dd4bf;
    transition: transform 0.18s ease, box-shadow 0.18s ease, border-color 0.18s ease;
}
:is([data-testid="stColumn"], [data-testid="column"]):nth-child(2) [data-testid="stVerticalBlockBorderWrapper"] {
    --card-a: #2dd4bf; --card-b: #60a5fa;
}
:is([data-testid="stColumn"], [data-testid="column"]):nth-child(3) [data-testid="stVerticalBlockBorderWrapper"] {
    --card-a: #818cf8; --card-b: #a78bfa;
}
:is([data-testid="stColumn"], [data-testid="column"]) [data-testid="stVerticalBlockBorderWrapper"]::before {
    content: ""; position: absolute; inset: 0 0 auto 0; height: 3px;
    background: linear-gradient(90deg, var(--card-a), var(--card-b));
}
:is([data-testid="stColumn"], [data-testid="column"]) [data-testid="stVerticalBlockBorderWrapper"]:hover {
    transform: translateY(-3px);
    border-color: rgba(129, 140, 248, 0.45);
    box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.05), 0 18px 40px rgba(0, 0, 0, 0.42);
}

/* Chat: new messages ease in, Lumo's avatar carries the orb gradient */
@keyframes lumo-rise {
    from { opacity: 0; transform: translateY(8px); }
    to   { opacity: 1; transform: none; }
}
[data-testid="stChatMessage"] { animation: lumo-rise 0.35s ease both; }
[data-testid="stChatMessageAvatarAssistant"],
[data-testid="chatAvatarIcon-assistant"] {
    background: linear-gradient(135deg, #2dd4bf, #6366f1) !important;
    color: #fff !important;
    border-radius: 50%;
}

/* Login: feature chips under the description */
.lumo-chips { display: flex; flex-wrap: wrap; gap: 8px; justify-content: center; margin-top: 14px; }
.lumo-chip {
    display: inline-flex; align-items: center; gap: 7px; padding: 6px 13px;
    border-radius: 999px; font-size: 0.875rem; color: var(--lumo-text);
    background: var(--lumo-glass); border: 1px solid var(--lumo-glass-edge);
}
.lumo-chip i { width: 8px; height: 8px; border-radius: 50%; display: block; }

@media (max-width: 640px) {
    .stApp h1[style*="margin-bottom"] { font-size: 2rem !important; }
}
@media (prefers-reduced-motion: reduce) {
    [data-testid="stChatMessage"] { animation: none; }
    :is([data-testid="stColumn"], [data-testid="column"]) [data-testid="stVerticalBlockBorderWrapper"]:hover,
    [data-testid="stSidebar"] button:hover { transform: none; }
}

/* Progress: aurora score ring */
.lumo-ring-wrap {
    display: flex; align-items: center; gap: 24px; padding: 20px 24px; margin: 4px 0 16px;
    background: var(--lumo-glass); border: 1px solid var(--lumo-glass-edge);
    border-radius: var(--lumo-radius); box-shadow: inset 0 1px 0 rgba(255,255,255,0.05), var(--lumo-lift);
    -webkit-backdrop-filter: blur(14px); backdrop-filter: blur(14px);
}
.lumo-ring {
    --pct: 0; flex: none; width: 128px; height: 128px; border-radius: 50%;
    display: grid; place-items: center;
    background: conic-gradient(#4ade80 0%, #2dd4bf calc(var(--pct) * 0.5%), #a78bfa calc(var(--pct) * 1%),
                               rgba(255, 255, 255, 0.09) calc(var(--pct) * 1%));
    filter: drop-shadow(0 0 16px rgba(45, 212, 191, 0.30));
}
.lumo-ring-inner {
    width: 100px; height: 100px; border-radius: 50%; background: #060c17;
    display: flex; flex-direction: column; align-items: center; justify-content: center;
}
.lumo-ring-num { font-family: var(--lumo-font-head); font-size: 1.9rem; font-weight: 600; line-height: 1; }
.lumo-ring-label { font-size: 0.72rem; color: var(--lumo-muted); margin-top: 4px; }
.lumo-ring-title { font-family: var(--lumo-font-head); font-size: 1.5rem; font-weight: 600; margin-bottom: 4px; }
.lumo-ring-side p { margin: 0; color: var(--lumo-muted); }
@media (max-width: 640px) {
    .lumo-ring-wrap { flex-direction: column; text-align: center; gap: 14px; }
}
/* ===== END POLISH LAYER ===== */

@media (prefers-reduced-motion: reduce) {
    .stApp * { transition: none !important; }
}
</style>
"""

# Tiny early rule sent as normal page content, so the page is already dark
# (never white) before the injected Aurora arrives.
_EARLY_CSS = (
    "<style>html{background:#02050b!important}"
    ".stApp,[data-testid=\"stAppViewContainer\"],[data-testid=\"stMain\"],"
    "[data-testid=\"stHeader\"]{background:transparent!important}</style>"
)


def apply_lumo_styles():
    st.markdown(_EARLY_CSS, unsafe_allow_html=True)
    aurora_css = (
        _AURORA_CSS
        .replace("__WAVE1__", _wave("%234ade80", 0.55))
        .replace("__WAVE2__", _wave("%232dd4bf", 0.45))
        .replace("__WAVE3__", _wave("%23a78bfa", 0.38))
        .replace("__TREES__", _TREES)
    )
    payload = json.dumps(
        _FONT_LINK + _AURORA_HTML + aurora_css + _AURORA_MOBILE_CSS + _THEME_CSS
    )
    # Inject straight into the page (Streamlit ignores big style blocks sent as text).
    # If an older copy from a previous deploy is already there, replace it once.
    components.html(
        f"""<script>
(function() {{
  var VERSION = '{_HOLDER_VERSION}';
  var d = window.parent.document;
  var old = d.getElementById('lumo-aurora-root');
  if (old) {{
    if (old.getAttribute('data-v') === VERSION) return;
    old.remove();
  }}
  var holder = d.createElement('div');
  holder.id = 'lumo-aurora-root';
  holder.setAttribute('data-v', VERSION);
  holder.innerHTML = {payload};
  d.body.appendChild(holder);
}})();
</script>""",
        height=0,
    )


# Card styles now live in the theme above; kept so `from styles import CARD_CSS` still works.
CARD_CSS = "<style>/* card styles live in styles.py */</style>"
