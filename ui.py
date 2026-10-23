import html as _html
import streamlit as st

def _t(text) -> str:
    """Escape text so user-typed words can never be read as HTML."""
    return _html.escape(str(text))

def card(title: str, body: str = ""):
    """A reusable glassmorphism card component."""
    st.markdown(
        f"""
        <div class="lumo-card" style="padding: 16px 20px;">
            <h4 style="margin: 0 0 6px 0;">{_t(title)}</h4>
            <p style="margin: 0; color: var(--lumo-muted);">{_t(body)}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

def page_header(title: str, subtitle: str = ""):
    """Renders a beautiful, large page header with a frosted glass subtitle plate."""
    sub = (
        f"""<p style="
            display: inline-block;
            background: var(--lumo-plate);
            border-radius: var(--lumo-radius);
            padding: 4px 12px;
            color: var(--lumo-muted);
            margin-top: 8px;
        ">{_t(subtitle)}</p>"""
        if subtitle else ""
    )
    st.markdown(
        f"""
        <div style="text-align: center; animation: slideDownFade 0.4s ease-out forwards; margin-bottom: 2rem;">
            <h1 style="margin-bottom: 0;">{_t(title)}</h1>
            {sub}
        </div>
        """,
        unsafe_allow_html=True,
    )

def stat_card(label: str, value, icon: str = ""):
    """Renders a glassmorphism dashboard stat card."""
    st.markdown(
        f"""
        <div class="lumo-card" style="text-align: center; padding: 1.5rem;">
            <div style="font-family: var(--lumo-font-head); font-size: 2.5rem; font-weight: 600; color: var(--lumo-text); line-height: 1;">{_t(value)}</div>
            <div style="font-size: 0.75rem; color: var(--lumo-muted); text-transform: uppercase; letter-spacing: 0.05em; margin-top: 8px;">{_t(label)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

def empty_state(icon: str, title: str, description: str = ""):
    """Friendly placeholder when a page has no data yet."""
    st.markdown(
        f"""
        <div style="text-align: center; padding: 3rem 1rem; color: var(--lumo-muted);">
            <div style="font-size: 3rem; margin-bottom: 1rem;">{icon}</div>
            <h3 style="color: var(--lumo-text); font-weight: 600;">{_t(title)}</h3>
            <p>{_t(description)}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

def progress_bar(label: str, percentage):
    """Renders a custom glowing gradient progress bar."""
    percent = max(0, min(100, int(percentage)))
    safe_label = _t(label)
    st.markdown(
        f"""
        <div style="margin-bottom: 1rem;">
            <div style="display: flex; justify-content: space-between; font-size: 0.875rem; margin-bottom: 4px;">
                <span style="font-weight: 600; color: var(--lumo-text);">{safe_label}</span>
                <span style="color: var(--lumo-muted);">{percent}%</span>
            </div>
            <div style="width: 100%; background: var(--lumo-plate-strong); border-radius: 999px; height: 8px; overflow: hidden; border: 1px solid var(--lumo-border);">
                <div style="width: {percent}%; background: var(--lumo-aurora-line); height: 100%; border-radius: 999px; transition: width 1s ease-in-out;"></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
