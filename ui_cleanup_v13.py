import streamlit as st


def apply_ui_cleanup_v13():
    """
    Общая чистка интерфейса v1.3:
    - меньше обрезаний текста;
    - аккуратнее боковое меню;
    - скрытие лишних Streamlit-якорей;
    - более современный вид карточек и кнопок.
    """
    st.markdown(
        """
<style>
/* ===== Base layout ===== */

html, body, [data-testid="stAppViewContainer"] {
    background: #f6f8f7;
}

.block-container {
    padding-top: 1.8rem !important;
    padding-bottom: 3rem !important;
    max-width: 1320px !important;
}

/* Чтобы заголовки не обрезались */
h1, h2, h3 {
    line-height: 1.22 !important;
    overflow: visible !important;
    padding-bottom: 0.12em !important;
    color: #123321 !important;
}

/* Скрыть маленькие якоря-ссылки возле заголовков */
a[href^="#"] {
    display: none !important;
}

/* Скрыть кнопку Deploy и верхние лишние элементы Streamlit */
.stDeployButton {
    display: none !important;
}

[data-testid="stToolbar"] {
    display: none !important;
}

/* Скрыть кнопку сворачивания sidebar */
[data-testid="collapsedControl"] {
    display: none !important;
}

/* ===== Sidebar ===== */

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #f7fff9 0%, #ffffff 100%) !important;
    border-right: 1px solid rgba(18, 51, 33, 0.08);
}

[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    font-size: 1.15rem !important;
    line-height: 1.28 !important;
}

[data-testid="stSidebar"] .stButton > button {
    border-radius: 18px !important;
}

/* Радио-навигация аккуратнее */
[data-testid="stSidebar"] [role="radiogroup"] label {
    padding: 8px 10px !important;
    border-radius: 14px !important;
    margin-bottom: 4px !important;
    transition: all .16s ease;
}

[data-testid="stSidebar"] [role="radiogroup"] label:hover {
    background: rgba(34, 197, 94, 0.10) !important;
}

/* ===== Buttons ===== */

div.stButton > button {
    border-radius: 18px !important;
    min-height: 46px !important;
    font-weight: 700 !important;
    border: 1px solid rgba(18, 51, 33, 0.12) !important;
    box-shadow: 0 8px 20px rgba(15, 23, 42, 0.06);
    transition: transform .15s ease, box-shadow .15s ease, background .15s ease;
}

div.stButton > button:hover {
    transform: translateY(-1px);
    box-shadow: 0 12px 26px rgba(15, 23, 42, 0.10);
}

/* ===== Cards / expanders ===== */

[data-testid="stExpander"] {
    border-radius: 20px !important;
    overflow: hidden !important;
}

.stForm {
    border-radius: 22px !important;
}

/* ===== Inputs ===== */

input, textarea, select {
    border-radius: 16px !important;
}

/* ===== Mobile ===== */

@media (max-width: 760px) {
    .block-container {
        padding-top: 1.1rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }

    h1 {
        font-size: 2.0rem !important;
    }

    h2 {
        font-size: 1.55rem !important;
    }

    h3 {
        font-size: 1.28rem !important;
    }

    div.stButton > button {
        min-height: 50px !important;
        font-size: 1rem !important;
    }

    [data-testid="stSidebar"] {
        min-width: 300px !important;
        max-width: 320px !important;
    }
}
</style>
        """,
        unsafe_allow_html=True,
    )
