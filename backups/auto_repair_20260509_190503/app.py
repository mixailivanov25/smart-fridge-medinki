import re
from datetime import datetime, date

import pandas as pd
import streamlit as st
from media_page import render_media_page
from settings import APP_NAME, APP_VERSION, DEVELOPER, PEOPLE, NUTRITION_GOALS, APP_TAGLINE, DEFAULT_AUTH_PINS
from demo_data import load_demo_products, reset_everything_and_load_demo
from database import (
get_db_kind,
    init_db,
    add_or_update_product,
    get_products,
    get_product_by_id,
    update_product,
    reduce_product_quantity,
    delete_product,
    add_cooking_history,
    get_history,
    get_user_profiles,
    get_user_profile,
    update_user_profile,
    add_favorite_dish,
    get_favorite_dishes,
    delete_favorite_dish,
    get_product_transactions,
    get_accepted_week_menus,
    get_accepted_week_menu_items,
    ensure_v08_tables,
    add_nutrition_diary_entry,
    get_nutrition_diary_entries,
    delete_nutrition_diary_entry,
    get_daily_calories,
    add_shopping_item,
    get_shopping_items,
    delete_shopping_item,
    add_shopping_item_to_fridge,
    ensure_v09_tables,
    add_custom_recipe,
    get_custom_recipes,
    get_custom_recipe_by_id,
    delete_custom_recipe,
    get_custom_recipe_categories
)
from database import get_latest_accepted_week_menu, cancel_latest_accepted_week_menu
from recipes import get_recipe_matches, find_product, to_base_unit, get_all_recipes
from product_catalog import get_catalog_categories, get_catalog_products, default_expiration_date_for_product
from dish_catalog import get_dish_metadata, enrich_recipe, search_dish_metadata
from menu_engine import (
    get_person_emoji,
    get_person_genitive,
    build_personal_week_menu,
    build_shopping_list_for_menu,
    combine_shopping_lists,
    accept_week_menus
)

from ui_cleanup_v13 import apply_ui_cleanup_v13

def request_navigation(target_page: str):
    """
    Безопасный переход между разделами.
    """
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
        "Стресс-тест": "🧪 Стресс-тест",
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

st.set_page_config(
    page_title=APP_NAME,
    page_icon="🥦",
    layout="wide"
)


apply_ui_cleanup_v13()
@st.cache_resource
def bootstrap_database_once():
    init_db()
    ensure_v08_tables()
    ensure_v09_tables()
    return True


bootstrap_database_once()


st.markdown("""
<style>
    .main {
        background: #f7f9fb;
    }

    .block-container {
        padding-top: 1.4rem;
        padding-bottom: 3rem;
        max-width: 1220px;
    }

    .app-title {
        font-size: 42px;
        font-weight: 950;
        margin-bottom: 0;
        color: #163020;
        letter-spacing: -1px;
    }

    .app-subtitle {
        font-size: 18px;
        color: #5c6b63;
        margin-bottom: 25px;
    }

    .card, .recipe-card, .person-card, .favorite-card, .menu-day-card, .catalog-card, .dish-card {
        background: rgba(255, 255, 255, 0.97);
        padding: 22px;
        border-radius: 26px;
        border: 1px solid rgba(230, 238, 233, 0.95);
        box-shadow: 0 14px 35px rgba(22, 48, 32, 0.08);
        margin-bottom: 18px;
    }

    .gradient-card {
        background: linear-gradient(135deg, #163020, #2f6b45);
        color: white;
        padding: 28px;
        border-radius: 30px;
        box-shadow: 0 18px 45px rgba(22, 48, 32, 0.20);
        margin-bottom: 20px;
    }

    .gradient-card h3 {
        color: white;
        margin-bottom: 8px;
    }

    .soft-card {
        background: linear-gradient(135deg, #e8fff1, #ffffff);
        padding: 24px;
        border-radius: 28px;
        border: 1px solid #d7f5e2;
        box-shadow: 0 12px 30px rgba(22, 48, 32, 0.06);
        margin-bottom: 18px;
    }

    .big-number {
        font-size: 34px;
        font-weight: 950;
        color: #163020;
    }

    .small-label {
        color: #6b756e;
        font-size: 14px;
    }

    .muted {
        color: #7a857d;
    }

    .status-pill, .badge-green, .badge-yellow, .badge-red {
        display: inline-block;
        padding: 6px 12px;
        border-radius: 999px;
        font-size: 13px;
        font-weight: 800;
        margin-right: 6px;
        margin-bottom: 6px;
    }

    .badge-green, .pill-green {
        background: #e7f8ef;
        color: #147a3d;
    }

    .badge-yellow, .pill-orange {
        background: #fff2df;
        color: #a65b00;
    }

    .badge-red, .pill-red {
        background: #ffe5e5;
        color: #a11616;
    }

    .pill-blue {
        background: #e8f1ff;
        color: #1b5bbf;
    }

    .pill-purple {
        background: #f1e8ff;
        color: #6d28b8;
    }

    .pill-gray {
        background: #eef1f0;
        color: #5c6b63;
    }

    .menu-meal {
        padding: 13px 15px;
        border-radius: 18px;
        background: #f7faf8;
        margin-bottom: 10px;
        border: 1px solid #edf2ef;
    }

    .footer {
        margin-top: 45px;
        padding: 14px 18px;
        border-radius: 16px;
        background: linear-gradient(90deg, #163020, #2f6b45);
        color: white;
        font-size: 13px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.08);
    }

    .footer b {
        color: white;
    }

    .sidebar-text {
        font-size: 14px;
        color: #617067;
    }

    .emoji-big {
        font-size: 44px;
        line-height: 1;
    }


    /* -----------------------------
       v0.9.1 Mobile Polish
       ----------------------------- */

    .mobile-install-card {
        background: linear-gradient(135deg, #f1fff6, #ffffff);
        padding: 20px 22px;
        border-radius: 24px;
        border: 1px solid #d7f5e2;
        box-shadow: 0 12px 30px rgba(22, 48, 32, 0.07);
        margin-bottom: 18px;
    }

    .mobile-install-card h3 {
        margin-bottom: 8px;
        color: #163020;
    }

    .mobile-step {
        display: inline-block;
        background: #e7f8ef;
        color: #147a3d;
        padding: 6px 10px;
        border-radius: 999px;
        font-size: 13px;
        font-weight: 800;
        margin-right: 6px;
        margin-bottom: 6px;
    }

    .mobile-home-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 14px;
        margin-bottom: 18px;
    }

    .mobile-action-card {
        background: white;
        border: 1px solid #e8f3ed;
        border-radius: 22px;
        padding: 18px;
        box-shadow: 0 10px 26px rgba(22, 48, 32, 0.07);
        text-align: center;
    }

    .mobile-action-card .icon {
        font-size: 34px;
        margin-bottom: 8px;
    }

    .mobile-action-card .title {
        font-weight: 900;
        color: #163020;
        font-size: 16px;
    }

    .mobile-action-card .text {
        color: #6b756e;
        font-size: 13px;
        margin-top: 4px;
    }

    /* Make Streamlit buttons more touch-friendly */
    div.stButton > button {
        border-radius: 14px;
        min-height: 42px;
        font-weight: 700;
    }

    div.stDownloadButton > button {
        border-radius: 14px;
        min-height: 42px;
        font-weight: 700;
    }

    /* Inputs */
    div[data-baseweb="input"] {
        border-radius: 14px;
    }

    div[data-baseweb="select"] {
        border-radius: 14px;
    }

    textarea {
        border-radius: 14px !important;
    }

    /* Mobile responsive */
    @media (max-width: 768px) {
        .block-container {
            padding-left: 1rem !important;
            padding-right: 1rem !important;
            padding-top: 1rem !important;
            max-width: 100% !important;
        }

        .app-title {
            font-size: 28px !important;
            line-height: 1.12 !important;
            letter-spacing: -0.5px !important;
        }

        .app-subtitle {
            font-size: 14px !important;
            margin-bottom: 16px !important;
        }

        h1 {
            font-size: 28px !important;
        }

        h2 {
            font-size: 24px !important;
        }

        h3 {
            font-size: 20px !important;
        }

        .gradient-card {
            padding: 20px !important;
            border-radius: 22px !important;
            margin-bottom: 16px !important;
        }

        .gradient-card h3 {
            font-size: 22px !important;
        }

        .soft-card,
        .card,
        .recipe-card,
        .person-card,
        .favorite-card,
        .menu-day-card,
        .catalog-card,
        .dish-card,
        .mobile-install-card {
            padding: 16px !important;
            border-radius: 20px !important;
            margin-bottom: 14px !important;
        }

        .big-number {
            font-size: 28px !important;
        }

        .small-label {
            font-size: 13px !important;
        }

        .status-pill,
        .badge-green,
        .badge-yellow,
        .badge-red {
            font-size: 12px !important;
            padding: 5px 9px !important;
            margin-bottom: 5px !important;
        }

        .emoji-big {
            font-size: 34px !important;
        }

        .mobile-home-grid {
            grid-template-columns: 1fr !important;
            gap: 10px !important;
        }

        .mobile-action-card {
            text-align: left !important;
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 14px !important;
        }

        .mobile-action-card .icon {
            font-size: 30px !important;
            margin-bottom: 0 !important;
        }

        .menu-meal {
            padding: 11px 12px !important;
            border-radius: 16px !important;
        }

        .footer {
            font-size: 12px !important;
            padding: 12px 14px !important;
            border-radius: 14px !important;
        }

        /* Make tables less painful on mobile */
        div[data-testid="stDataFrame"] {
            overflow-x: auto !important;
            border-radius: 16px !important;
        }

        /* Larger tabs tap area */
        button[data-baseweb="tab"] {
            padding-left: 10px !important;
            padding-right: 10px !important;
            min-height: 42px !important;
            font-weight: 700 !important;
        }

        /* Sidebar radio labels */
        section[data-testid="stSidebar"] label {
            font-size: 15px !important;
            line-height: 1.4 !important;
        }

        section[data-testid="stSidebar"] {
            background: #f3f7f5 !important;
        }
    }

    @media (max-width: 480px) {
        .app-title {
            font-size: 25px !important;
        }

        .gradient-card p,
        .soft-card p,
        .mobile-install-card p {
            font-size: 14px !important;
        }

        .status-pill,
        .badge-green,
        .badge-yellow,
        .badge-red {
            display: inline-block !important;
        }
    }

</style>
""", unsafe_allow_html=True)


def normalize_unit(unit):
    aliases = {
        "гр": "г",
        "грамм": "г",
        "граммов": "г",
        "кг": "кг",
        "шт": "шт",
        "штук": "шт",
        "штука": "шт",
        "мл": "мл",
        "л": "л",
        "литр": "л",
        "литра": "л",
        "литров": "л",
    }
    unit = str(unit).lower().strip()
    return aliases.get(unit, unit)


def parse_bulk_products(text):
    products = []
    errors = []
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    pattern = r"^(.+?)\s+(\d+(?:[.,]\d+)?)\s*(г|гр|кг|шт|штук|штука|мл|л|литр|литра|литров)?$"

    for line in lines:
        match = re.match(pattern, line.lower().strip())

        if not match:
            errors.append(line)
            continue

        name = match.group(1).strip()
        quantity = float(match.group(2).replace(",", "."))
        unit = normalize_unit(match.group(3) or "шт")
        products.append({"name": name, "quantity": quantity, "unit": unit})

    return products, errors


def expiration_status(expiration_date):
    if not expiration_date:
        return "Нет даты", "green"

    try:
        exp = datetime.strptime(expiration_date, "%Y-%m-%d").date()
    except Exception:
        return "Нет даты", "green"

    days_left = (exp - date.today()).days

    if days_left < 0:
        return f"Просрочено на {abs(days_left)} дн.", "red"
    if days_left == 0:
        return "Истекает сегодня", "red"
    if days_left <= 3:
        return f"Осталось {days_left} дн.", "yellow"

    return f"Осталось {days_left} дн.", "green"


def estimate_inventory_calories(products):
    total = 0

    for product in products:
        quantity = product[2]
        unit = product[3]
        calories_per_100g = product[4] or 0
        base_amount, base_unit = to_base_unit(quantity, unit)

        if base_unit in ["г", "мл"]:
            total += (base_amount / 100) * calories_per_100g

    return round(total)


def convert_amount_to_product_unit(amount, ingredient_unit, product_unit):
    ingredient_base_amount, ingredient_base_unit = to_base_unit(amount, ingredient_unit)
    _, product_base_unit = to_base_unit(1, product_unit)

    if ingredient_base_unit != product_base_unit:
        return None

    product_unit = product_unit.lower().strip()

    if product_unit == "кг":
        return ingredient_base_amount / 1000
    if product_unit == "л":
        return ingredient_base_amount / 1000
    return ingredient_base_amount


def spend_recipe_products(recipe, products):
    spent = []

    for ingredient in recipe["ingredients"]:
        if ingredient.get("optional", False):
            continue

        product = find_product(products, ingredient["variants"])

        if not product:
            continue

        product_id = product[0]
        product_name = product[1]
        product_unit = product[3]

        amount_to_reduce = convert_amount_to_product_unit(
            ingredient["amount"],
            ingredient["unit"],
            product_unit
        )

        if amount_to_reduce is None:
            continue

        reduce_product_quantity(product_id, amount_to_reduce)
        spent.append(f"{product_name}: {round(amount_to_reduce, 2)} {product_unit}")

    return spent


def products_to_dataframe(products):
    return pd.DataFrame(
        products,
        columns=["ID", "Продукт", "Количество", "Ед.", "Ккал на 100 г", "Категория", "Срок годности"]
    )


