
import streamlit as st
import streamlit.components.v1 as components


def modern_go(target_page: str):
    aliases = {
        "Быстрый экран": "📱 Быстрый экран",
        "Главная": "🏠 Главная",
        "Семейный режим": "👨‍👩‍👧 Семейный режим",
        "Сегодня": "📅 Сегодня",
        "Дневник питания": "📔 Дневник питания",
        "Добавить еду": "📔 Дневник питания",
        "Умные покупки": "🛒 Умные покупки",
        "Добавить покупку": "🛒 Умные покупки",
        "Аналитика": "📊 Аналитика",
        "Мои рецепты": "📝 Мои рецепты",
        "Мой холодильник": "🧊 Мой холодильник",
        "Холодильник": "🧊 Мой холодильник",
        "Добавить продукты": "➕ Добавить продукты",
        "Рецепты": "🍳 Рецепты",
        "Каталог блюд": "🍽️ Каталог блюд",
        "Меню": "🗓️ Меню на неделю",
        "Меню на неделю": "🗓️ Меню на неделю",
        "Список покупок": "🛒 Список покупок",
        "Питание и цели": "🎯 Питание и цели",
        "Любимые блюда": "❤️ Любимые блюда",
        "История": "📜 История",
        "Списания": "📉 Списания",
        "Демо-режим": "🧪 Демо-режим",
        "Скоро испортится": "⏰ Скоро испортится",
        "Фото и сканер": "📸 Фото и сканер",
        "Фото": "📸 Фото и сканер",
        "Сканер": "📸 Фото и сканер",
        "📸": "📸 Фото и сканер",
    }

    target_page = aliases.get(target_page, target_page)
    st.session_state["pending_navigation"] = target_page

    try:
        st.session_state["main_navigation"] = target_page
    except Exception:
        pass

    st.rerun()


