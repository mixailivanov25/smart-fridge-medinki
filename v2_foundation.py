
import streamlit as st
import streamlit.components.v1 as components


V2_PAGE = "🌟 Новый интерфейс v2"


def v2_set_page(tab: str):
    st.session_state["v2_tab"] = tab
    st.session_state["pending_navigation"] = V2_PAGE
    try:
        st.session_state["main_navigation"] = V2_PAGE
    except Exception:
        pass
    st.rerun()


def v2_go_old_page(page_name: str):
    aliases = {
        "Главная": "🏠 Главная",
        "Холодильник": "🧊 Мой холодильник",
        "Мой холодильник": "🧊 Мой холодильник",
        "Фото": "📸 Фото и сканер",
        "Фото и сканер": "📸 Фото и сканер",
        "Покупки": "🛒 Умные покупки",
        "Умные покупки": "🛒 Умные покупки",
        "Аналитика": "📊 Аналитика",
        "Дневник": "📔 Дневник питания",
        "Дневник питания": "📔 Дневник питания",
        "Рецепты": "🍳 Рецепты",
        "Меню": "🗓️ Меню на неделю",
        "Меню на неделю": "🗓️ Меню на неделю",
    }
    target = aliases.get(page_name, page_name)
    st.session_state["pending_navigation"] = target
    try:
        st.session_state["main_navigation"] = target
    except Exception:
        pass
    st.rerun()


def process_v2_query_navigation():
    """
    Обработка нижней мобильной навигации:
    ?v2tab=today/fridge/scan/recipes/shopping
    """
    try:
        tab = st.query_params.get("v2tab", None)
    except Exception:
        tab = None

    if isinstance(tab, list):
        tab = tab[0] if tab else None

    allowed = {"today", "fridge", "scan", "recipes", "shopping"}

    if tab in allowed:
        last = st.session_state.get("_last_v2tab")
        st.session_state["v2_tab"] = tab
        st.session_state["pending_navigation"] = V2_PAGE
        try:
            st.session_state["main_navigation"] = V2_PAGE
        except Exception:
            pass
        st.session_state["_last_v2tab"] = tab