def render_footer():
    st.markdown(f"""
    <div class="footer">
        <b>{APP_NAME}</b> · версия {APP_VERSION} · разработка: {DEVELOPER}
    </div>
    """, unsafe_allow_html=True)


def render_page_intro():
    """
    Восстановленный быстрый экран v1.3.
    Без дублей, без кнопки обновления, с живыми часами и быстрыми действиями.
    """
    from datetime import datetime
    import streamlit.components.v1 as components

    st.markdown("""
<style>
.medinki-fast-hero {
    padding: 26px 28px;
    border-radius: 30px;
    background: linear-gradient(135deg, #123321 0%, #246b43 100%);
    color: white;
    box-shadow: 0 18px 42px rgba(15, 23, 42, 0.14);
    margin-bottom: 22px;
}

.medinki-fast-hero h1 {
    color: white !important;
    margin: 0 0 10px 0;
    line-height: 1.18 !important;
}

.medinki-fast-hero p {
    margin: 0;
    opacity: .92;
    font-size: 1.06rem;
}

.medinki-card-soft {
    padding: 22px;
    border-radius: 26px;
    background: rgba(255,255,255,.92);
    border: 1px solid rgba(18, 51, 33, .10);
    box-shadow: 0 12px 30px rgba(15, 23, 42, .07);
    margin-bottom: 18px;
}

.medinki-user-card {
    padding: 20px;
    border-radius: 24px;
    background: linear-gradient(135deg, #f0fff4 0%, #ffffff 100%);
    border: 1px solid rgba(34, 197, 94, .18);
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
    .medinki-fast-hero {
        padding: 20px;
        border-radius: 24px;
    }

    .medinki-fast-hero h1 {
        font-size: 1.65rem !important;
    }

    .medinki-card-soft {
        padding: 16px;
        border-radius: 22px;
    }
}
</style>
""", unsafe_allow_html=True)

    st.markdown("""
<div class="medinki-fast-hero">
    <h1>🧊 Умный холодильник Мединки</h1>
    <p>Главное на сегодня: питание, покупки, холодильник, рецепты и фото-сканер.</p>
</div>
""", unsafe_allow_html=True)

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
<div class="medinki-card-soft">
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

    render_fast_action_buttons()

    st.markdown("## 📌 Сегодня")
    st.info("Здесь будут меню на сегодня, срочные продукты и рекомендации. Фото-сканер доступен через быстрые действия.")

def get_russian_weekday(dt):
    weekdays = [
        "понедельник",
        "вторник",
        "среда",
        "четверг",
        "пятница",
        "суббота",
        "воскресенье"
    ]

    return weekdays[dt.weekday()]


def get_russian_month(dt):
    months = [
        "января",
        "февраля",
        "марта",
        "апреля",
        "мая",
        "июня",
        "июля",
        "августа",
        "сентября",
        "октября",
        "ноября",
        "декабря"
    ]

    return months[dt.month - 1]


def render_current_datetime_card():
    now = datetime.now()

    weekday = get_russian_weekday(now)
    month = get_russian_month(now)

    date_text = f"{now.day} {month} {now.year}"
    time_text = now.strftime("%H:%M")

    st.markdown(f"""
    <div class="soft-card">
        <h3>🕒 Сегодня: {date_text}</h3>
        <p>
            <span class="status-pill pill-blue">День недели: {weekday}</span>
            <span class="status-pill pill-green">Текущее время: {time_text}</span>
            <span class="status-pill pill-purple">Версия: {APP_VERSION}</span>
        </p>
        <p class="muted">Время обновляется при перезагрузке страницы.</p>
    </div>
    """, unsafe_allow_html=True)


def render_quick_actions():
    current_person = get_current_person()
    if current_person:
        st.subheader(f"⚡ Быстрые действия · Активный пользователь: {current_person}")
    else:
        st.subheader("⚡ Быстрые действия")

    c1, c2, c3 = st.columns(3)

    with c1:
        if st.button("➕ Добавить еду в дневник", use_container_width=True):
            st.session_state["main_navigation"] = "Дневник питания"
            st.rerun()

    with c2:
        if st.button("🛒 Добавить покупку", use_container_width=True):
            st.session_state["main_navigation"] = "Умные покупки"
            st.rerun()

    with c3:
        if st.button("🧊 Открыть холодильник", use_container_width=True):
            st.session_state["main_navigation"] = "Мой холодильник"
            st.rerun()


def render_today_calorie_cards():
    today_str = str(date.today())

    st.subheader("🍽️ Калории сегодня")

    cols = st.columns(2)

    for index, person in enumerate(PEOPLE):
        profile = get_user_profile(person)

        if profile:
            target_calories = profile[1]
        else:
            target_calories = 2000

        eaten = get_daily_calories(person, today_str)
        left = target_calories - eaten
        progress = min(eaten / target_calories, 1.0) if target_calories else 0

        if left >= 0:
            status_class = "pill-green"
            status_text = f"Осталось: {left} ккал"
        else:
            status_class = "pill-red"
            status_text = f"Перебор: {abs(left)} ккал"

        with cols[index % 2]:
            st.markdown(f"""
            <div class="person-card">
                <h3>{get_person_emoji(person)} {person}</h3>
                <span class="status-pill pill-blue">Цель: {target_calories} ккал</span>
                <span class="status-pill pill-purple">Съедено: {eaten} ккал</span>
                <span class="status-pill {status_class}">{status_text}</span>
            </div>
            """, unsafe_allow_html=True)

            st.progress(progress)




def render_mobile_install_tip():
    st.markdown("""
    <div class="mobile-install-card">
        <h3>📱 Можно пользоваться как приложением</h3>
        <p>
            Так «Холодильник Мединки» будет запускаться почти как обычное приложение.
        </p>
        <span class="mobile-step">iPhone: Safari → Поделиться → На экран Домой</span>
    </div>
    """, unsafe_allow_html=True)


