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
