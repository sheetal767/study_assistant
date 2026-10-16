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