def render_mobile_start_cards():
    st.markdown("""
    <div class="mobile-home-grid">
        <div class="mobile-action-card">
            <div class="icon">📅</div>
            <div>
                <div class="title">Сегодня</div>
                <div class="text">План питания, калории и срочные продукты.</div>
            </div>
        </div>
        <div class="mobile-action-card">
            <div class="icon">🧊</div>
            <div>
                <div class="title">Холодильник</div>
                <div class="text">Остатки, сроки годности и продукты.</div>
            </div>
        </div>
        <div class="mobile-action-card">
            <div class="icon">🛒</div>
            <div>
                <div class="title">Покупки</div>
                <div class="text">Список покупок и перенос в холодильник.</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)




# -----------------------------
# v1.1 Auth & Family Mode
# -----------------------------
def get_auth_pins():
    """
    PIN-коды можно задать в Streamlit Secrets:
    AUTH_PIN_MISHKA = "1234"
    AUTH_PIN_MEDINKA = "5678"

    Если secrets не заданы, используются DEFAULT_AUTH_PINS из settings.py.
    """
    pins = dict(DEFAULT_AUTH_PINS)

    try:
        if "AUTH_PIN_MISHKA" in st.secrets:
            pins["Мишка"] = str(st.secrets["AUTH_PIN_MISHKA"])

        if "AUTH_PIN_MEDINKA" in st.secrets:
            pins["Мединка"] = str(st.secrets["AUTH_PIN_MEDINKA"])
    except Exception:
        pass

    return pins


def is_authenticated():
    return bool(st.session_state.get("auth_ok", False))


def get_current_person():
    return st.session_state.get("current_person", "")


def logout_user():
    st.session_state["auth_ok"] = False
    st.session_state["current_person"] = ""
    st.session_state["main_navigation"] = "Быстрый экран"


def render_login_screen():
    st.markdown(f"<div class='app-title'>🥦 {APP_NAME}</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='app-subtitle'>Семейный вход</div>",
        unsafe_allow_html=True
    )

    st.markdown("""
    <div class="gradient-card">
        <h3>🔐 Вход в приложение</h3>
        <p>
            Приложение опубликовано в интернете, поэтому мы добавили простой PIN-код,
            чтобы данные холодильника, покупок и дневника не меняли случайные люди.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="soft-card">
        <h3>👨‍👩‍👧 Вход в приложение</h3>
        <p class="muted">Введите логин и PIN-код.</p>
    </div>
    """, unsafe_allow_html=True)

    pins = get_auth_pins()

    with st.form("login_form"):
        person = st.selectbox("Логин", PEOPLE)
        pin = st.text_input("PIN-код", type="password", placeholder="Введите PIN")

        submitted = st.form_submit_button("🔓 Войти")

        if submitted:
            expected_pin = str(pins.get(person, ""))

            if pin and pin == expected_pin:
                st.session_state["auth_ok"] = True
                st.session_state["current_person"] = person
                st.session_state["main_navigation"] = "Быстрый экран"
                st.success(f"Добро пожаловать, {person}!")
                st.rerun()
            else:
                st.error("Неверный PIN-код.")

def require_auth():
    if not is_authenticated():
        render_login_screen()
        st.stop()


def render_current_user_sidebar():
    current_person = get_current_person()

    if current_person:
        st.sidebar.success(f"{get_person_emoji(current_person)} Вы вошли как: {current_person}")

        if st.sidebar.button("🚪 Выйти"):
            logout_user()
            st.rerun()




# -----------------------------
# v1.2 Speed helpers
# -----------------------------
@st.cache_data(ttl=15)
def cached_fast_products():
    return get_products()


@st.cache_data(ttl=30)
def cached_fast_profiles():
    return get_user_profiles()


@st.cache_data(ttl=15)
def cached_fast_daily_calories(person, diary_date):
    return get_daily_calories(person, diary_date)


@st.cache_data(ttl=20)
def cached_fast_recipe_matches(products_as_tuple):
    products_list = list(products_as_tuple)
    return get_recipe_matches(products_list)


def clear_app_cache():
    try:
        st.cache_data.clear()
    except Exception:
        pass

    try:
        st.cache_resource.clear()
    except Exception:
        pass


def render_speed_refresh_button(location="main"):
    pass
def get_today_name_ru():
    day_names = [
        "Понедельник",
        "Вторник",
        "Среда",
        "Четверг",
        "Пятница",
        "Суббота",
        "Воскресенье"
    ]

    return day_names[date.today().weekday()]


def get_urgent_products_for_fast_screen(products):
    urgent = []

    for product in products:
        status_text, status_color = expiration_status(product[6])

        if status_color in ["yellow", "red"]:
            urgent.append((product, status_text, status_color))

    return urgent


def render_fast_calorie_card(person):
    today_str = str(date.today())
    profile = get_user_profile(person)

    if profile:
        target = profile[1]
    else:
        target = 2000

    eaten = cached_fast_daily_calories(person, today_str)
    left = target - eaten

    progress = min(eaten / target, 1.0) if target else 0

    if left >= 0:
        status_class = "pill-green"
        status_text = f"Осталось: {left} ккал"
    else:
        status_class = "pill-red"
        status_text = f"Перебор: {abs(left)} ккал"

    st.markdown(f"""
    <div class="person-card">
        <h3>{get_person_emoji(person)} {person}</h3>
        <span class="status-pill pill-blue">Цель: {target} ккал</span>
        <span class="status-pill pill-purple">Съедено: {eaten} ккал</span>
        <span class="status-pill {status_class}">{status_text}</span>
    </div>
    """, unsafe_allow_html=True)

    st.progress(progress)


def render_fast_action_buttons():
    """
    Быстрые действия.
    """
    st.markdown("## ⚡ Быстрые действия")

    c1, c2 = st.columns(2)

    with c1:
        if st.button("➕ Добавить еду", key="fast_add_food_repair_v13", use_container_width=True):
            request_navigation("📔 Дневник питания")

        if st.button("🧊 Холодильник", key="fast_fridge_repair_v13", use_container_width=True):
            request_navigation("🧊 Мой холодильник")

        if st.button("🗓️ Меню", key="fast_menu_repair_v13", use_container_width=True):
            request_navigation("🗓️ Меню на неделю")

        if st.button("📸 Фото и сканер", key="fast_photo_repair_v13", use_container_width=True):
            request_navigation("📸 Фото и сканер")

    with c2:
        if st.button("🛒 Добавить покупку", key="fast_shopping_repair_v13", use_container_width=True):
            request_navigation("🛒 Умные покупки")

        if st.button("⏰ Скоро испортится", key="fast_expiring_repair_v13", use_container_width=True):
            request_navigation("⏰ Скоро испортится")

        if st.button("📊 Аналитика", key="fast_analytics_repair_v13", use_container_width=True):
            request_navigation("📊 Аналитика")

        if st.button("🍳 Рецепты", key="fast_recipes_repair_v13", use_container_width=True):
            request_navigation("🍳 Рецепты")

def render_person_card(profile):
    person, target_calories, goal, meals_per_day, protein_focus, preferences, dislikes, allergies, updated_at = profile
    protein_text = "Да" if protein_focus else "Нет"

    st.markdown(f"""
    <div class="person-card">
        <h3>{get_person_emoji(person)} {person}</h3>
        <p class="muted">Персональные настройки питания</p>
        <span class="status-pill pill-green">{target_calories} ккал/день</span>
        <span class="status-pill pill-blue">{goal}</span>
        <span class="status-pill pill-purple">{meals_per_day} приёма пищи</span>
        <span class="status-pill pill-orange">Белок: {protein_text}</span>
        <br><br>
        <b>Предпочтения:</b> {preferences or "не указаны"}<br>
        <b>Не любит:</b> {dislikes or "не указано"}<br>
        <b>Аллергии:</b> {allergies or "не указаны"}
    </div>
    """, unsafe_allow_html=True)


def render_favorite_card(row):
    favorite_id, person, dish_name, source, rating, notes, created_at = row
    stars = "⭐" * int(rating)

    st.markdown(f"""
    <div class="favorite-card">
        <h3>{get_person_emoji(person)} {dish_name}</h3>
        <span class="status-pill pill-purple">{person}</span>
        <span class="status-pill pill-green">{stars}</span>
        <span class="status-pill pill-blue">{source}</span>
        <p class="muted">{notes or "Без заметки"}</p>
        <p class="muted">Добавлено: {created_at}</p>
    </div>
    """, unsafe_allow_html=True)


def build_shopping_list_from_recipes(products, min_score=50):
    matches = get_recipe_matches(products)
    shopping = {}

    for item in matches:
        if item["can_make"]:
            continue
        if item["score"] < min_score:
            continue

        recipe_name = item["recipe"]["name"]

        for missing in item["missing"]:
            key = f"{missing['name']}|{missing['unit']}"
            shopping.setdefault(key, {"name": missing["name"], "amount": 0, "unit": missing["unit"], "recipes": []})
            shopping[key]["amount"] += missing["amount"]

            if recipe_name not in shopping[key]["recipes"]:
                shopping[key]["recipes"].append(recipe_name)

    return list(shopping.values())


DOWNLOAD_BUTTON_COUNTER = 0


def render_shopping_list(items):
    if not items:
        st.success("Почти ничего не нужно докупать.")
        return

    df = pd.DataFrame(items)
    df["recipes"] = df["recipes"].apply(lambda values: ", ".join(values))
    df = df.rename(columns={
        "name": "Продукт",
        "amount": "Нужно примерно",
        "unit": "Ед.",
        "recipes": "Для блюд"
    })
    st.dataframe(df, use_container_width=True, hide_index=True)

    text_lines = [f"- {item['name']}: {round(item['amount'], 2)} {item['unit']}" for item in items]
    st.code("\n".join(text_lines), language="text")

    global DOWNLOAD_BUTTON_COUNTER
    DOWNLOAD_BUTTON_COUNTER += 1

    st.download_button(
        "📥 Скачать список покупок",
        data="\n".join(text_lines),
        file_name="shopping_list_medinki.txt",
        mime="text/plain",
        key=f"download_shopping_list_{DOWNLOAD_BUTTON_COUNTER}"
    )


def render_week_menu_for_person(menu_data):
    if not menu_data:
        st.warning("Не удалось построить меню.")
        return

    person = menu_data["person"]
    profile = menu_data["profile"]
    target_calories = profile[1]

    st.markdown(f"""
    <div class="gradient-card">
        <h3>{get_person_emoji(person)} Меню {get_person_genitive(person)} на неделю</h3>
        <p>Цель: {target_calories} ккал/день · Среднее: {menu_data["avg_calories"]} ккал/день · Любимых блюд: {menu_data["favorites_used"]}</p>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric("Цель", f"{target_calories} ккал")
    with c2:
        st.metric("Среднее за неделю", f"{menu_data['avg_calories']} ккал")
    with c3:
        st.metric("Отклонение", f"{menu_data['avg_diff']} ккал")

    for day in menu_data["week"]:
        badge_class = "badge-green"
        if day["status_color"] == "yellow":
            badge_class = "badge-yellow"
        if day["status_color"] == "red":
            badge_class = "badge-red"

        st.markdown(f"""
        <div class="menu-day-card">
            <h3>{day["day"]}</h3>
            <span class="{badge_class}">{day["status"]}</span>
            <span class="status-pill pill-blue">Итого: {day["calories"]} ккал</span>
            <span class="status-pill pill-gray">Цель: {day["target_calories"]} ккал</span>
        </div>
        """, unsafe_allow_html=True)

        for meal in day["meals"]:
            recipe = meal["recipe"]
            meta = get_dish_metadata(recipe["name"])
            favorite = " ❤️" if meal["is_favorite"] else ""
            rating = f" ⭐{meal['favorite_rating']}" if meal["favorite_rating"] else ""
            can_make_badge = "pill-green" if meal["can_make"] else "pill-orange"
            can_make_text = "есть продукты" if meal["can_make"] else "нужно докупить"

            st.markdown(f"""
            <div class="menu-meal">
                <b>{meal["slot"]}:</b> {meta.get("emoji", "🍽️")} {recipe["name"]}{favorite}{rating}<br>
                <span class="status-pill pill-purple">{recipe["category"]}</span>
                <span class="status-pill pill-blue">{recipe["calories"]} ккал</span>
                <span class="status-pill {can_make_badge}">{can_make_text}</span>
            </div>
            """, unsafe_allow_html=True)


# v1.1 auth gate
require_auth()

st.sidebar.markdown(f"## 🥦 {APP_NAME}")
st.sidebar.markdown(f"<div class='sidebar-text'>{APP_TAGLINE}</div>", unsafe_allow_html=True)
st.sidebar.divider()

st.sidebar.caption(f"{APP_VERSION} · {DEVELOPER}")

render_speed_refresh_button("sidebar")

nav_labels = {
    "Быстрый экран": "📱 Быстрый экран",
    "📸 Фото и сканер": "📸 Фото и сканер",
    "Главная": "🏠 Главная",
    "Семейный режим": "👨‍👩‍👧 Семейный режим",
    "Сегодня": "📅 Сегодня",
    "Дневник питания": "📔 Дневник питания",
    "Аналитика": "📊 Аналитика",
    "Стресс-тест": "🧪 Стресс-тест",
    "Мои рецепты": "📝 Мои рецепты",
    "Умные покупки": "🛒 Умные покупки",
    "Скоро испортится": "⏰ Скоро испортится",
    "Мой холодильник": "🧊 Мой холодильник",
    "Добавить продукты": "➕ Добавить продукты",
    "Рецепты": "🍳 Рецепты",
    "Каталог блюд": "🍽️ Каталог блюд",
    "Меню на неделю": "🗓️ Меню на неделю",
    "Список покупок": "🛒 Список покупок",
    "Питание и цели": "🎯 Питание и цели",
    "Любимые блюда": "❤️ Любимые блюда",
    "История": "📜 История",
    "Списания": "📉 Списания",
    "Демо-режим": "🧪 Демо-режим",
}

# Применяем переходы от быстрых кнопок ДО создания виджета меню.
if "pending_navigation" in st.session_state:
    st.session_state["main_navigation"] = st.session_state.pop("pending_navigation")

page = st.sidebar.radio(
    "Навигация",
    list(nav_labels.keys()),
    format_func=lambda item: nav_labels[item],
    key="main_navigation"
)
products = get_products()

st.markdown(f"<div class='app-title'>🥦 {APP_NAME}</div>", unsafe_allow_html=True)
st.markdown("<div class='app-subtitle'>Холодильник, меню, рецепты, покупки и списание продуктов.</div>", unsafe_allow_html=True)




if page == "Быстрый экран":
    st.header("📱 Быстрый экран")

    current_person = get_current_person()
    today_name = get_today_name_ru()

    render_page_intro(
        "Главное на сегодня",
        "Калории, меню, покупки, холодильник и срочные продукты — всё в одном месте.",
        "📱"
    )

    render_current_datetime_card()

    render_speed_refresh_button("fast_screen_top")

    if current_person:
        st.markdown(f"""
        <div class="gradient-card">
            <h3>{get_person_emoji(current_person)} Активный пользователь: {current_person}</h3>
            <p>Сегодня: {today_name}. Быстрые действия будут удобнее для текущего пользователя.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("Активный пользователь не выбран.")

    render_fast_action_buttons()

    st.divider()

    st.subheader("🍽️ Калории сегодня")

    if current_person:
        render_fast_calorie_card(current_person)

        other_people = [person for person in PEOPLE if person != current_person]

        for person in other_people:
            render_fast_calorie_card(person)
    else:
        cols = st.columns(2)

        for index, person in enumerate(PEOPLE):
            with cols[index % 2]:
                render_fast_calorie_card(person)

    st.divider()

    st.subheader("⏰ Срочные продукты")

    try:
        fast_products = cached_fast_products()
        urgent_products = get_urgent_products_for_fast_screen(fast_products)

        if not urgent_products:
            st.success("Срочных продуктов нет.")
        else:
            for product, status_text, status_color in urgent_products[:5]:
                badge = "badge-red" if status_color == "red" else "badge-yellow"

                st.markdown(f"""
                <div class="card">
                    <h3>{product[1]}</h3>
                    <p><b>{product[2]}</b> {product[3]} · {product[5] or "Без категории"}</p>
                    <span class="{badge}">{status_text}</span>
                </div>
                """, unsafe_allow_html=True)

            if len(urgent_products) > 5:
                st.caption(f"Ещё продуктов требуют внимания: {len(urgent_products) - 5}")

    except Exception as e:
        st.error(f"Не удалось загрузить срочные продукты: {e}")

    st.divider()

    st.subheader("🗓️ Меню на сегодня")

    try:
        fast_products = cached_fast_products()

        people_to_show = [current_person] if current_person else PEOPLE

        for person in people_to_show:
            if not person:
                continue

            menu_data = build_personal_week_menu(person, fast_products)

            if not menu_data:
                st.warning(f"Не удалось построить меню для {person}.")
                continue

            day_plan = next(
                (day for day in menu_data["week"] if day["day"] == today_name),
                None
            )

            if not day_plan:
                st.info(f"На сегодня нет плана для {person}.")
                continue

            st.markdown(f"""
            <div class="menu-day-card">
                <h3>{get_person_emoji(person)} Сегодня для {get_person_genitive(person)}</h3>
                <span class="status-pill pill-blue">Итого: {day_plan["calories"]} ккал</span>
                <span class="status-pill pill-gray">Цель: {day_plan["target_calories"]} ккал</span>
                <span class="status-pill pill-green">{day_plan["status"]}</span>
            </div>
            """, unsafe_allow_html=True)

            for meal in day_plan["meals"]:
                recipe = meal["recipe"]
                meta = get_dish_metadata(recipe["name"])
                fav = "❤️" if meal["is_favorite"] else ""

                st.markdown(f"""
                <div class="menu-meal">
                    <b>{meal["slot"]}:</b> {meta.get("emoji", "🍽️")} {recipe["name"]} {fav}<br>
                    <span class="status-pill pill-blue">{recipe["calories"]} ккал</span>
                    <span class="status-pill pill-purple">{recipe["category"]}</span>
                </div>
                """, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Не удалось построить меню на сегодня: {e}")

    st.divider()

    st.caption(
    )


elif page in ("📸 Фото и сканер", "Фото и сканер", "📸"):
    render_media_page()

elif page == "Главная":
    total_products = len(products)
    expiring_count = 0

    for product in products:
        _, status_color = expiration_status(product[6])
        if status_color in ["yellow", "red"]:
            expiring_count += 1

    total_calories = estimate_inventory_calories(products)
    recipe_matches = get_recipe_matches(products)
    can_make_count = len([item for item in recipe_matches if item["can_make"]])

    st.markdown("""
    <div class="gradient-card">
        <h3>Добро пожаловать в холодильник Мединки 🥦</h3>
        <p>Здесь видно, что есть дома, что приготовить, что скоро испортится и что докупить.</p>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.markdown(f"<div class='card'><div class='big-number'>{total_products}</div><div class='small-label'>продуктов</div></div>", unsafe_allow_html=True)
    with c2:
        st.markdown(f"<div class='card'><div class='big-number'>{can_make_count}</div><div class='small-label'>блюд можно приготовить</div></div>", unsafe_allow_html=True)
    with c3:
        st.markdown(f"<div class='card'><div class='big-number'>{expiring_count}</div><div class='small-label'>требуют внимания</div></div>", unsafe_allow_html=True)
    with c4:
        st.markdown(f"<div class='card'><div class='big-number'>{total_calories}</div><div class='small-label'>ккал в запасах</div></div>", unsafe_allow_html=True)

    st.subheader("🎯 Цели питания Мишки и Мединки")

    cols = st.columns(2)
    for index, profile in enumerate(get_user_profiles()):
        with cols[index % 2]:
            render_person_card(profile)

    st.subheader("🔥 Что можно приготовить сейчас")

    best_recipes = [item for item in recipe_matches if item["can_make"]][:3]

    if not best_recipes:
        st.info("Пока нет блюд, которые можно полностью приготовить.")
    else:
        for item in best_recipes:
            recipe = item["recipe"]
            meta = get_dish_metadata(recipe["name"])
            st.markdown(f"""
            <div class="recipe-card">
                <h3>{meta.get("emoji", "🍽️")} {recipe["name"]}</h3>
                <p class="muted">{recipe["description"]}</p>
                <span class="badge-green">Можно приготовить</span>
                <span class="badge-green">{recipe["time"]}</span>
                <span class="badge-green">{recipe["calories"]} ккал</span>
            </div>
            """, unsafe_allow_html=True)






elif page == "Семейный режим":
    st.header("👨‍👩‍👧 Семейный режим")

    render_page_intro(
        "Пользователи холодильника Мединки",
        "Здесь видно, кто сейчас вошёл в приложение, можно переключить пользователя и посмотреть настройки Мишки и Мединки.",
        "👨‍👩‍👧"
    )

    current_person = get_current_person()

    if current_person:
        st.markdown(f"""
        <div class="gradient-card">
            <h3>{get_person_emoji(current_person)} Сейчас активен: {current_person}</h3>
            <p>
                Быстрые действия, дневник питания и любимые блюда можно вести от имени выбранного пользователя.
            </p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.warning("Логин не выбран.")

    st.subheader("👥 Профили")

    profiles = get_user_profiles()

    if profiles:
        cols = st.columns(2)

        for index, profile in enumerate(profiles):
            with cols[index % 2]:
                render_person_card(profile)

    st.divider()

    st.subheader("🔄 Переключить пользователя")

    st.info("Для переключения нужно ввести PIN нового пользователя.")

    pins = get_auth_pins()

    with st.form("switch_user_form"):
        new_person = st.selectbox("Кто будет пользоваться?", PEOPLE, key="switch_user_person")
        new_pin = st.text_input("PIN-код", type="password", key="switch_user_pin")

        submitted = st.form_submit_button("🔄 Переключиться")

        if submitted:
            expected_pin = str(pins.get(new_person, ""))

            if new_pin and new_pin == expected_pin:
                st.session_state["auth_ok"] = True
                st.session_state["current_person"] = new_person
                st.success(f"Теперь активен пользователь: {new_person}")
                st.rerun()
            else:
                st.error("Неверный PIN-код.")

    st.divider()

    st.subheader("🔐 Безопасность")

    st.markdown("""
    <div class="soft-card">
        <h3>Как поменять PIN-коды?</h3>
        <p>
            Откройте Streamlit Cloud → Manage app → Settings → Secrets
            и добавьте свои значения:
        </p>
        <pre>
AUTH_PIN_MISHKA = "ваш_PIN_для_Мишки"
AUTH_PIN_MEDINKA = "ваш_PIN_для_Мединки"
        </pre>
        <p class="muted">
            После сохранения secrets нужно перезапустить приложение через Reboot.
        </p>
    </div>
    """, unsafe_allow_html=True)


elif page == "Сегодня":
    st.header("📅 Сегодня")

    render_page_intro(
        "План на сегодня",
        "Здесь собраны блюда на текущий день для Мишки и Мединки, а также продукты, которые лучше использовать быстрее.",
        "📅"
    )

    if not products:
        st.info("Сначала добавьте продукты или загрузите демо-данные.")
    else:
        day_names = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]
        today_name = day_names[date.today().weekday()]

        st.subheader(f"Сегодня: {today_name}")

        menu_mishka_today = build_personal_week_menu("Мишка", products)
        menu_medinka_today = build_personal_week_menu("Мединка", products)

        today_tabs = st.tabs(["🐻 Мишка", "🌸 Мединка", "⚠️ Срочно использовать"])

        with today_tabs[0]:
            if menu_mishka_today:
                day_plan = next((day for day in menu_mishka_today["week"] if day["day"] == today_name), None)

                if day_plan:
                    st.markdown(f"""
                    <div class="gradient-card">
                        <h3>🐻 Меню Мишки на сегодня</h3>
                        <p>Итого: {day_plan["calories"]} ккал · Цель: {day_plan["target_calories"]} ккал · {day_plan["status"]}</p>
                    </div>
                    """, unsafe_allow_html=True)

                    for meal in day_plan["meals"]:
                        recipe = meal["recipe"]
                        meta = get_dish_metadata(recipe["name"])
                        fav = "❤️" if meal["is_favorite"] else ""

                        st.markdown(f"""
                        <div class="menu-meal">
                            <b>{meal["slot"]}:</b> {meta.get("emoji", "🍽️")} {recipe["name"]} {fav}<br>
                            <span class="status-pill pill-blue">{recipe["calories"]} ккал</span>
                            <span class="status-pill pill-purple">{recipe["category"]}</span>
                        </div>
                        """, unsafe_allow_html=True)

        with today_tabs[1]:
            if menu_medinka_today:
                day_plan = next((day for day in menu_medinka_today["week"] if day["day"] == today_name), None)

                if day_plan:
                    st.markdown(f"""
                    <div class="gradient-card">
                        <h3>🌸 Меню Мединки на сегодня</h3>
                        <p>Итого: {day_plan["calories"]} ккал · Цель: {day_plan["target_calories"]} ккал · {day_plan["status"]}</p>
                    </div>
                    """, unsafe_allow_html=True)

                    for meal in day_plan["meals"]:
                        recipe = meal["recipe"]
                        meta = get_dish_metadata(recipe["name"])
                        fav = "❤️" if meal["is_favorite"] else ""

                        st.markdown(f"""
                        <div class="menu-meal">
                            <b>{meal["slot"]}:</b> {meta.get("emoji", "🍽️")} {recipe["name"]} {fav}<br>
                            <span class="status-pill pill-blue">{recipe["calories"]} ккал</span>
                            <span class="status-pill pill-purple">{recipe["category"]}</span>
                        </div>
                        """, unsafe_allow_html=True)

        with today_tabs[2]:
            urgent_products = []

            for product in products:
                status_text, status_color = expiration_status(product[6])

                if status_color in ["yellow", "red"]:
                    urgent_products.append((product, status_text, status_color))

            if not urgent_products:
                st.success("Срочных продуктов нет.")
            else:
                for product, status_text, status_color in urgent_products:
                    badge = "badge-red" if status_color == "red" else "badge-yellow"

                    st.markdown(f"""
                    <div class="card">
                        <h3>{product[1]}</h3>
                        <p><b>{product[2]}</b> {product[3]} · {product[5] or "Без категории"}</p>
                        <span class="{badge}">{status_text}</span>
                    </div>
                    """, unsafe_allow_html=True)



elif page == "Скоро испортится":
    st.header("⏰ Скоро испортится")

    render_page_intro(
        "Продукты, которые лучше использовать первыми",
        "Приложение показывает продукты с коротким сроком годности и рецепты, куда их можно применить.",
        "⏰"
    )

    if not products:
        st.info("Пока продуктов нет.")
    else:
        urgent_products = []
        normal_products = []

        for product in products:
            status_text, status_color = expiration_status(product[6])

            if status_color in ["yellow", "red"]:
                urgent_products.append((product, status_text, status_color))
            else:
                normal_products.append((product, status_text, status_color))

        col1, col2 = st.columns(2)

        with col1:
            st.metric("Требуют внимания", len(urgent_products))

        with col2:
            st.metric("Остальные продукты", len(normal_products))

        if not urgent_products:
            st.success("Отлично, продуктов с критичным сроком годности нет.")
        else:
            recipe_matches = get_recipe_matches(products)

            for product, status_text, status_color in urgent_products:
                badge = "badge-red" if status_color == "red" else "badge-yellow"

                st.markdown(f"""
                <div class="card">
                    <h3>{product[1]}</h3>
                    <p><b>{product[2]}</b> {product[3]} · {product[5] or "Без категории"}</p>
                    <span class="{badge}">{status_text}</span>
                </div>
                """, unsafe_allow_html=True)

                product_name = str(product[1]).lower()

                suitable = []

                for item in recipe_matches:
                    recipe = item["recipe"]
                    haystack = recipe["name"].lower() + " " + recipe.get("description", "").lower()

                    for ingredient in recipe.get("ingredients", []):
                        haystack += " " + ingredient.get("name", "").lower()
                        haystack += " " + " ".join(ingredient.get("variants", [])).lower()

                    if product_name in haystack:
                        suitable.append(item)

                if suitable:
                    with st.expander(f"Рецепты с продуктом «{product[1]}»"):
                        for item in suitable[:5]:
                            recipe = item["recipe"]
                            meta = get_dish_metadata(recipe["name"])

                            if item["can_make"]:
                                status_badge = "<span class='badge-green'>Можно приготовить</span>"
                            else:
                                status_badge = "<span class='badge-yellow'>Нужно докупить</span>"

                            st.markdown(f"""
                            <div class="menu-meal">
                                <b>{meta.get("emoji", "🍽️")} {recipe["name"]}</b><br>
                                <span class="status-pill pill-blue">{recipe["calories"]} ккал</span>
                                <span class="status-pill pill-purple">{recipe["category"]}</span>
                                {status_badge}
                            </div>
                            """, unsafe_allow_html=True)
                else:
                    st.caption("Пока нет рецептов с этим продуктом.")




elif page == "Дневник питания":
    st.header("📔 Дневник питания")

    render_page_intro(
        "Что реально съели сегодня",
        "Записывайте блюда Мишки и Мединки, следите за калориями за день и историей питания.",
        "📔"
    )

    today_str = str(date.today())

    st.subheader("📊 Калории за сегодня")

    cols = st.columns(2)

    for index, person in enumerate(PEOPLE):
        profile = get_user_profile(person)

        if profile:
            target_calories = profile[1]
        else:
            target_calories = 2000

        eaten = get_daily_calories(person, today_str)
        left = target_calories - eaten
        progress = min(eaten / target_calories, 1.0) if target_calories else 0

        with cols[index % 2]:
            st.markdown(f"""
            <div class="person-card">
                <h3>{get_person_emoji(person)} {person}</h3>
                <span class="status-pill pill-green">Цель: {target_calories} ккал</span>
                <span class="status-pill pill-blue">Съедено: {eaten} ккал</span>
                <span class="status-pill pill-purple">Осталось: {left} ккал</span>
            </div>
            """, unsafe_allow_html=True)

            st.progress(progress)

    st.divider()

    st.subheader("➕ Добавить запись")

    recipes = get_all_recipes()
    recipe_names = [recipe["name"] for recipe in recipes]
    recipe_map = {recipe["name"]: recipe for recipe in recipes}

    with st.form("nutrition_diary_form"):
        c1, c2 = st.columns(2)

        with c1:
            person = st.selectbox("Кто", PEOPLE)
            diary_date = st.date_input("Дата", value=date.today())
            meal_slot = st.selectbox(
                "Приём пищи",
                ["Завтрак", "Обед", "Ужин", "Перекус", "Дополнительно"]
            )

        with c2:
            dish_mode = st.radio(
                "Блюдо",
                ["Выбрать из рецептов", "Ввести вручную"],
                horizontal=True
            )

            if dish_mode == "Выбрать из рецептов":
                selected_dish = st.selectbox("Блюдо из рецептов", recipe_names)
                dish_name = selected_dish
                default_calories = recipe_map[selected_dish]["calories"]
            else:
                dish_name = st.text_input("Название блюда", placeholder="Например: сырники")
                default_calories = 0

            calories = st.number_input(
                "Калории",
                min_value=0.0,
                value=float(default_calories),
                step=10.0
            )

        c3, c4, c5 = st.columns(3)

        with c3:
            protein = st.number_input("Белки, г", min_value=0.0, value=0.0, step=1.0)

        with c4:
            fat = st.number_input("Жиры, г", min_value=0.0, value=0.0, step=1.0)

        with c5:
            carbs = st.number_input("Углеводы, г", min_value=0.0, value=0.0, step=1.0)

        comment = st.text_area("Комментарий", placeholder="Например: съели половину порции")

        submitted = st.form_submit_button("➕ Добавить в дневник")

        if submitted:
            if not dish_name:
                st.error("Введите название блюда.")
            else:
                add_nutrition_diary_entry(
                    person=person,
                    diary_date=str(diary_date),
                    meal_slot=meal_slot,
                    dish_name=dish_name,
                    calories=calories,
                    protein=protein,
                    fat=fat,
                    carbs=carbs,
                    comment=comment
                )

                st.success("Запись добавлена в дневник питания.")
                st.rerun()

    st.divider()

    st.subheader("📋 Записи дневника")

    filter_col1, filter_col2 = st.columns(2)

    with filter_col1:
        filter_person = st.selectbox("Фильтр по человеку", ["Все"] + PEOPLE)

    with filter_col2:
        filter_date = st.date_input("Фильтр по дате", value=date.today(), key="diary_filter_date")

    person_arg = None if filter_person == "Все" else filter_person

    entries = get_nutrition_diary_entries(
        person=person_arg,
        diary_date=str(filter_date),
        limit=300
    )

    if not entries:
        st.info("Записей за выбранный день пока нет.")
    else:
        df = pd.DataFrame(
            entries,
            columns=[
                "ID",
                "Кто",
                "Дата",
                "Приём пищи",
                "Блюдо",
                "Калории",
                "Белки",
                "Жиры",
                "Углеводы",
                "Комментарий",
                "Создано"
            ]
        )

        st.dataframe(df, use_container_width=True, hide_index=True)

        delete_id = st.number_input(
            "ID записи для удаления",
            min_value=0,
            value=0,
            step=1
        )

        if st.button("🗑️ Удалить запись из дневника", disabled=delete_id <= 0):
            delete_nutrition_diary_entry(delete_id)
            st.success("Запись удалена.")
            st.rerun()



elif page == "Умные покупки":
    st.header("🛒 Умные покупки")

    render_page_intro(
        "Список покупок с переносом в холодильник",
        "Добавляйте продукты в список покупок, отмечайте купленное и переносите продукты в холодильник одной кнопкой.",
        "🛒"
    )

    tab1, tab2, tab3 = st.tabs(["➕ Добавить покупку", "📝 Нужно купить", "✅ Куплено"])

    with tab1:
        st.subheader("Добавить продукт в список покупок")

        mode = st.radio(
            "Как добавить?",
            ["Из каталога", "Вручную"],
            horizontal=True
        )

        if mode == "Из каталога":
            categories = ["Все категории"] + get_catalog_categories()

            c1, c2 = st.columns(2)

            with c1:
                selected_category = st.selectbox("Категория", categories, key="smart_shop_category")

            with c2:
                query = st.text_input("Поиск", placeholder="Например: молоко, яйца, курица", key="smart_shop_query")

            catalog_items = get_catalog_products(selected_category, query)

            if not catalog_items:
                st.warning("Ничего не найдено.")
            else:
                labels = [
                    f"{item['emoji']} {item['name']} · {item['category']} · {item['calories']} ккал · ед.: {item['unit']}"
                    for item in catalog_items
                ]

                selected_label = st.selectbox("Продукт", labels, key="smart_shop_product")
                selected_item = catalog_items[labels.index(selected_label)]

                st.markdown(f"""
                <div class="catalog-card">
                    <div class="emoji-big">{selected_item['emoji']}</div>
                    <h3>{selected_item['name']}</h3>
                    <p class="muted">{selected_item['description']}</p>
                    <span class="status-pill pill-blue">{selected_item['category']}</span>
                    <span class="status-pill pill-green">{selected_item['calories']} ккал на 100 г</span>
                </div>
                """, unsafe_allow_html=True)

                with st.form("smart_shopping_catalog_form"):
                    c1, c2, c3 = st.columns(3)

                    with c1:
                        amount = st.number_input("Количество", min_value=0.0, value=1.0, step=0.1)

                    with c2:
                        unit_values = ["г", "кг", "шт", "мл", "л"]
                        unit_index = unit_values.index(selected_item["unit"]) if selected_item["unit"] in unit_values else 0
                        unit = st.selectbox("Единица", unit_values, index=unit_index)

                    with c3:
                        expiration_date = st.date_input(
                            "Срок годности после покупки",
                            value=default_expiration_date_for_product(selected_item)
                        )

                    submitted = st.form_submit_button("➕ Добавить в покупки")

                    if submitted:
                        if amount <= 0:
                            st.error("Количество должно быть больше нуля.")
                        else:
                            add_shopping_item(
                                name=selected_item["name"],
                                amount=amount,
                                unit=unit,
                                category=selected_item["category"],
                                calories_per_100g=selected_item["calories"],
                                expiration_date=str(expiration_date),
                                source="catalog"
                            )

                            st.success(f"Добавлено в покупки: {selected_item['name']}")
                            st.rerun()

        else:
            with st.form("smart_shopping_manual_form"):
                c1, c2 = st.columns(2)

                with c1:
                    name = st.text_input("Название продукта")
                    amount = st.number_input("Количество", min_value=0.0, value=1.0, step=0.1)
                    unit = st.selectbox("Единица", ["г", "кг", "шт", "мл", "л"])

                with c2:
                    category = st.text_input("Категория")
                    calories = st.number_input("Ккал на 100 г", min_value=0.0, value=0.0, step=1.0)
                    expiration_date = st.date_input("Срок годности после покупки")

                submitted = st.form_submit_button("➕ Добавить в покупки")

                if submitted:
                    if not name:
                        st.error("Введите название продукта.")
                    elif amount <= 0:
                        st.error("Количество должно быть больше нуля.")
                    else:
                        add_shopping_item(
                            name=name,
                            amount=amount,
                            unit=unit,
                            category=category,
                            calories_per_100g=calories,
                            expiration_date=str(expiration_date),
                            source="manual"
                        )

                        st.success(f"Добавлено в покупки: {name}")
                        st.rerun()

    with tab2:
        st.subheader("Что нужно купить")

        items = get_shopping_items(include_bought=False)

        if not items:
            st.success("Список покупок пуст.")
        else:
            df = pd.DataFrame(
                items,
                columns=[
                    "ID",
                    "Продукт",
                    "Количество",
                    "Ед.",
                    "Категория",
                    "Ккал на 100 г",
                    "Срок годности",
                    "Источник",
                    "Куплено",
                    "Создано",
                    "Куплено в"
                ]
            )

            st.dataframe(df, use_container_width=True, hide_index=True)

            st.write("### Быстрые действия")

            for item in items:
                (
                    item_id,
                    name,
                    amount,
                    unit,
                    category,
                    calories,
                    expiration_date,
                    source,
                    is_bought,
                    created_at,
                    bought_at
                ) = item

                with st.expander(f"{name} — {amount} {unit}"):
                    st.write(f"Категория: {category or 'не указана'}")
                    st.write(f"Ккал на 100 г: {calories or 0}")
                    st.write(f"Срок годности после покупки: {expiration_date or 'не указан'}")

                    c1, c2 = st.columns(2)

                    with c1:
                        if st.button(
                            "✅ Куплено и добавить в холодильник",
                            key=f"buy_to_fridge_{item_id}"
                        ):
                            result = add_shopping_item_to_fridge(item_id)

                            if result["ok"]:
                                st.success(result["message"])
                                st.rerun()
                            else:
                                st.error(result["message"])

                    with c2:
                        if st.button(
                            "🗑️ Удалить из покупок",
                            key=f"delete_shopping_{item_id}"
                        ):
                            delete_shopping_item(item_id)
                            st.success("Позиция удалена.")
                            st.rerun()

    with tab3:
        st.subheader("Купленные продукты")

        items = get_shopping_items(include_bought=True)
        bought = [item for item in items if item[8] == 1]

        if not bought:
            st.info("Купленных позиций пока нет.")
        else:
            df = pd.DataFrame(
                bought,
                columns=[
                    "ID",
                    "Продукт",
                    "Количество",
                    "Ед.",
                    "Категория",
                    "Ккал на 100 г",
                    "Срок годности",
                    "Источник",
                    "Куплено",
                    "Создано",
                    "Куплено в"
                ]
            )

            st.dataframe(df, use_container_width=True, hide_index=True)




elif page == "Аналитика":
    st.header("📊 Аналитика")

    render_page_intro(
        "Сводка по питанию, покупкам и холодильнику",
        "Здесь собраны ключевые показатели: калории, дневник, история готовки, списания и покупки.",
        "📊"
    )

    today_str = str(date.today())

    st.subheader("🍽️ Калории за сегодня")

    calorie_rows = []

    for person in PEOPLE:
        profile = get_user_profile(person)
        target = profile[1] if profile else 2000
        eaten = get_daily_calories(person, today_str)
        left = target - eaten

        calorie_rows.append({
            "Кто": person,
            "Цель": target,
            "Съедено": eaten,
            "Осталось": left,
            "Выполнено %": round((eaten / target) * 100) if target else 0
        })

    st.dataframe(pd.DataFrame(calorie_rows), use_container_width=True, hide_index=True)

    c1, c2, c3, c4 = st.columns(4)

    history = get_history()
    transactions = get_product_transactions()
    shopping_items = get_shopping_items(include_bought=True)
    diary_today = get_nutrition_diary_entries(diary_date=today_str, limit=500)

    with c1:
        st.metric("Записей в дневнике сегодня", len(diary_today))

    with c2:
        st.metric("Блюд в истории", len(history))

    with c3:
        st.metric("Операций списания/покупок", len(transactions))

    with c4:
        bought_count = len([item for item in shopping_items if item[8] == 1])
        st.metric("Купленных позиций", bought_count)

    st.divider()

    tab1, tab2, tab3, tab4 = st.tabs([
        "📔 Дневник",
        "📜 История блюд",
        "📉 Списания",
        "🛒 Покупки"
    ])

    with tab1:
        st.subheader("Дневник питания за сегодня")

        if not diary_today:
            st.info("Сегодня ещё нет записей в дневнике.")
        else:
            df = pd.DataFrame(
                diary_today,
                columns=[
                    "ID",
                    "Кто",
                    "Дата",
                    "Приём пищи",
                    "Блюдо",
                    "Калории",
                    "Белки",
                    "Жиры",
                    "Углеводы",
                    "Комментарий",
                    "Создано"
                ]
            )

            st.dataframe(df, use_container_width=True, hide_index=True)

    with tab2:
        st.subheader("История приготовленных блюд")

        if not history:
            st.info("История пока пустая.")
        else:
            df = pd.DataFrame(
                history,
                columns=["Блюдо", "Списано", "Калории", "Дата"]
            )

            st.dataframe(df.head(30), use_container_width=True, hide_index=True)

    with tab3:
        st.subheader("Последние операции с продуктами")

        if not transactions:
            st.info("Операций пока нет.")
        else:
            df = pd.DataFrame(
                transactions,
                columns=[
                    "ID",
                    "Product ID",
                    "Продукт",
                    "Изменение",
                    "Ед.",
                    "Действие",
                    "Причина",
                    "Блюдо",
                    "Кто",
                    "День",
                    "Приём",
                    "Дата"
                ]
            )

            st.dataframe(df.head(50), use_container_width=True, hide_index=True)

    with tab4:
        st.subheader("Покупки")

        if not shopping_items:
            st.info("Список покупок пуст.")
        else:
            df = pd.DataFrame(
                shopping_items,
                columns=[
                    "ID",
                    "Продукт",
                    "Количество",
                    "Ед.",
                    "Категория",
                    "Ккал на 100 г",
                    "Срок годности",
                    "Источник",
                    "Куплено",
                    "Создано",
                    "Куплено в"
                ]
            )

            st.dataframe(df.head(50), use_container_width=True, hide_index=True)




elif page == "Мои рецепты":
    st.header("📝 Мои рецепты")

    render_page_intro(
        "Собственная книга рецептов",
        "Добавляйте свои блюда, сохраняйте ингредиенты, шаги приготовления, калории, БЖУ, историю блюда и заметки.",
        "📝"
    )

    tab1, tab2, tab3 = st.tabs(["➕ Добавить рецепт", "📚 Мои рецепты", "❤️ В избранное / дневник"])

    with tab1:
        st.subheader("Добавить новый рецепт")

        with st.form("custom_recipe_form"):
            c1, c2 = st.columns(2)

            with c1:
                name = st.text_input("Название блюда", placeholder="Например: сырники Мединки")
                emoji = st.text_input("Иконка", value="🍽️")
                category = st.selectbox(
                    "Категория",
                    ["Завтрак", "Обед", "Ужин", "Перекус", "Салат", "Суп", "Десерт", "Другое"]
                )
                cooking_time = st.text_input("Время приготовления", placeholder="Например: 25 минут")

            with c2:
                calories = st.number_input("Калории", min_value=0.0, value=0.0, step=10.0)
                protein = st.number_input("Белки, г", min_value=0.0, value=0.0, step=1.0)
                fat = st.number_input("Жиры, г", min_value=0.0, value=0.0, step=1.0)
                carbs = st.number_input("Углеводы, г", min_value=0.0, value=0.0, step=1.0)

            ingredients_text = st.text_area(
                "Ингредиенты",
                height=140,
                placeholder="Например:\nтворог — 300 г\nяйцо — 1 шт\nмука — 50 г"
            )

            instructions_text = st.text_area(
                "Шаги приготовления",
                height=160,
                placeholder="Например:\n1. Смешать ингредиенты\n2. Сформировать сырники\n3. Обжарить на сковороде"
            )

            c3, c4 = st.columns(2)

            with c3:
                origin = st.text_input("Происхождение / кухня", placeholder="Например: домашняя кухня")

            with c4:
                history_text = st.text_area(
                    "История блюда",
                    placeholder="Например: семейный рецепт, который часто готовим на завтрак"
                )

            notes = st.text_area("Заметки", placeholder="Например: Мединке нравится со сметаной, Мишке — с мёдом")

            submitted = st.form_submit_button("💾 Сохранить рецепт")

            if submitted:
                if not name.strip():
                    st.error("Введите название блюда.")
                else:
                    add_custom_recipe(
                        name=name,
                        category=category,
                        cooking_time=cooking_time,
                        calories=calories,
                        protein=protein,
                        fat=fat,
                        carbs=carbs,
                        ingredients_text=ingredients_text,
                        instructions_text=instructions_text,
                        history=history_text,
                        origin=origin,
                        notes=notes,
                        emoji=emoji
                    )

                    st.success(f"Рецепт «{name}» сохранён.")
                    st.rerun()

    with tab2:
        st.subheader("Список моих рецептов")

        c1, c2 = st.columns(2)

        with c1:
            query = st.text_input("Поиск по рецептам", placeholder="Например: сырники, курица, завтрак")

        with c2:
            categories = ["Все категории"] + get_custom_recipe_categories()
            selected_category = st.selectbox("Категория", categories)

        recipes = get_custom_recipes(query=query, category=selected_category)

        if not recipes:
            st.info("Своих рецептов пока нет.")
        else:
            cols = st.columns(2)

            for index, recipe in enumerate(recipes):
                (
                    recipe_id,
                    name,
                    category,
                    cooking_time,
                    calories,
                    protein,
                    fat,
                    carbs,
                    ingredients_text,
                    instructions_text,
                    history_text,
                    origin,
                    notes,
                    emoji,
                    created_at
                ) = recipe

                with cols[index % 2]:
                    st.markdown(f"""
                    <div class="dish-card">
                        <div class="emoji-big">{emoji or "🍽️"}</div>
                        <h3>{name}</h3>
                        <span class="status-pill pill-purple">{category or "Без категории"}</span>
                        <span class="status-pill pill-blue">{cooking_time or "Время не указано"}</span>
                        <span class="status-pill pill-green">{calories or 0} ккал</span>
                        <br><br>
                        <b>БЖУ:</b> белки {protein or 0} г · жиры {fat or 0} г · углеводы {carbs or 0} г<br>
                        <b>Происхождение:</b> {origin or "не указано"}<br>
                        <p class="muted">{notes or ""}</p>
                    </div>
                    """, unsafe_allow_html=True)

                    with st.expander(f"Подробнее: {name}"):
                        st.write("### Ингредиенты")
                        st.text(ingredients_text or "Ингредиенты не указаны")

                        st.write("### Приготовление")
                        st.text(instructions_text or "Шаги не указаны")

                        st.write("### История блюда")
                        st.write(history_text or "История не указана")

                        st.write("### Заметки")
                        st.write(notes or "Заметок нет")

                        if st.button("🗑️ Удалить рецепт", key=f"delete_custom_recipe_{recipe_id}"):
                            delete_custom_recipe(recipe_id)
                            st.success("Рецепт удалён.")
                            st.rerun()

    with tab3:
        st.subheader("Добавить свой рецепт в дневник или любимые")

        recipes = get_custom_recipes()

        if not recipes:
            st.info("Сначала добавьте хотя бы один свой рецепт.")
        else:
            recipe_labels = [
                f"{row[0]} — {row[13] or '🍽️'} {row[1]} · {row[2]} · {row[4]} ккал"
                for row in recipes
            ]

            selected_label = st.selectbox("Выберите рецепт", recipe_labels)
            selected_id = int(selected_label.split(" — ")[0])
            recipe = get_custom_recipe_by_id(selected_id)

            if recipe:
                (
                    recipe_id,
                    name,
                    category,
                    cooking_time,
                    calories,
                    protein,
                    fat,
                    carbs,
                    ingredients_text,
                    instructions_text,
                    history_text,
                    origin,
                    notes,
                    emoji,
                    created_at
                ) = recipe

                st.markdown(f"""
                <div class="dish-card">
                    <div class="emoji-big">{emoji or "🍽️"}</div>
                    <h3>{name}</h3>
                    <span class="status-pill pill-purple">{category or "Без категории"}</span>
                    <span class="status-pill pill-blue">{cooking_time or "Время не указано"}</span>
                    <span class="status-pill pill-green">{calories or 0} ккал</span>
                </div>
                """, unsafe_allow_html=True)

                action_tabs = st.tabs(["📔 В дневник питания", "❤️ В любимые блюда"])

                with action_tabs[0]:
                    with st.form("custom_recipe_to_diary_form"):
                        c1, c2 = st.columns(2)

                        with c1:
                            person = st.selectbox("Кто", PEOPLE, key="custom_recipe_diary_person")
                            diary_date = st.date_input("Дата", value=date.today(), key="custom_recipe_diary_date")
                            meal_slot = st.selectbox(
                                "Приём пищи",
                                ["Завтрак", "Обед", "Ужин", "Перекус", "Дополнительно"],
                                key="custom_recipe_diary_slot"
                            )

                        with c2:
                            diary_calories = st.number_input(
                                "Калории",
                                min_value=0.0,
                                value=float(calories or 0),
                                step=10.0,
                                key="custom_recipe_diary_calories"
                            )
                            diary_protein = st.number_input(
                                "Белки",
                                min_value=0.0,
                                value=float(protein or 0),
                                step=1.0,
                                key="custom_recipe_diary_protein"
                            )
                            diary_fat = st.number_input(
                                "Жиры",
                                min_value=0.0,
                                value=float(fat or 0),
                                step=1.0,
                                key="custom_recipe_diary_fat"
                            )
                            diary_carbs = st.number_input(
                                "Углеводы",
                                min_value=0.0,
                                value=float(carbs or 0),
                                step=1.0,
                                key="custom_recipe_diary_carbs"
                            )

                        comment = st.text_area("Комментарий", value=notes or "", key="custom_recipe_diary_comment")

                        submitted = st.form_submit_button("➕ Добавить в дневник питания")

                        if submitted:
                            add_nutrition_diary_entry(
                                person=person,
                                diary_date=str(diary_date),
                                meal_slot=meal_slot,
                                dish_name=name,
                                calories=diary_calories,
                                protein=diary_protein,
                                fat=diary_fat,
                                carbs=diary_carbs,
                                comment=comment
                            )

                            st.success(f"«{name}» добавлено в дневник питания.")
                            st.rerun()

                with action_tabs[1]:
                    with st.form("custom_recipe_to_favorites_form"):
                        person = st.selectbox("Для кого добавить в любимые", PEOPLE, key="custom_recipe_favorite_person")
                        rating = st.slider("Оценка", min_value=1, max_value=5, value=5, key="custom_recipe_favorite_rating")
                        fav_notes = st.text_area("Заметка", value=notes or "", key="custom_recipe_favorite_notes")

                        submitted = st.form_submit_button("❤️ Добавить в любимые")

                        if submitted:
                            add_favorite_dish(
                                person=person,
                                dish_name=name,
                                source="custom_recipe",
                                rating=rating,
                                notes=fav_notes
                            )

                            st.success(f"«{name}» добавлено в любимые блюда {get_person_genitive(person)}.")
                            st.rerun()




elif page == "Стресс-тест":
    st.header("🧪 Стресс-тест приложения")

    render_page_intro(
        "Проверка связок приложения, облака и базы данных",
        "Этот раздел проверяет ключевые функции: базу данных, холодильник, дневник, покупки, любимые блюда, свои рецепты, меню и историю.",
        "🧪"
    )

    st.warning(
        "Стресс-тест создаёт временные записи с префиксом __stress_test__ "
        "и затем пытается их удалить. Тест не принимает недельное меню и не списывает реальные продукты."
    )

    def add_result(results, name, ok, details=""):
        results.append({
            "Проверка": name,
            "Статус": "✅ OK" if ok else "❌ Ошибка",
            "Детали": details
        })

    def cleanup_products_by_name(product_name):
        deleted = 0

        for product in get_products():
            if str(product[1]).lower().strip() == product_name.lower().strip():
                delete_product(product[0])
                deleted += 1

        return deleted

    def cleanup_shopping_by_name(product_name):
        deleted = 0

        try:
            items = get_shopping_items(include_bought=True)

            for item in items:
                if str(item[1]).lower().strip() == product_name.lower().strip():
                    delete_shopping_item(item[0])
                    deleted += 1
        except Exception:
            pass

        return deleted

    def cleanup_diary_by_dish(dish_name):
        deleted = 0

        try:
            entries = get_nutrition_diary_entries(limit=1000)

            for entry in entries:
                if str(entry[4]).lower().strip() == dish_name.lower().strip():
                    delete_nutrition_diary_entry(entry[0])
                    deleted += 1
        except Exception:
            pass

        return deleted

    def cleanup_favorites_by_dish(dish_name):
        deleted = 0

        try:
            favorites = get_favorite_dishes()

            for favorite in favorites:
                if str(favorite[2]).lower().strip() == dish_name.lower().strip():
                    delete_favorite_dish(favorite[0])
                    deleted += 1
        except Exception:
            pass

        return deleted

    def cleanup_custom_recipes_by_name(recipe_name):
        deleted = 0

        try:
            recipes = get_custom_recipes(query=recipe_name)

            for recipe in recipes:
                if str(recipe[1]).lower().strip() == recipe_name.lower().strip():
                    delete_custom_recipe(recipe[0])
                    deleted += 1
        except Exception:
            pass

        return deleted

    def run_stress_test():
        results = []

        suffix = datetime.now().strftime("%Y%m%d_%H%M%S")
        test_product = f"__stress_test_product_{suffix}"
        test_dish = f"__stress_test_dish_{suffix}"
        test_recipe = f"__stress_test_recipe_{suffix}"
        today_str = str(date.today())

        # 1. DB kind
        try:
            db_kind = get_db_kind()
            add_result(results, "Тип базы данных", True, db_kind)
        except Exception as e:
            add_result(results, "Тип базы данных", False, str(e))

        # 2. Products read
        try:
            products_before = get_products()
            add_result(results, "Чтение холодильника", True, f"Продуктов: {len(products_before)}")
        except Exception as e:
            add_result(results, "Чтение холодильника", False, str(e))

        # 3. Product create/read/delete
        try:
            add_or_update_product(
                name=test_product,
                quantity=1,
                unit="шт",
                calories_per_100g=10,
                category="Стресс-тест",
                expiration_date=today_str
            )

            found = [
                product for product in get_products()
                if str(product[1]).lower().strip() == test_product.lower().strip()
            ]

            if not found:
                raise RuntimeError("Тестовый продукт не найден после добавления")

            deleted = cleanup_products_by_name(test_product)

            add_result(
                results,
                "Добавление/удаление продукта",
                True,
                f"Создано: {len(found)}, удалено: {deleted}"
            )
        except Exception as e:
            add_result(results, "Добавление/удаление продукта", False, str(e))

        # 4. Nutrition diary
        try:
            add_nutrition_diary_entry(
                person="Мишка",
                diary_date=today_str,
                meal_slot="Перекус",
                dish_name=test_dish,
                calories=123,
                protein=1,
                fat=2,
                carbs=3,
                comment="stress test"
            )

            entries = get_nutrition_diary_entries(
                person="Мишка",
                diary_date=today_str,
                limit=500
            )

            found = [
                entry for entry in entries
                if str(entry[4]).lower().strip() == test_dish.lower().strip()
            ]

            if not found:
                raise RuntimeError("Запись дневника не найдена после добавления")

            deleted = cleanup_diary_by_dish(test_dish)

            add_result(
                results,
                "Дневник питания",
                True,
                f"Создано: {len(found)}, удалено: {deleted}"
            )
        except Exception as e:
            add_result(results, "Дневник питания", False, str(e))

        # 5. Smart shopping
        try:
            add_shopping_item(
                name=test_product,
                amount=2,
                unit="шт",
                category="Стресс-тест",
                calories_per_100g=10,
                expiration_date=today_str,
                source="stress_test"
            )

            items = get_shopping_items(include_bought=True)

            found = [
                item for item in items
                if str(item[1]).lower().strip() == test_product.lower().strip()
            ]

            if not found:
                raise RuntimeError("Покупка не найдена после добавления")

            deleted = cleanup_shopping_by_name(test_product)

            add_result(
                results,
                "Умные покупки",
                True,
                f"Создано: {len(found)}, удалено: {deleted}"
            )
        except Exception as e:
            add_result(results, "Умные покупки", False, str(e))

        # 6. Favorites
        try:
            add_favorite_dish(
                person="Мишка",
                dish_name=test_dish,
                source="stress_test",
                rating=5,
                notes="stress test"
            )

            favorites = get_favorite_dishes("Мишка")

            found = [
                favorite for favorite in favorites
                if str(favorite[2]).lower().strip() == test_dish.lower().strip()
            ]

            if not found:
                raise RuntimeError("Любимое блюдо не найдено после добавления")

            deleted = cleanup_favorites_by_dish(test_dish)

            add_result(
                results,
                "Любимые блюда",
                True,
                f"Создано: {len(found)}, удалено: {deleted}"
            )
        except Exception as e:
            add_result(results, "Любимые блюда", False, str(e))

        # 7. Custom recipes
        try:
            add_custom_recipe(
                name=test_recipe,
                category="Стресс-тест",
                cooking_time="1 минута",
                calories=111,
                protein=1,
                fat=1,
                carbs=1,
                ingredients_text="тестовый ингредиент",
                instructions_text="тестовый шаг",
                history="тестовая история",
                origin="стресс-тест",
                notes="stress test",
                emoji="🧪"
            )

            recipes = get_custom_recipes(query=test_recipe)

            found = [
                recipe for recipe in recipes
                if str(recipe[1]).lower().strip() == test_recipe.lower().strip()
            ]

            if not found:
                raise RuntimeError("Свой рецепт не найден после добавления")

            deleted = cleanup_custom_recipes_by_name(test_recipe)

            add_result(
                results,
                "Мои рецепты",
                True,
                f"Создано: {len(found)}, удалено: {deleted}"
            )
        except Exception as e:
            add_result(results, "Мои рецепты", False, str(e))

        # 8. Menu build
        try:
            current_products = get_products()

            menu_mishka = build_personal_week_menu("Мишка", current_products)
            menu_medinka = build_personal_week_menu("Мединка", current_products)

            if not menu_mishka or not menu_medinka:
                raise RuntimeError("Меню для одного из пользователей не построилось")

            add_result(
                results,
                "Построение меню",
                True,
                f"Мишка: {len(menu_mishka['week'])} дней, Мединка: {len(menu_medinka['week'])} дней"
            )
        except Exception as e:
            add_result(results, "Построение меню", False, str(e))

        # 9. Shopping list for menu
        try:
            current_products = get_products()
            menu_mishka = build_personal_week_menu("Мишка", current_products)
            menu_medinka = build_personal_week_menu("Мединка", current_products)

            shopping_mishka = build_shopping_list_for_menu(menu_mishka, current_products)
            shopping_medinka = build_shopping_list_for_menu(menu_medinka, current_products)

            add_result(
                results,
                "Список покупок для меню",
                True,
                f"Мишка: {len(shopping_mishka)}, Мединка: {len(shopping_medinka)}"
            )
        except Exception as e:
            add_result(results, "Список покупок для меню", False, str(e))

        # 10. History read
        try:
            history = get_history()
            add_result(results, "История блюд", True, f"Записей: {len(history)}")
        except Exception as e:
            add_result(results, "История блюд", False, str(e))

        # 11. Transactions read
        try:
            transactions = get_product_transactions()
            add_result(results, "Списания/транзакции", True, f"Записей: {len(transactions)}")
        except Exception as e:
            add_result(results, "Списания/транзакции", False, str(e))

        # 12. Accepted menus read
        try:
            accepted_menus = get_accepted_week_menus()
            add_result(results, "Принятые меню", True, f"Записей: {len(accepted_menus)}")
        except Exception as e:
            add_result(results, "Принятые меню", False, str(e))

        return results

    st.subheader("🚦 Быстрая проверка")

    col1, col2, col3 = st.columns(3)

    with col1:
        try:
            st.metric("База", get_db_kind())
        except Exception:
            st.metric("База", "ошибка")

    with col2:
        try:
            st.metric("Продуктов", len(get_products()))
        except Exception:
            st.metric("Продуктов", "ошибка")

    with col3:
        try:
            st.metric("Записей истории", len(get_history()))
        except Exception:
            st.metric("История", "ошибка")

    st.divider()

    if st.button("🧪 Запустить стресс-тест", use_container_width=True):
        with st.spinner("Проверяю приложение, облако и базу данных..."):
            results = run_stress_test()

        df = pd.DataFrame(results)

        st.dataframe(df, use_container_width=True, hide_index=True)

        errors = [row for row in results if not row["Статус"].startswith("✅")]

        if errors:
            st.error(f"Найдены ошибки: {len(errors)}")
            st.write("Ошибки:")
            st.dataframe(pd.DataFrame(errors), use_container_width=True, hide_index=True)
        else:
            st.success("Все базовые связки прошли стресс-тест ✅")

    st.divider()

    st.subheader("📱 Почему мобильная версия может тормозить")

    st.markdown("""
    Возможные причины:

    - бесплатный Streamlit Cloud может «засыпать», первый запуск после паузы медленный;
    - Supabase находится в другом регионе, запросы идут дольше;
    - Streamlit перерисовывает страницу после каждого действия;
    - мобильный интернет может быть медленнее Wi-Fi.

    Что уже оптимизировано:

    - инициализация базы теперь кэшируется через `st.cache_resource`;
    - стресс-тест проверяет Supabase изнутри облачного приложения.

    Что можно сделать дальше:

    - добавить кэширование чтения продуктов и рецептов на 10–30 секунд;
    - сделать главную страницу легче;
    - вынести тяжёлые таблицы в отдельные вкладки;
    - подключить сервис, который будет держать Streamlit Cloud «проснувшимся».
    """)


elif page == "Мой холодильник":
    st.header("🧊 Мой холодильник")

    if not products:
        st.info("Пока продуктов нет.")
    else:
        tab1, tab2, tab3 = st.tabs(["Таблица", "Карточки", "Редактировать"])

        with tab1:
            st.dataframe(products_to_dataframe(products), use_container_width=True, hide_index=True)

        with tab2:
            cols = st.columns(3)

            for index, product in enumerate(products):
                product_id, name, quantity, unit, calories, category, exp_date = product
                status_text, status_color = expiration_status(exp_date)
                badge_class = "badge-green"
                if status_color == "yellow":
                    badge_class = "badge-yellow"
                if status_color == "red":
                    badge_class = "badge-red"

                with cols[index % 3]:
                    st.markdown(f"""
                    <div class="card">
                        <h3>{name}</h3>
                        <p><b>{quantity}</b> {unit}</p>
                        <p class="muted">{category or "Без категории"}</p>
                        <p class="muted">{calories or 0} ккал на 100 г</p>
                        <span class="{badge_class}">{status_text}</span>
                    </div>
                    """, unsafe_allow_html=True)

        with tab3:
            product_options = {f"{product[0]} — {product[1]} ({product[2]} {product[3]})": product[0] for product in products}
            selected = st.selectbox("Выберите продукт", list(product_options.keys()))
            selected_id = product_options[selected]
            selected_product = get_product_by_id(selected_id)

            if selected_product:
                with st.form("edit_product_form"):
                    name = st.text_input("Название", value=selected_product[1])
                    quantity = st.number_input("Количество", min_value=0.0, value=float(selected_product[2]), step=0.1)

                    unit_values = ["г", "кг", "шт", "мл", "л"]
                    unit_index = unit_values.index(selected_product[3]) if selected_product[3] in unit_values else 0
                    unit = st.selectbox("Единица", unit_values, index=unit_index)

                    calories = st.number_input("Ккал на 100 г", min_value=0.0, value=float(selected_product[4] or 0), step=1.0)
                    category = st.text_input("Категория", value=selected_product[5] or "")
                    expiration_date = st.text_input("Срок годности YYYY-MM-DD", value=selected_product[6] or "")

                    c1, c2 = st.columns(2)

                    save_clicked = c1.form_submit_button("💾 Сохранить")
                    delete_clicked = c2.form_submit_button("🗑️ Удалить")

                    if save_clicked:
                        update_product(selected_id, name, quantity, unit, calories, category, expiration_date)
                        st.success("Продукт обновлён.")
                        st.rerun()

                    if delete_clicked:
                        delete_product(selected_id)
                        st.success("Продукт удалён.")
                        st.rerun()


elif page == "Добавить продукты":
    st.header("➕ Добавить продукты")

    tab1, tab2, tab3 = st.tabs(["Каталог", "Один продукт", "Списком"])

    with tab1:
        render_page_intro("Каталог продуктов", "Выберите продукт из каталога, укажите количество и срок годности.", "🧺")

        categories = ["Все категории"] + get_catalog_categories()
        c1, c2 = st.columns(2)

        with c1:
            selected_category = st.selectbox("Категория", categories)
        with c2:
            catalog_query = st.text_input("Поиск", placeholder="Например: курица, рис, творог")

        catalog_items = get_catalog_products(selected_category, catalog_query)

        if not catalog_items:
            st.warning("Ничего не найдено.")
        else:
            product_labels = [
                f"{item['emoji']} {item['name']} · {item['category']} · {item['calories']} ккал · ед.: {item['unit']}"
                for item in catalog_items
            ]

            selected_label = st.selectbox("Продукт", product_labels)
            selected_item = catalog_items[product_labels.index(selected_label)]

            st.markdown(f"""
            <div class="catalog-card">
                <div class="emoji-big">{selected_item['emoji']}</div>
                <h3>{selected_item['name']}</h3>
                <p class="muted">{selected_item['description']}</p>
                <span class="status-pill pill-blue">{selected_item['category']}</span>
                <span class="status-pill pill-green">{selected_item['calories']} ккал на 100 г</span>
                <span class="status-pill pill-purple">хранение ~{selected_item['storage_days']} дн.</span>
            </div>
            """, unsafe_allow_html=True)

            with st.form("catalog_add_form"):
                c1, c2, c3 = st.columns(3)

                with c1:
                    quantity = st.number_input("Количество", min_value=0.0, step=0.1, value=1.0)
                with c2:
                    unit_values = ["г", "кг", "шт", "мл", "л"]
                    unit_index = unit_values.index(selected_item["unit"]) if selected_item["unit"] in unit_values else 0
                    unit = st.selectbox("Единица", unit_values, index=unit_index)
                with c3:
                    expiration_date = st.date_input("Срок годности", value=default_expiration_date_for_product(selected_item))

                submitted = st.form_submit_button("➕ Добавить из каталога")

                if submitted:
                    if quantity <= 0:
                        st.error("Количество должно быть больше нуля.")
                    else:
                        add_or_update_product(
                            selected_item["name"],
                            quantity,
                            unit,
                            selected_item["calories"],
                            selected_item["category"],
                            str(expiration_date)
                        )
                        st.success(f"Добавлено: {selected_item['name']}")
                        st.rerun()

        with st.expander("Посмотреть каталог таблицей"):
            st.dataframe(pd.DataFrame(catalog_items), use_container_width=True, hide_index=True)

    with tab2:
        with st.form("add_single_product_form"):
            c1, c2 = st.columns(2)

            with c1:
                name = st.text_input("Название продукта", placeholder="Например: яйца")
                quantity = st.number_input("Количество", min_value=0.0, step=0.1)
                unit = st.selectbox("Единица измерения", ["г", "кг", "шт", "мл", "л"])
            with c2:
                calories = st.number_input("Ккал на 100 г", min_value=0.0, step=1.0)
                category = st.text_input("Категория", placeholder="Например: молочные продукты")
                expiration_date = st.date_input("Срок годности")

            submitted = st.form_submit_button("Добавить продукт")

            if submitted:
                if not name:
                    st.error("Введите название продукта.")
                elif quantity <= 0:
                    st.error("Количество должно быть больше нуля.")
                else:
                    add_or_update_product(name, quantity, unit, calories, category, str(expiration_date))
                    st.success(f"Продукт «{name}» добавлен.")
                    st.rerun()

    with tab3:
        st.markdown("""
        Формат списка:

        ```text
        яйца 10 шт
        молоко 1 л
        картофель 2 кг
        курица 800 г
        ```
        """)

        bulk_text = st.text_area("Список продуктов", height=220)
        default_category = st.text_input("Категория для этих продуктов", value="")
        default_calories = st.number_input("Ккал на 100 г по умолчанию", min_value=0.0, step=1.0)
        default_expiration = st.date_input("Срок годности для этих продуктов")

        if st.button("Разобрать список"):
            parsed, errors = parse_bulk_products(bulk_text)

            if parsed:
                st.success(f"Распознано продуктов: {len(parsed)}")
                st.dataframe(pd.DataFrame(parsed), use_container_width=True, hide_index=True)
                st.session_state["parsed_products"] = parsed
                st.session_state["bulk_category"] = default_category
                st.session_state["bulk_calories"] = default_calories
                st.session_state["bulk_expiration"] = str(default_expiration)

            if errors:
                st.warning("Не удалось распознать строки:")
                for error in errors:
                    st.write(f"- {error}")

        if "parsed_products" in st.session_state:
            if st.button("✅ Добавить распознанные продукты"):
                for item in st.session_state["parsed_products"]:
                    add_or_update_product(
                        item["name"],
                        item["quantity"],
                        item["unit"],
                        st.session_state.get("bulk_calories", 0),
                        st.session_state.get("bulk_category", ""),
                        st.session_state.get("bulk_expiration", "")
                    )

                del st.session_state["parsed_products"]
                st.success("Продукты добавлены.")
                st.rerun()


elif page == "Рецепты":
    st.header("🍳 Рецепты из того, что есть")

    if not products:
        st.info("Сначала добавьте продукты.")
    else:
        matches = get_recipe_matches(products)

        c1, c2 = st.columns([1, 2])

        with c1:
            only_available = st.checkbox("Только то, что можно приготовить", value=False)
        with c2:
            min_match = st.slider("Минимальное совпадение", 0, 100, 0, 10)

        filtered_matches = []
        for item in matches:
            if only_available and not item["can_make"]:
                continue
            if item["score"] < min_match:
                continue
            filtered_matches.append(item)

        for item in filtered_matches:
            recipe = item["recipe"]
            meta = get_dish_metadata(recipe["name"])

            st.markdown(f"""
            <div class="recipe-card">
                <h3>{meta.get("emoji", "🍽️")} {recipe["name"]}</h3>
                <p class="muted">{recipe["description"]}</p>
                <span class="status-pill pill-purple">{recipe["category"]}</span>
                <span class="status-pill pill-blue">{recipe["time"]}</span>
                <span class="status-pill pill-green">{recipe["calories"]} ккал</span>
            </div>
            """, unsafe_allow_html=True)

            c1, c2, c3, c4 = st.columns(4)

            with c1:
                st.metric("Совпадение", f"{item['score']}%")
            with c2:
                st.metric("Время", recipe["time"])
            with c3:
                st.metric("Калории", f"{recipe['calories']} ккал")
            with c4:
                if item["can_make"]:
                    st.markdown("<span class='badge-green'>Можно приготовить</span>", unsafe_allow_html=True)
                else:
                    st.markdown("<span class='badge-yellow'>Нужно докупить</span>", unsafe_allow_html=True)

            st.progress(item["score"] / 100)

            with st.expander("Ингредиенты, рецепт и история блюда"):
                st.write("### Ингредиенты")
                for ingredient in recipe["ingredients"]:
                    optional = " — опционально" if ingredient.get("optional", False) else ""
                    st.write(f"- {ingredient['name']}: {ingredient['amount']} {ingredient['unit']}{optional}")

                if item["missing"]:
                    st.write("### Не хватает")
                    for missing in item["missing"]:
                        st.write(f"- {missing['name']}: {missing['amount']} {missing['unit']} ({missing['reason']})")

                st.write("### Как готовить")
                for index, step in enumerate(recipe["instructions"], start=1):
                    st.write(f"{index}. {step}")

                st.write("### История блюда")
                st.write(meta.get("history", "История блюда пока не заполнена."))
                st.write(f"**Происхождение:** {meta.get('origin', '')}")
                st.write(f"**Где популярно:** {meta.get('where_popular', '')}")
                st.write(f"**Интересный факт:** {meta.get('interesting_fact', '')}")

            cook_clicked = st.button(
                f"✅ Я приготовил: {recipe['name']}",
                key=f"cook_{recipe['name']}",
                disabled=not item["can_make"]
            )

            if cook_clicked:
                current_products = get_products()
                spent = spend_recipe_products(recipe, current_products)
                ingredients_used = ", ".join(spent) if spent else "Ингредиенты не списаны"
                add_cooking_history(recipe["name"], ingredients_used, recipe["calories"])
                st.success("Блюдо добавлено в историю, продукты списаны.")
                st.rerun()

            st.divider()


elif page == "Каталог блюд":
    st.header("🍽️ Каталог блюд")

    render_page_intro(
        "Блюда, история и идеи",
        "Здесь собраны блюда с описанием, происхождением, интересными фактами и связью с рецептами.",
        "🍽️"
    )

    query = st.text_input("Поиск по блюдам", placeholder="Например: омлет, курица, Греция")
    recipes = get_all_recipes()
    recipe_map = {recipe["name"]: recipe for recipe in recipes}

    if query:
        names = [item["name"] for item in search_dish_metadata(query)]
        visible_recipes = [recipe for recipe in recipes if query.lower() in recipe["name"].lower() or recipe["name"] in names]
    else:
        visible_recipes = recipes

    cols = st.columns(2)

    for index, recipe in enumerate(visible_recipes):
        meta = get_dish_metadata(recipe["name"])
        with cols[index % 2]:
            st.markdown(f"""
            <div class="dish-card">
                <div class="emoji-big">{meta.get("emoji", "🍽️")}</div>
                <h3>{recipe["name"]}</h3>
                <p class="muted">{recipe["description"]}</p>
                <span class="status-pill pill-purple">{recipe["category"]}</span>
                <span class="status-pill pill-blue">{recipe["time"]}</span>
                <span class="status-pill pill-green">{recipe["calories"]} ккал</span>
                <br><br>
                <b>Происхождение:</b> {meta.get("origin", "")}<br>
                <b>Где популярно:</b> {meta.get("where_popular", "")}<br>
                <b>Факт:</b> {meta.get("interesting_fact", "")}
            </div>
            """, unsafe_allow_html=True)


elif page == "Меню на неделю":
    st.header("🗓️ Меню на неделю")

    if not products:
        st.info("Сначала добавьте продукты.")
    else:
        menu_mishka = build_personal_week_menu("Мишка", products)
        menu_medinka = build_personal_week_menu("Мединка", products)

        tabs = st.tabs(["🐻 Меню Мишки", "🌸 Меню Мединки", "🛒 Покупки для меню", "✅ Принять меню", "📊 Принятые меню"])

        with tabs[0]:
            render_week_menu_for_person(menu_mishka)

        with tabs[1]:
            render_week_menu_for_person(menu_medinka)

        shopping_mishka = build_shopping_list_for_menu(menu_mishka, products)
        shopping_medinka = build_shopping_list_for_menu(menu_medinka, products)
        shopping_all = combine_shopping_lists(shopping_mishka, shopping_medinka)

        with tabs[2]:
            sub1, sub2, sub3 = st.tabs(["Для Мишки", "Для Мединки", "Общий список"])

            with sub1:
                st.write("### Что докупить для меню Мишки")
                render_shopping_list(shopping_mishka)

            with sub2:
                st.write("### Что докупить для меню Мединки")
                render_shopping_list(shopping_medinka)

            with sub3:
                st.write("### Общий список покупок")
                render_shopping_list(shopping_all)

        with tabs[3]:
            render_page_intro(
                "Принять меню и списать продукты",
                "После принятия меню продукты будут списаны из холодильника за меню Мишки и Мединки. Действие нельзя отменить автоматически.",
                "✅"
            )

            if shopping_all:
                st.warning("Для меню не хватает некоторых продуктов. Можно принять меню, но часть ингредиентов не спишется полностью.")
                render_shopping_list(shopping_all)
            else:
                st.success("Для меню достаточно продуктов.")

            latest_menu = get_latest_accepted_week_menu()
            already_accepted_today = False

            if latest_menu:
                latest_menu_id, latest_title, latest_status, latest_notes, latest_accepted_at = latest_menu

                try:
                    latest_date = datetime.fromisoformat(latest_accepted_at).date()
                    already_accepted_today = latest_date == date.today()
                except Exception:
                    already_accepted_today = False

                if already_accepted_today:
                    st.warning(
                        f"Сегодня уже было принято меню: ID {latest_menu_id}. "
                        "Если принять меню повторно, продукты спишутся ещё раз."
                    )

            confirm = st.checkbox("Я понимаю, что продукты будут списаны из холодильника")
            repeat_accept_confirm = True

            if already_accepted_today:
                repeat_accept_confirm = st.checkbox("Я точно хочу принять меню повторно сегодня")

            notes = st.text_area("Заметка к меню", placeholder="Например: меню на следующую неделю")

            accept_disabled = not confirm or not repeat_accept_confirm

            if st.button("✅ Принять меню на неделю и списать продукты", disabled=accept_disabled):
                report = accept_week_menus(
                    menu_mishka=menu_mishka,
                    menu_medinka=menu_medinka,
                    title="Меню Мишки и Мединки на неделю",
                    notes=notes
                )

                st.success(f"Меню принято. ID меню: {report['menu_id']}. Сохранено блюд: {report['items_saved']}.")

                if report["spent"]:
                    st.write("### Списано")
                    st.dataframe(pd.DataFrame(report["spent"]), use_container_width=True, hide_index=True)

                if report["missing"]:
                    st.write("### Не хватило")
                    st.dataframe(pd.DataFrame(report["missing"]), use_container_width=True, hide_index=True)

                st.info("Холодильник обновлён. История и списания сохранены.")

        with tabs[4]:
            st.subheader("↩️ Управление принятыми меню")

            latest_menu = get_latest_accepted_week_menu()

            if latest_menu:
                latest_menu_id, latest_title, latest_status, latest_notes, latest_accepted_at = latest_menu

                st.info(
                    f"Последнее активное меню: ID {latest_menu_id} · "
                    f"{latest_title} · принято: {latest_accepted_at}"
                )

                cancel_confirm = st.checkbox(
                    "Я понимаю, что отмена вернёт продукты по последнему принятому меню",
                    key="cancel_latest_menu_confirm"
                )

                if st.button("↩️ Отменить последнее принятое меню", disabled=not cancel_confirm):
                    cancel_report = cancel_latest_accepted_week_menu()

                    if cancel_report["ok"]:
                        st.success(cancel_report["message"])

                        if cancel_report["returned"]:
                            st.write("### Возвращено в холодильник")
                            st.dataframe(
                                pd.DataFrame(cancel_report["returned"]),
                                use_container_width=True,
                                hide_index=True
                            )

                        st.info("Откройте «Мой холодильник» и «Списания», чтобы проверить изменения.")
                        st.rerun()
                    else:
                        st.warning(cancel_report["message"])
            else:
                st.info("Активных принятых меню для отмены нет.")

            st.divider()

            menus = get_accepted_week_menus()

            if not menus:
                st.info("Принятых меню пока нет.")
            else:
                st.dataframe(
                    pd.DataFrame(menus, columns=["ID", "Название", "Статус", "Заметка", "Дата"]),
                    use_container_width=True,
                    hide_index=True
                )

                selected_menu_id = st.selectbox("Посмотреть состав меню", [row[0] for row in menus])
                items = get_accepted_week_menu_items(selected_menu_id)

                if items:
                    st.dataframe(
                        pd.DataFrame(items, columns=["ID", "Menu ID", "Кто", "День", "Приём пищи", "Блюдо", "Ккал", "Любимое", "Дата"]),
                        use_container_width=True,
                        hide_index=True
                    )


elif page == "Список покупок":
    st.header("🛒 Список покупок")

    render_page_intro("Умный список недостающих продуктов", "Приложение смотрит на рецепты и собирает продукты, которых не хватает.", "🛒")

    if not products:
        st.info("Сначала добавьте продукты или включите демо-режим.")
    else:
        min_score = st.slider("Учитывать рецепты с совпадением от", 0, 100, 50, 10)
        shopping_list = build_shopping_list_from_recipes(products, min_score=min_score)
        render_shopping_list(shopping_list)


elif page == "Питание и цели":
    st.header("🎯 Питание и цели")

    render_page_intro(
        "Персональные цели Мишки и Мединки",
        "Задаём калории, цель питания, количество приёмов пищи, предпочтения, нелюбимые продукты и аллергии.",
        "🎯"
    )

    profiles = get_user_profiles()
    cols = st.columns(2)

    for index, profile in enumerate(profiles):
        with cols[index % 2]:
            render_person_card(profile)

    st.divider()

    for person in PEOPLE:
        profile = get_user_profile(person)

        if profile:
            _, target_calories, goal, meals_per_day, protein_focus, preferences, dislikes, allergies, _ = profile
        else:
            target_calories = 2000
            goal = "Поддержание веса"
            meals_per_day = 3
            protein_focus = 0
            preferences = ""
            dislikes = ""
            allergies = ""

        with st.expander(f"{get_person_emoji(person)} Настройки {get_person_genitive(person)}", expanded=True):
            with st.form(f"profile_form_{person}"):
                c1, c2 = st.columns(2)

                with c1:
                    new_target_calories = st.number_input("Цель по калориям в день", min_value=1000, max_value=5000, value=int(target_calories), step=50, key=f"calories_{person}")
                    goal_index = NUTRITION_GOALS.index(goal) if goal in NUTRITION_GOALS else 1
                    new_goal = st.selectbox("Цель питания", NUTRITION_GOALS, index=goal_index, key=f"goal_{person}")
                    new_meals_per_day = st.number_input("Приёмов пищи в день", min_value=1, max_value=5, value=int(meals_per_day), step=1, key=f"meals_{person}")
                    new_protein_focus = st.checkbox("Сделать упор на белок", value=bool(protein_focus), key=f"protein_{person}")

                with c2:
                    new_preferences = st.text_area("Любимые продукты / предпочтения", value=preferences or "", key=f"preferences_{person}")
                    new_dislikes = st.text_area("Что не любит", value=dislikes or "", key=f"dislikes_{person}")
                    new_allergies = st.text_area("Аллергии / ограничения", value=allergies or "", key=f"allergies_{person}")

                submitted = st.form_submit_button(f"💾 Сохранить настройки {get_person_genitive(person)}")

                if submitted:
                    update_user_profile(person, new_target_calories, new_goal, new_meals_per_day, new_protein_focus, new_preferences, new_dislikes, new_allergies)
                    st.success(f"Настройки {get_person_genitive(person)} сохранены.")
                    st.rerun()


elif page == "Любимые блюда":
    st.header("❤️ Любимые блюда")

    render_page_intro("Любимые блюда Мишки и Мединки", "Меню на неделю учитывает любимые блюда и оценки.", "❤️")

    all_recipes = get_all_recipes()
    recipe_names = [recipe["name"] for recipe in all_recipes]
    tabs = st.tabs([f"{get_person_emoji(person)} {person}" for person in PEOPLE])

    for tab, person in zip(tabs, PEOPLE):
        with tab:
            with st.form(f"favorite_form_{person}"):
                source_type = st.radio("Как добавить блюдо?", ["Выбрать из рецептов", "Добавить своё"], horizontal=True, key=f"favorite_source_{person}")

                if source_type == "Выбрать из рецептов":
                    dish_name_input = st.selectbox("Блюдо из рецептов", recipe_names, key=f"favorite_recipe_{person}")
                    source = "recipe"
                else:
                    dish_name_input = st.text_input("Название своего блюда", placeholder="Например: сырники, борщ, паста с курицей", key=f"favorite_custom_{person}")
                    source = "custom"

                rating = st.slider("Оценка блюда", min_value=1, max_value=5, value=5, key=f"favorite_rating_{person}")
                notes = st.text_area("Заметка", placeholder="Например: готовить без лука, любит с сыром", key=f"favorite_notes_{person}")

                submitted = st.form_submit_button(f"❤️ Добавить для {get_person_genitive(person)}")

                if submitted:
                    dish_name = dish_name_input.strip()

                    if not dish_name:
                        st.error("Введите название блюда.")
                    else:
                        add_favorite_dish(person, dish_name, source, rating, notes)
                        st.success(f"Блюдо «{dish_name}» добавлено для {get_person_genitive(person)}.")
                        st.rerun()

            st.divider()

            favorites = get_favorite_dishes(person)

            if not favorites:
                st.info(f"У {get_person_genitive(person)} пока нет любимых блюд.")
            else:
                for favorite in favorites:
                    render_favorite_card(favorite)

                    if st.button(f"🗑️ Удалить: {favorite[2]}", key=f"delete_favorite_{favorite[0]}"):
                        delete_favorite_dish(favorite[0])
                        st.success("Блюдо удалено.")
                        st.rerun()


elif page == "История":
    st.header("📜 История приготовленных блюд")

    history = get_history()

    if not history:
        st.info("История пока пустая.")
    else:
        df = pd.DataFrame(history, columns=["Блюдо", "Списано", "Калории", "Дата"])
        st.dataframe(df, use_container_width=True, hide_index=True)

        c1, c2 = st.columns(2)
        with c1:
            st.metric("Приготовлено блюд", len(history))
        with c2:
            st.metric("Калорий по истории", f"{sum([row[2] or 0 for row in history])} ккал")


elif page == "Списания":
    st.header("📉 Списания продуктов")

    transactions = get_product_transactions()

    if not transactions:
        st.info("Списаний пока нет.")
    else:
        df = pd.DataFrame(
            transactions,
            columns=["ID", "Product ID", "Продукт", "Изменение", "Ед.", "Действие", "Причина", "Блюдо", "Кто", "День", "Приём", "Дата"]
        )
        st.dataframe(df, use_container_width=True, hide_index=True)


elif page == "Демо-режим":
    st.header("🧪 Демо-режим")

    render_page_intro("Проверка приложения", "Можно быстро наполнить холодильник продуктами, целями и любимыми блюдами.", "🧪")

    c1, c2 = st.columns(2)

    with c1:
        st.markdown("<div class='card'><h3>Добавить демо-продукты</h3><p>Продукты добавятся к тем, что уже есть.</p></div>", unsafe_allow_html=True)
        if st.button("➕ Добавить демо-продукты"):
            count = load_demo_products(reset=False)
            st.success(f"Добавлено демо-продуктов: {count}")
            st.rerun()

    with c2:
        st.markdown("<div class='card'><h3>Очистить и загрузить демо</h3><p>Удалит продукты, историю, списания и любимые блюда.</p></div>", unsafe_allow_html=True)
        if st.button("♻️ Очистить всё и загрузить демо"):
            count = reset_everything_and_load_demo()
            st.success(f"База очищена. Загружено демо-продуктов: {count}")
            st.rerun()


render_footer()
