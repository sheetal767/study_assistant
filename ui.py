import html

import streamlit as st

# Small reusable building blocks. Colors and fonts come from the CSS variables
# defined in styles.py, so changing the theme there changes everything here.


def _t(text) -> str:
    """Escape text so user-typed words can never be read as HTML."""
    return html.escape(str(text))


def card(title: str, body: str = ""):
    """A reusable card component."""
    st.markdown(
        f"""
        <div class="lumo-card" style="padding:16px 20px">
            <h4 style="margin:0 0 6px 0">{_t(title)}</h4>
            <p style="margin:0;color:var(--lumo-muted)">{_t(body)}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def page_header(title: str, subtitle: str = ""):
    """Page title with an optional subtitle."""
    sub = (
        f"<p style='color:var(--lumo-muted);margin:0'>{_t(subtitle)}</p>"
        if subtitle else ""
    )
    st.markdown(
        f"<h1 style='margin-bottom:4px'>{_t(title)}</h1>{sub}",
        unsafe_allow_html=True,
    )


def stat_card(label: str, value, icon: str = ""):
    """Small metric card, e.g. minutes studied or average score.

    `icon` is still accepted so older calls keep working, but it is no longer shown.
    """
    st.markdown(
        f"""
        <div class="lumo-card" style="text-align:center;padding:16px 20px">
            <div style="font-family:var(--lumo-font-head);font-size:2rem;font-weight:600;line-height:1.2">{_t(value)}</div>
            <div style="color:var(--lumo-muted);font-size:0.875rem;margin-top:4px">{_t(label)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def empty_state(icon: str, title: str, hint: str = ""):
    """Friendly placeholder when a page has no data yet.

    `icon` is still accepted so older calls keep working, but it is no longer shown.
    """
    hint_html = (
        f"<div style='color:var(--lumo-muted);font-size:0.875rem'>{_t(hint)}</div>"
        if hint else ""
    )
    st.markdown(
        f"""
        <div class="lumo-card" style="text-align:center;padding:32px 20px">
            <div style="font-weight:600;font-size:1.125rem;margin-bottom:4px">{_t(title)}</div>
            {hint_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def progress_bar(label: str, percent: int):
    """Horizontal bar, e.g. a quiz score. percent is 0 to 100."""
    percent = max(0, min(100, int(percent)))
    safe_label = _t(label)
    st.markdown(
        f"""
        <div style="margin-bottom:12px">
            <div style="display:flex;justify-content:space-between;font-size:0.875rem;margin-bottom:4px">
                <span>{safe_label}</span><span style="color:var(--lumo-muted)">{percent}%</span>
            </div>
            <div role="progressbar" aria-label="{safe_label}" aria-valuemin="0" aria-valuemax="100"
                 aria-valuenow="{percent}"
                 style="background:var(--lumo-border);border:1px solid var(--lumo-border-input);border-radius:999px;height:10px;overflow:hidden">
                <div style="width:{percent}%;height:100%;background:var(--lumo-accent-text)"></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
