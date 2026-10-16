import streamlit as st


def card(title: str, body: str = ""):
    """A reusable card component."""
    st.markdown(
        f"""
        <div class="sf-card">
            <h4>{title}</h4>
            <p>{body}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def page_header(title: str, subtitle: str = ""):
    """Big page title with an optional subtitle."""
    sub = f"<p style='opacity:0.7;margin:0'>{subtitle}</p>" if subtitle else ""
    st.markdown(
        f"<h1 style='margin-bottom:4px'>{title}</h1>{sub}",
        unsafe_allow_html=True,
    )


def stat_card(label: str, value, icon: str = ""):
    """Small metric card, e.g. topics done or quiz score."""
    st.markdown(
        f"""
        <div class="sf-card" style="text-align:center">
            <div style="font-size:1.6rem">{icon}</div>
            <div style="font-size:1.8rem;font-weight:700">{value}</div>
            <div style="opacity:0.7;font-size:0.85rem">{label}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def empty_state(icon: str, title: str, hint: str = ""):
    """Friendly placeholder when a page has no data yet."""
    hint_html = f"<div style='opacity:0.65;font-size:0.9rem'>{hint}</div>" if hint else ""
    st.markdown(
        f"""
        <div class="sf-card" style="text-align:center;padding:32px 20px">
            <div style="font-size:2.4rem;margin-bottom:6px">{icon}</div>
            <div style="font-weight:600;font-size:1.05rem;margin-bottom:4px">{title}</div>
            {hint_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def progress_bar(label: str, percent: int):
    """Horizontal bar, e.g. a quiz score. percent is 0 to 100."""
    percent = max(0, min(100, int(percent)))
    st.markdown(
        f"""
        <div style="margin-bottom:12px">
            <div style="display:flex;justify-content:space-between;font-size:0.85rem;margin-bottom:4px">
                <span>{label}</span><span style="opacity:0.7">{percent}%</span>
            </div>
            <div style="background:rgba(128,128,128,0.2);border-radius:999px;height:8px;overflow:hidden">
                <div style="width:{percent}%;height:100%;background:#6366f1;border-radius:999px"></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
