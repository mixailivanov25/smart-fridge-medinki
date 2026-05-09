
import streamlit as st
from urllib.parse import quote


NAV_ALIASES = {
    "fast": "📱 Быстрый экран",
    "home": "🏠 Главная",
    "fridge": "🧊 Мой холодильник",
    "photo": "📸 Фото и сканер",
    "shopping": "🛒 Умные покупки",
    "analytics": "📊 Аналитика",
    "diary": "📔 Дневник питания",
    "recipes": "🍳 Рецепты",
    "menu": "🗓️ Меню на неделю",
}


def process_mobile_nav_v13():
    """
    Обрабатывает переходы из нижней мобильной навигации.

    Ссылки вида:
        ?go=home
        ?go=fridge
        ?go=photo

    превращаются в установку main_navigation.
    """
    try:
        go = st.query_params.get("go", None)
    except Exception:
        go = None

    if isinstance(go, list):
        go = go[0] if go else None

    if not go:
        return

    target = NAV_ALIASES.get(str(go).strip())

    if not target:
        return

    # Чтобы query param не перетирал выбор из sidebar на каждом rerun.
    last = st.session_state.get("_last_mobile_nav_go_v13")

    if last == go:
        return

    st.session_state["_last_mobile_nav_go_v13"] = go
    st.session_state["pending_navigation"] = target

    try:
        st.session_state["main_navigation"] = target
    except Exception:
        pass


def apply_modern_sidebar_and_mobile_nav_v13():
    """
    Современный вид sidebar + нижняя мобильная навигация.
    """
    st.markdown(
        """
<style>
/* ===== Modern sidebar nav ===== */

[data-testid="stSidebar"] {
    background:
        radial-gradient(circle at top left, rgba(34, 197, 94, .10), transparent 34%),
        linear-gradient(180deg, #f4fff8 0%, #ffffff 100%) !important;
    border-right: 1px solid rgba(18, 51, 33, 0.08) !important;
}

[data-testid="stSidebar"] [role="radiogroup"] {
    display: flex !important;
    flex-direction: column !important;
    gap: 5px !important;
}

/* Прячем radio-кружки */
[data-testid="stSidebar"] [role="radiogroup"] input[type="radio"] {
    display: none !important;
    opacity: 0 !important;
    width: 0 !important;
    height: 0 !important;
    position: absolute !important;
}

/* Убираем контейнеры кружков в разных версиях Streamlit */
[data-testid="stSidebar"] [role="radiogroup"] label > div:first-child:has(input[type="radio"]) {
    display: none !important;
}

[data-testid="stSidebar"] [role="radiogroup"] label {
    min-height: 38px !important;
    border-radius: 16px !important;
    padding: 9px 12px !important;
    margin: 0 !important;
    border: 1px solid transparent !important;
    background: transparent !important;
    color: #123321 !important;
    font-weight: 650 !important;
    transition:
        background .16s ease,
        transform .16s ease,
        box-shadow .16s ease,
        border-color .16s ease !important;
    cursor: pointer !important;
}

[data-testid="stSidebar"] [role="radiogroup"] label:hover {
    background: rgba(34, 197, 94, 0.10) !important;
    border-color: rgba(34, 197, 94, 0.14) !important;
    transform: translateX(2px) !important;
}

/* Активный пункт через :has */
[data-testid="stSidebar"] [role="radiogroup"] label:has(input[type="radio"]:checked) {
    background: linear-gradient(135deg, rgba(34,197,94,.20), rgba(240,253,244,.95)) !important;
    border-color: rgba(34,197,94,.28) !important;
    box-shadow: 0 8px 20px rgba(15,23,42,.06) !important;
    color: #0b2f20 !important;
}

/* Если Streamlit рисует пустой круг не input-ом */
[data-testid="stSidebar"] [role="radiogroup"] svg {
    display: none !important;
}

/* Sidebar title compact */
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    line-height: 1.18 !important;
}

/* ===== Bottom mobile navigation ===== */

.medinki-bottom-nav-v13 {
    display: none;
}

@media (max-width: 760px) {
    .block-container {
        padding-bottom: 6.2rem !important;
    }

    .medinki-bottom-nav-v13 {
        position: fixed;
        display: grid;
        grid-template-columns: repeat(5, 1fr);
        left: 10px;
        right: 10px;
        bottom: 10px;
        z-index: 999999;
        padding: 8px;
        border-radius: 26px;
        background: rgba(255,255,255,.92);
        border: 1px solid rgba(18, 51, 33, .10);
        box-shadow: 0 18px 44px rgba(15,23,42,.18);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        gap: 6px;
    }

    .medinki-bottom-nav-v13 a {
        text-decoration: none !important;
        color: #123321 !important;
        border-radius: 20px;
        padding: 8px 4px 7px 4px;
        min-height: 46px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        gap: 2px;
        font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        font-weight: 800;
        font-size: 10px;
        line-height: 1.05;
        transition: background .15s ease, transform .15s ease;
    }

    .medinki-bottom-nav-v13 a:hover {
        background: rgba(34,197,94,.12);
        transform: translateY(-1px);
    }

    .medinki-bottom-nav-v13 .nav-emoji {
        font-size: 20px;
        line-height: 1;
    }

    .medinki-bottom-nav-v13 .nav-text {
        white-space: nowrap;
    }
}
</style>
        """,
        unsafe_allow_html=True,
    )


def render_bottom_mobile_nav_v13():
    """
    Фиксированная нижняя мобильная навигация.
    На desktop скрыта через CSS.
    """
    items = [
        ("home", "🏠", "Главная"),
        ("fridge", "🧊", "Холод."),
        ("photo", "📸", "Фото"),
        ("shopping", "🛒", "Покупки"),
        ("analytics", "📊", "Аналит."),
    ]

    links = []

    for key, emoji, label in items:
        href = f"?go={quote(key)}"
        links.append(
            f"""
<a href="{href}" target="_self">
    <span class="nav-emoji">{emoji}</span>
    <span class="nav-text">{label}</span>
</a>
"""
        )

    html = f"""
<div class="medinki-bottom-nav-v13">
    {''.join(links)}
</div>
"""

    st.markdown(html, unsafe_allow_html=True)
