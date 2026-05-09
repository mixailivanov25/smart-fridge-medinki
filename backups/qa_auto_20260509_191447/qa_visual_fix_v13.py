
import streamlit as st


def apply_qa_visual_fix_v13():
    """
    Safe visual QA fix:
    - не ломает бизнес-логику;
    - чинит обрезание заголовков;
    - улучшает sidebar;
    - прячет лишние Streamlit-элементы;
    - делает кнопки и карточки аккуратнее.
    """
    st.markdown(
        """
<style>
html, body, [data-testid="stAppViewContainer"] {
    background: #f5f8f6 !important;
}

.block-container {
    max-width: 1320px !important;
    padding-top: 1.35rem !important;
    padding-left: 2rem !important;
    padding-right: 2rem !important;
    padding-bottom: 3rem !important;
}

h1, h2, h3 {
    line-height: 1.22 !important;
    overflow: visible !important;
    padding-bottom: 0.15em !important;
    color: #123321 !important;
    word-break: normal !important;
}

p, div, span, label {
    word-break: normal !important;
}

a[href^="#"] {
    display: none !important;
}

.stDeployButton,
[data-testid="stToolbar"] {
    display: none !important;
}

[data-testid="collapsedControl"] {
    display: none !important;
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #f7fff9 0%, #ffffff 100%) !important;
    border-right: 1px solid rgba(18, 51, 33, 0.08) !important;
}

[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    font-size: 1.12rem !important;
    line-height: 1.25 !important;
}

[data-testid="stSidebar"] [role="radiogroup"] label {
    padding: 8px 10px !important;
    border-radius: 14px !important;
    margin-bottom: 3px !important;
    transition: background .15s ease !important;
}

[data-testid="stSidebar"] [role="radiogroup"] label:hover {
    background: rgba(34, 197, 94, 0.10) !important;
}

div.stButton > button {
    border-radius: 18px !important;
    min-height: 48px !important;
    font-weight: 750 !important;
    border: 1px solid rgba(18, 51, 33, 0.12) !important;
    box-shadow: 0 8px 20px rgba(15, 23, 42, 0.06) !important;
    transition: transform .15s ease, box-shadow .15s ease !important;
}

div.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 12px 26px rgba(15, 23, 42, 0.10) !important;
}

[data-testid="stExpander"] {
    border-radius: 20px !important;
    overflow: hidden !important;
}

.stForm {
    border-radius: 22px !important;
}

input, textarea, select {
    border-radius: 16px !important;
}

.medinki-hero,
.medinki-card,
.medinki-page-intro,
.medinki-soft,
.medinki-user-card {
    overflow: visible !important;
}

@media (max-width: 760px) {
    .block-container {
        padding-top: 1rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }

    h1 {
        font-size: 1.85rem !important;
    }

    h2 {
        font-size: 1.45rem !important;
    }

    h3 {
        font-size: 1.22rem !important;
    }

    div.stButton > button {
        min-height: 52px !important;
        font-size: 1rem !important;
    }

    [data-testid="stSidebar"] {
        min-width: 300px !important;
        max-width: 330px !important;
    }
}
</style>
        """,
        unsafe_allow_html=True,
    )