def apply_v2_design():
    st.markdown(
        """
<style>
:root {
    --v2-bg: #f6f8f5;
    --v2-ink: #10281c;
    --v2-muted: #647067;
    --v2-green: #1f6b43;
    --v2-green-dark: #123321;
    --v2-mint: #eafaf0;
    --v2-card: rgba(255,255,255,.94);
    --v2-border: rgba(18,51,33,.10);
    --v2-shadow: 0 18px 42px rgba(15,23,42,.09);
}

html, body, [data-testid="stAppViewContainer"] {
    background:
        radial-gradient(circle at top left, rgba(34,197,94,.08), transparent 30%),
        linear-gradient(180deg, #f8fbf8 0%, #f3f7f4 100%) !important;
}

.block-container {
    max-width: 1320px !important;
    padding-top: 1.15rem !important;
    padding-bottom: 6rem !important;
}

h1, h2, h3 {
    color: var(--v2-ink) !important;
    line-height: 1.15 !important;
    letter-spacing: -0.035em !important;
    overflow: visible !important;
}

p, span, div {
    word-break: normal !important;
}

a[href^="#"],
.stDeployButton,
[data-testid="stToolbar"] {
    display: none !important;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background:
        radial-gradient(circle at top left, rgba(34,197,94,.12), transparent 34%),
        linear-gradient(180deg, #f4fff8 0%, #ffffff 100%) !important;
    border-right: 1px solid rgba(18,51,33,.08) !important;
}

[data-testid="stSidebar"] [role="radiogroup"] {
    display: flex !important;
    flex-direction: column !important;
    gap: 5px !important;
}

[data-testid="stSidebar"] input[type="radio"] {
    display: none !important;
}

[data-testid="stSidebar"] [role="radiogroup"] svg {
    display: none !important;
}

[data-testid="stSidebar"] [role="radiogroup"] label {
    min-height: 38px !important;
    border-radius: 16px !important;
    padding: 9px 12px !important;
    margin: 0 !important;
    border: 1px solid transparent !important;
    font-weight: 750 !important;
    transition: all .15s ease !important;
}

[data-testid="stSidebar"] [role="radiogroup"] label:hover {
    background: rgba(34,197,94,.10) !important;
    transform: translateX(2px);
}

[data-testid="stSidebar"] [role="radiogroup"] label:has(input[type="radio"]:checked) {
    background: linear-gradient(135deg, rgba(34,197,94,.22), rgba(240,253,244,.96)) !important;
    border-color: rgba(34,197,94,.28) !important;
    box-shadow: 0 8px 20px rgba(15,23,42,.06) !important;
}

/* Buttons */
div.stButton > button {
    border-radius: 18px !important;
    min-height: 48px !important;
    font-weight: 800 !important;
    border: 1px solid rgba(18,51,33,.12) !important;
    box-shadow: 0 10px 24px rgba(15,23,42,.06) !important;
}

div.stButton > button:hover {
    transform: translateY(-1px);
    box-shadow: 0 14px 30px rgba(15,23,42,.11) !important;
}

/* V2 layout */
.v2-shell {
    display: flex;
    flex-direction: column;
    gap: 18px;
}

.v2-hero {
    position: relative;
    overflow: hidden;
    border-radius: 34px;
    padding: 30px;
    background:
        radial-gradient(circle at top right, rgba(255,255,255,.22), transparent 28%),
        linear-gradient(135deg, #123321 0%, #1f6b43 100%);
    color: white;
    box-shadow: 0 24px 58px rgba(15,23,42,.18);
}

.v2-hero h1 {
    color: white !important;
    margin: 0 0 10px 0 !important;
    font-size: clamp(2rem, 4vw, 3.5rem) !important;
}

.v2-hero p {
    color: rgba(255,255,255,.92) !important;
    margin: 0 !important;
    font-size: 1.08rem;
}

.v2-grid-4 {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 16px;
}

.v2-grid-3 {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 16px;
}

.v2-grid-2 {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 16px;
}

.v2-card {
    border-radius: 28px;
    padding: 22px;
    background: var(--v2-card);
    border: 1px solid var(--v2-border);
    box-shadow: var(--v2-shadow);
}

.v2-card-soft {
    background: linear-gradient(135deg, #f0fff4 0%, #ffffff 100%);
}

.v2-card-warm {
    background: linear-gradient(135deg, #fff7ed 0%, #fff 48%, #fdf2f8 100%);
}

.v2-metric {
    font-size: 2.15rem;
    font-weight: 950;
    color: var(--v2-ink);
    letter-spacing: -.04em;
}

.v2-label {
    color: var(--v2-muted);
    font-weight: 650;
    margin-top: 4px;
}

.v2-chip {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 7px 11px;
    border-radius: 999px;
    margin: 4px 5px 0 0;
    font-weight: 850;
    font-size: .86rem;
}

.v2-chip-green {
    background: #dcfce7;
    color: #166534;
}

.v2-chip-blue {
    background: #dbeafe;
    color: #1d4ed8;
}

.v2-chip-purple {
    background: #ede9fe;
    color: #6d28d9;
}

.v2-chip-orange {
    background: #ffedd5;
    color: #c2410c;
}

.v2-section-title {
    display: flex;
    align-items: center;
    gap: 12px;
    margin: 10px 0 4px 0;
}

.v2-section-title h2 {
    margin: 0 !important;
    font-size: clamp(1.55rem, 2.5vw, 2.25rem) !important;
}

.v2-icon {
    font-size: 2rem;
    line-height: 1;
}

.v2-action-card {
    cursor: pointer;
    min-height: 118px;
}

.v2-photo-placeholder {
    height: 150px;
    border-radius: 22px;
    background:
        radial-gradient(circle at top right, rgba(236,72,153,.20), transparent 35%),
        linear-gradient(135deg, #fff7ed 0%, #fdf2f8 100%);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 3.2rem;
    margin-bottom: 14px;
}

/* Bottom mobile nav */
.v2-bottom-nav {
    display: none;
}

@media (max-width: 900px) {
    .block-container {
        padding: .95rem 1rem 6.7rem 1rem !important;
    }

    .v2-grid-4,
    .v2-grid-3,
    .v2-grid-2 {
        grid-template-columns: 1fr !important;
        gap: 14px;
    }

    .v2-hero {
        border-radius: 26px;
        padding: 22px;
    }

    .v2-hero h1 {
        font-size: 2rem !important;
    }

    .v2-card {
        border-radius: 24px;
        padding: 18px;
    }

    .v2-bottom-nav {
        position: fixed;
        display: grid;
        grid-template-columns: repeat(5, 1fr);
        left: 10px;
        right: 10px;
        bottom: 10px;
        z-index: 2147483647;
        padding: 8px;
        border-radius: 26px;
        background: rgba(255,255,255,.94);
        border: 1px solid rgba(18,51,33,.12);
        box-shadow: 0 18px 48px rgba(15,23,42,.20);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        gap: 6px;
    }

    .v2-bottom-nav a {
        text-decoration: none !important;
        color: #123321 !important;
        border-radius: 19px;
        padding: 8px 4px 7px 4px;
        min-height: 48px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        gap: 2px;
        font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        font-weight: 900;
        font-size: 10px;
        line-height: 1.05;
    }

    .v2-bottom-nav a:hover {
        background: rgba(34,197,94,.12);
    }

    .v2-bottom-nav .e {
        font-size: 21px;
        line-height: 1;
    }
}
</style>
        """,
        unsafe_allow_html=True,
    )