def apply_modern_ui_v13():
    st.markdown(
        """
<style>
html, body, [data-testid="stAppViewContainer"] {
    background: #f5f8f6 !important;
}

.block-container {
    max-width: 1320px !important;
    padding-top: 1.4rem !important;
    padding-bottom: 3rem !important;
}

h1, h2, h3 {
    line-height: 1.18 !important;
    overflow: visible !important;
    padding-bottom: 0.12em !important;
    color: #123321 !important;
}

a[href^="#"] {
    display: none !important;
}

.stDeployButton,
[data-testid="stToolbar"],
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
    font-size: 1.15rem !important;
    line-height: 1.25 !important;
}

[data-testid="stSidebar"] [role="radiogroup"] label {
    padding: 8px 10px !important;
    border-radius: 14px !important;
    margin-bottom: 3px !important;
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

/* Карточки нового UI */
.medinki-hero {
    padding: 28px 30px;
    border-radius: 32px;
    background: linear-gradient(135deg, #123321 0%, #246b43 100%);
    color: white;
    box-shadow: 0 18px 46px rgba(15, 23, 42, 0.15);
    margin-bottom: 20px;
}

.medinki-hero h1 {
    color: white !important;
    margin: 0 0 10px 0;
}

.medinki-hero p {
    margin: 0;
    opacity: .92;
    font-size: 1.08rem;
}

.medinki-card {
    padding: 22px;
    border-radius: 26px;
    background: rgba(255,255,255,.94);
    border: 1px solid rgba(18,51,33,.10);
    box-shadow: 0 12px 30px rgba(15,23,42,.07);
    margin-bottom: 18px;
}

.medinki-soft {
    background: linear-gradient(135deg, #f0fff4 0%, #ffffff 100%);
}

.medinki-user-card {
    padding: 20px;
    border-radius: 24px;
    background: linear-gradient(135deg, #f0fff4 0%, #ffffff 100%);
    border: 1px solid rgba(34,197,94,.18);
    min-height: 150px;
}

.medinki-pill {
    display: inline-block;
    padding: 7px 11px;
    border-radius: 999px;
    margin: 4px 6px 0 0;
    font-weight: 800;
    font-size: .86rem;
}

.medinki-pill-blue {
    background: #dbeafe;
    color: #1d4ed8;
}

.medinki-pill-purple {
    background: #ede9fe;
    color: #6d28d9;
}

.medinki-pill-green {
    background: #dcfce7;
    color: #15803d;
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

    .medinki-hero {
        padding: 20px;
        border-radius: 24px;
    }

    .medinki-card {
        padding: 16px;
        border-radius: 22px;
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


def render_v13_fast_actions():
    st.markdown("## ⚡ Быстрые действия")

    c1, c2 = st.columns(2)

    with c1:
        if st.button("➕ Добавить еду", key="modern_fast_add_food_v13", use_container_width=True):
            modern_go("📔 Дневник питания")

        if st.button("🧊 Холодильник", key="modern_fast_fridge_v13", use_container_width=True):
            modern_go("🧊 Мой холодильник")

        if st.button("🗓️ Меню", key="modern_fast_menu_v13", use_container_width=True):
            modern_go("🗓️ Меню на неделю")

        if st.button("📸 Фото и сканер", key="modern_fast_photo_v13", use_container_width=True):
            modern_go("📸 Фото и сканер")

    with c2:
        if st.button("🛒 Добавить покупку", key="modern_fast_shopping_v13", use_container_width=True):
            modern_go("🛒 Умные покупки")

        if st.button("⏰ Скоро испортится", key="modern_fast_expiring_v13", use_container_width=True):
            modern_go("⏰ Скоро испортится")

        if st.button("📊 Аналитика", key="modern_fast_analytics_v13", use_container_width=True):
            modern_go("📊 Аналитика")

        if st.button("🍳 Рецепты", key="modern_fast_recipes_v13", use_container_width=True):
            modern_go("🍳 Рецепты")


def render_v13_clean_fast_screen():
    apply_modern_ui_v13()

    st.markdown(
        """
<div class="medinki-hero">
    <h1>🧊 Умный холодильник Мединки</h1>
    <p>Главное на сегодня: питание, покупки, холодильник, рецепты и фото-сканер.</p>
</div>
""",
        unsafe_allow_html=True,
    )

    components.html(
        """
<div style="
    font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    padding: 14px 18px;
    border-radius: 22px;
    background: linear-gradient(135deg, #fff7ed 0%, #f0fdf4 100%);
    border: 1px solid rgba(18,51,33,.10);
    color: #123321;
    font-size: 20px;
    font-weight: 800;
    margin-bottom: 12px;
">
    <span>🕒 </span><span id="medinki-clock">--:--:--</span>
</div>
<script>
function updateClock() {
    const el = document.getElementById("medinki-clock");
    if (!el) return;
    const now = new Date();
    const text = now.toLocaleDateString("ru-RU", {
        weekday: "long",
        day: "2-digit",
        month: "long"
    }) + " · " + now.toLocaleTimeString("ru-RU");
    el.innerText = text;
}
updateClock();
setInterval(updateClock, 1000);
</script>
""",
        height=78,
    )

    active_user = (
        st.session_state.get("active_user")
        or st.session_state.get("current_user")
        or st.session_state.get("user")
        or "Мишка"
    )

    st.markdown(
        f"""
<div class="medinki-card medinki-soft">
    <h2>👤 Активный пользователь: {active_user}</h2>
    <p style="margin-bottom:0;color:#475569;">Быстрые действия применяются к текущему пользователю.</p>
</div>
""",
        unsafe_allow_html=True,
    )

    st.markdown("## 🍽️ Калории сегодня")

    c1, c2 = st.columns(2)

    with c1:
        st.markdown(
            """
<div class="medinki-user-card">
    <h2>🐻 Мишка</h2>
    <span class="medinki-pill medinki-pill-blue">Цель: 2300 ккал</span>
    <span class="medinki-pill medinki-pill-purple">Съедено: —</span>
    <span class="medinki-pill medinki-pill-green">Осталось: —</span>
</div>
""",
            unsafe_allow_html=True,
        )

    with c2:
        st.markdown(
            """
<div class="medinki-user-card">
    <h2>🌸 Мединка</h2>
    <span class="medinki-pill medinki-pill-blue">Цель: 1800 ккал</span>
    <span class="medinki-pill medinki-pill-purple">Съедено: —</span>
    <span class="medinki-pill medinki-pill-green">Осталось: —</span>
</div>
""",
            unsafe_allow_html=True,
        )

    render_v13_fast_actions()

    st.markdown("## 📌 Сегодня")
    st.markdown(
        """
<div class="medinki-card">
    <h3>🥦 Рекомендации</h3>
    <p style="color:#475569;margin-bottom:0;">
        Проверь срочные продукты, добавь еду в дневник или сфотографируй новый продукт через фото-сканер.
    </p>
</div>
""",
        unsafe_allow_html=True,
    )
