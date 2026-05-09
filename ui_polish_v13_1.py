
import streamlit as st


def apply_ui_polish_v13_1():
    """
    Дополнительная визуальная полировка v1.3.1:
    - убирает ощущение дублей иконок;
    - чинит тёмный текст на тёмных карточках;
    - улучшает mobile;
    - делает таблицы аккуратнее;
    - полирует sidebar.
    """
    st.markdown(
        """
<style>
/* ===== Global polish ===== */

html, body, [data-testid="stAppViewContainer"] {
    background: #f5f8f6 !important;
}

.block-container {
    max-width: 1320px !important;
    padding-top: 1.25rem !important;
    padding-bottom: 3rem !important;
}

/* Заголовки без обрезаний */
h1, h2, h3 {
    line-height: 1.18 !important;
    overflow: visible !important;
    padding-bottom: 0.12em !important;
    color: #0b2f20 !important;
    letter-spacing: -0.02em;
}

p {
    line-height: 1.55 !important;
}

/* Скрыть якоря Streamlit возле заголовков */
a[href^="#"] {
    display: none !important;
}

/* Скрыть служебные элементы Streamlit */
.stDeployButton,
[data-testid="stToolbar"] {
    display: none !important;
}

/* ===== Sidebar ===== */

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #f4fff8 0%, #ffffff 100%) !important;
    border-right: 1px solid rgba(18, 51, 33, 0.08) !important;
}

[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    font-size: 1.05rem !important;
    line-height: 1.22 !important;
}

/* Навигация более похожа на меню, а не на дешёвые radio */
[data-testid="stSidebar"] [role="radiogroup"] label {
    border-radius: 14px !important;
    padding: 8px 10px !important;
    margin-bottom: 4px !important;
    transition: background .15s ease, transform .15s ease !important;
}

[data-testid="stSidebar"] [role="radiogroup"] label:hover {
    background: rgba(34, 197, 94, 0.10) !important;
    transform: translateX(1px);
}

/* Прячем кружки radio аккуратно, оставляем текст */
[data-testid="stSidebar"] input[type="radio"] {
    display: none !important;
}

/* ===== Buttons ===== */

div.stButton > button {
    border-radius: 18px !important;
    min-height: 48px !important;
    font-weight: 750 !important;
    border: 1px solid rgba(18, 51, 33, 0.12) !important;
    box-shadow: 0 8px 20px rgba(15, 23, 42, 0.055) !important;
    transition: transform .15s ease, box-shadow .15s ease !important;
}

div.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 12px 26px rgba(15, 23, 42, 0.10) !important;
}

/* ===== Cards ===== */

.medinki-hero,
.medinki-card,
.medinki-page-intro,
.medinki-soft,
.medinki-user-card,
.medinki-intro-card {
    overflow: visible !important;
}

/* Тёмные hero-карточки: весь текст белый */
.medinki-hero,
.medinki-hero * {
    color: white !important;
}

/* Если тёмный зелёный задан inline-стилем */
div[style*="background: linear-gradient"][style*="#123321"] *,
div[style*="background:linear-gradient"][style*="#123321"] *,
div[style*="background: linear-gradient"][style*="#246b43"] *,
div[style*="background:linear-gradient"][style*="#246b43"] * {
    color: white !important;
}

/* Новая карточка intro */
.medinki-intro-card {
    padding: 18px 22px;
    border-radius: 24px;
    background: rgba(255,255,255,.92);
    border: 1px solid rgba(18,51,33,.10);
    box-shadow: 0 10px 26px rgba(15,23,42,.055);
    margin: 12px 0 20px 0;
}

.medinki-intro-card h1 {
    display: flex;
    align-items: center;
    gap: 12px;
    margin: 0 !important;
    font-size: clamp(1.75rem, 3.2vw, 2.7rem) !important;
}

.medinki-intro-icon {
    display: inline-flex;
    flex: 0 0 auto;
    font-size: 1.95rem;
    line-height: 1;
}

.medinki-intro-card p {
    margin: 10px 0 0 0 !important;
    color: #475569 !important;
    font-size: 1.04rem !important;
}

/* Таблицы аккуратнее */
[data-testid="stDataFrame"],
[data-testid="stTable"] {
    border-radius: 16px !important;
    overflow: auto !important;
}

/* Footer выглядит компактнее */
div[style*="версия v1."] {
    border-radius: 18px !important;
}

/* ===== Mobile ===== */

@media (max-width: 760px) {
    .block-container {
        padding-top: .85rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }

    h1 {
        font-size: 1.65rem !important;
        line-height: 1.18 !important;
    }

    h2 {
        font-size: 1.35rem !important;
    }

    h3 {
        font-size: 1.15rem !important;
    }

    .medinki-hero {
        padding: 20px !important;
        border-radius: 24px !important;
        margin-bottom: 14px !important;
    }

    .medinki-hero h1 {
        font-size: 1.8rem !important;
    }

    .medinki-card,
    .medinki-user-card {
        padding: 16px !important;
        border-radius: 22px !important;
    }

    .medinki-intro-card {
        padding: 16px !important;
        border-radius: 22px !important;
        margin: 10px 0 16px 0 !important;
    }

    .medinki-intro-card h1 {
        font-size: 1.55rem !important;
        gap: 9px !important;
    }

    .medinki-intro-icon {
        font-size: 1.45rem !important;
    }

    .medinki-intro-card p {
        font-size: .96rem !important;
    }

    div.stButton > button {
        min-height: 50px !important;
        font-size: .98rem !important;
    }

    [data-testid="stDataFrame"],
    [data-testid="stTable"] {
        font-size: .82rem !important;
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