def render_v2_bottom_nav():
    html = """
<div class="v2-bottom-nav">
    <a href="?v2tab=today" target="_self"><span class="e">🏠</span><span>Сегодня</span></a>
    <a href="?v2tab=fridge" target="_self"><span class="e">🧊</span><span>Холод.</span></a>
    <a href="?v2tab=scan" target="_self"><span class="e">📸</span><span>Сканер</span></a>
    <a href="?v2tab=recipes" target="_self"><span class="e">🍳</span><span>Рецепты</span></a>
    <a href="?v2tab=shopping" target="_self"><span class="e">🛒</span><span>Покупки</span></a>
</div>
"""
    st.markdown(html, unsafe_allow_html=True)


def render_v2_clock():
    components.html(
        """
<div style="
    font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    padding: 14px 18px;
    border-radius: 22px;
    background: rgba(255,255,255,.88);
    border: 1px solid rgba(18,51,33,.10);
    color: #123321;
    font-size: 20px;
    font-weight: 900;
">
    <span>🕒 </span><span id="v2-clock">--:--:--</span>
</div>
<script>
function updateClock() {
    const el = document.getElementById("v2-clock");
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
        height=64,
    )


def render_v2_user_cards():
    st.markdown(
        """
<div class="v2-grid-2">
    <div class="v2-card v2-card-soft">
        <h2>🐻 Мишка</h2>
        <span class="v2-chip v2-chip-green">2300 ккал/день</span>
        <span class="v2-chip v2-chip-blue">съедено: 320</span>
        <span class="v2-chip v2-chip-purple">осталось: 1980</span>
        <p class="v2-label">Фокус: белок, домашняя еда, удобное меню.</p>
    </div>
    <div class="v2-card v2-card-soft">
        <h2>🌸 Мединка</h2>
        <span class="v2-chip v2-chip-green">1800 ккал/день</span>
        <span class="v2-chip v2-chip-blue">съедено: 0</span>
        <span class="v2-chip v2-chip-purple">осталось: 1800</span>
        <p class="v2-label">Фокус: лёгкие блюда, овощи, комфортное питание.</p>
    </div>
</div>
""",
        unsafe_allow_html=True,
    )


def render_v2_today():
    st.markdown(
        """
<div class="v2-hero">
    <h1>🧊 Сегодня у Мединки</h1>
    <p>Главное на одном экране: питание, холодильник, покупки, рецепты и фото-сканер.</p>
</div>
""",
        unsafe_allow_html=True,
    )

    render_v2_clock()

    st.markdown(
        """
<div class="v2-grid-4">
    <div class="v2-card"><div class="v2-metric">12</div><div class="v2-label">продуктов дома</div></div>
    <div class="v2-card"><div class="v2-metric">2</div><div class="v2-label">требуют внимания</div></div>
    <div class="v2-card"><div class="v2-metric">1</div><div class="v2-label">блюдо можно приготовить</div></div>
    <div class="v2-card"><div class="v2-metric">3604</div><div class="v2-label">ккал в запасах</div></div>
</div>
""",
        unsafe_allow_html=True,
    )

    st.markdown('<div class="v2-section-title"><span class="v2-icon">⚡</span><h2>Быстрые действия</h2></div>', unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        if st.button("📸 Сканировать", use_container_width=True, key="v2_action_scan"):
            v2_set_page("scan")
    with c2:
        if st.button("🧊 Холодильник", use_container_width=True, key="v2_action_fridge"):
            v2_set_page("fridge")
    with c3:
        if st.button("🍳 Рецепты", use_container_width=True, key="v2_action_recipes"):
            v2_set_page("recipes")
    with c4:
        if st.button("🛒 Покупки", use_container_width=True, key="v2_action_shopping"):
            v2_set_page("shopping")

    st.markdown('<div class="v2-section-title"><span class="v2-icon">🍽️</span><h2>Питание сегодня</h2></div>', unsafe_allow_html=True)
    render_v2_user_cards()

    st.markdown(
        """
<div class="v2-card v2-card-warm">
    <h2>💡 Рекомендация дня</h2>
    <p>Используй продукты, которые скоро испортятся. Можно приготовить простое блюдо из текущих запасов и сразу списать ингредиенты.</p>
    <span class="v2-chip v2-chip-orange">умный совет</span>
    <span class="v2-chip v2-chip-green">экономия продуктов</span>
</div>
""",
        unsafe_allow_html=True,
    )


def render_v2_fridge():
    st.markdown(
        """
<div class="v2-hero">
    <h1>🧊 Холодильник</h1>
    <p>Продукты как карточки: фото, сроки, количество и быстрые действия.</p>
</div>
""",
        unsafe_allow_html=True,
    )

    st.markdown(
        """
<div class="v2-grid-3">
    <div class="v2-card">
        <div class="v2-photo-placeholder">🍊</div>
        <h2>Апельсин</h2>
        <span class="v2-chip v2-chip-green">1 шт</span>
        <span class="v2-chip v2-chip-blue">47 ккал</span>
        <span class="v2-chip v2-chip-green">годен</span>
    </div>
    <div class="v2-card">
        <div class="v2-photo-placeholder">🥩</div>
        <h2>Фарш</h2>
        <span class="v2-chip v2-chip-green">500 г</span>
        <span class="v2-chip v2-chip-blue">250 ккал</span>
        <span class="v2-chip v2-chip-orange">скоро</span>
    </div>
    <div class="v2-card">
        <div class="v2-photo-placeholder">🥕</div>
        <h2>Морковь</h2>
        <span class="v2-chip v2-chip-green">4 шт</span>
        <span class="v2-chip v2-chip-blue">41 ккал</span>
        <span class="v2-chip v2-chip-green">годен</span>
    </div>
</div>
""",
        unsafe_allow_html=True,
    )

    if st.button("Открыть старый холодильник", use_container_width=True, key="v2_old_fridge"):
        v2_go_old_page("Холодильник")


def render_v2_scan():
    st.markdown(
        """
<div class="v2-hero">
    <h1>📸 Сканер продуктов</h1>
    <p>Сфотографируй продукт с телефона, подтверди данные и добавь в холодильник.</p>
</div>
""",
        unsafe_allow_html=True,
    )

    st.markdown(
        """
<div class="v2-card v2-card-warm">
    <h2>Как будет работать</h2>
    <p>Фото продукта → AI распознаёт название, категорию, калории и срок годности → ты проверяешь форму → продукт попадает в холодильник.</p>
    <span class="v2-chip v2-chip-purple">камера</span>
    <span class="v2-chip v2-chip-blue">AI Vision</span>
    <span class="v2-chip v2-chip-green">подтверждение</span>
</div>
""",
        unsafe_allow_html=True,
    )

    if st.button("Открыть текущий фото-сканер", use_container_width=True, key="v2_old_scan"):
        v2_go_old_page("Фото и сканер")


def render_v2_recipes():
    st.markdown(
        """
<div class="v2-hero">
    <h1>🍳 Рецепты и меню</h1>
    <p>Блюда с фото, калориями, временем, историей и понятной кнопкой “готовить”.</p>
</div>
""",
        unsafe_allow_html=True,
    )

    st.markdown(
        """
<div class="v2-grid-3">
    <div class="v2-card">
        <div class="v2-photo-placeholder">🍳</div>
        <h2>Омлет</h2>
        <p>Нежный завтрак на молоке.</p>
        <span class="v2-chip v2-chip-blue">12 минут</span>
        <span class="v2-chip v2-chip-green">320 ккал</span>
    </div>
    <div class="v2-card">
        <div class="v2-photo-placeholder">🍗</div>
        <h2>Курица с рисом</h2>
        <p>Сытное домашнее блюдо.</p>
        <span class="v2-chip v2-chip-blue">35 минут</span>
        <span class="v2-chip v2-chip-green">560 ккал</span>
    </div>
    <div class="v2-card">
        <div class="v2-photo-placeholder">🥣</div>
        <h2>Овсянка</h2>
        <p>Быстрый завтрак.</p>
        <span class="v2-chip v2-chip-blue">10 минут</span>
        <span class="v2-chip v2-chip-green">350 ккал</span>
    </div>
</div>
""",
        unsafe_allow_html=True,
    )

    c1, c2 = st.columns(2)
    with c1:
        if st.button("Открыть рецепты", use_container_width=True, key="v2_old_recipes"):
            v2_go_old_page("Рецепты")
    with c2:
        if st.button("Открыть меню на неделю", use_container_width=True, key="v2_old_menu"):
            v2_go_old_page("Меню")


def render_v2_shopping():
    st.markdown(
        """
<div class="v2-hero">
    <h1>🛒 Покупки</h1>
    <p>Что купить, что уже куплено и что можно сразу перенести в холодильник.</p>
</div>
""",
        unsafe_allow_html=True,
    )

    st.markdown(
        """
<div class="v2-grid-2">
    <div class="v2-card">
        <h2>Нужно купить</h2>
        <p>Курица · 1050 г</p>
        <p>Молоко · 250 мл</p>
        <span class="v2-chip v2-chip-orange">для рецептов</span>
    </div>
    <div class="v2-card">
        <h2>Быстро добавить</h2>
        <p>Сканируй чек или добавляй продукты из каталога.</p>
        <span class="v2-chip v2-chip-green">в холодильник одной кнопкой</span>
    </div>
</div>
""",
        unsafe_allow_html=True,
    )

    if st.button("Открыть умные покупки", use_container_width=True, key="v2_old_shopping"):
        v2_go_old_page("Покупки")


def render_v2_app():
    apply_v2_design()
    render_v2_bottom_nav()

    tab = st.session_state.get("v2_tab", "today")

    st.markdown('<div class="v2-shell">', unsafe_allow_html=True)

    nav_cols = st.columns(5)
    labels = [
        ("today", "🏠 Сегодня"),
        ("fridge", "🧊 Холодильник"),
        ("scan", "📸 Сканер"),
        ("recipes", "🍳 Рецепты"),
        ("shopping", "🛒 Покупки"),
    ]

    for col, (key, label) in zip(nav_cols, labels):
        with col:
            if st.button(label, use_container_width=True, key=f"v2_top_nav_{key}"):
                v2_set_page(key)

    if tab == "fridge":
        render_v2_fridge()
    elif tab == "scan":
        render_v2_scan()
    elif tab == "recipes":
        render_v2_recipes()
    elif tab == "shopping":
        render_v2_shopping()
    else:
        render_v2_today()

    st.markdown("</div>", unsafe_allow_html=True)
