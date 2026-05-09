import os
import io
import base64
from datetime import date, datetime, timedelta

import pandas as pd
import streamlit as st
from sqlalchemy import create_engine, text


try:
    from v2_catalog_data import PRODUCT_CATALOG, PRODUCT_CATEGORIES, RECIPE_CATALOG, default_products_for_seed
except Exception:
    PRODUCT_CATALOG = [
        {
            "name": "апельсин",
            "emoji": "🍊",
            "category": "Фрукты",
            "unit": "шт",
            "calories_per_100g": 47,
            "protein": 0.9,
            "fat": 0.1,
            "carbs": 11.8,
            "storage_days": 14,
            "description": "Цитрус для перекуса и сока.",
        },
        {
            "name": "куриная грудка",
            "emoji": "🍗",
            "category": "Мясо и птица",
            "unit": "г",
            "calories_per_100g": 165,
            "protein": 31,
            "fat": 3.6,
            "carbs": 0,
            "storage_days": 3,
            "description": "Нежирный белок.",
        },
        {
            "name": "рис",
            "emoji": "🍚",
            "category": "Крупы и паста",
            "unit": "г",
            "calories_per_100g": 344,
            "protein": 6.7,
            "fat": 0.7,
            "carbs": 78,
            "storage_days": 365,
            "description": "Базовый гарнир.",
        },
    ]
    PRODUCT_CATEGORIES = sorted({x["category"] for x in PRODUCT_CATALOG})
    RECIPE_CATALOG = [
        {
            "name": "Омлет",
            "emoji": "🍳",
            "category": "Завтрак",
            "time": "12 минут",
            "calories": 320,
            "description": "Нежный омлет на молоке.",
            "ingredients": "яйца, молоко, соль",
        },
        {
            "name": "Курица с рисом",
            "emoji": "🍗",
            "category": "Обед",
            "time": "35 минут",
            "calories": 560,
            "description": "Сытное домашнее блюдо.",
            "ingredients": "курица, рис, морковь, лук",
        },
    ]

    def default_products_for_seed(limit=20):
        result = []
        for item in PRODUCT_CATALOG[:limit]:
            result.append((
                item["name"],
                1,
                item["unit"],
                item["calories_per_100g"],
                item["category"],
                date.today() + timedelta(days=item["storage_days"]),
                item["emoji"],
            ))
        return result


APP_NAME = "Умный холодильник Мединки"
APP_VERSION = "v2.0"
DEVELOPER = "Иванов Михаил"

USERS = {
    "Мишка": {
        "emoji": "🐻",
        "goal": 2300,
        "description": "Домашняя еда, белок, сытное меню.",
    },
    "Мединка": {
        "emoji": "🌸",
        "goal": 1800,
        "description": "Лёгкие блюда, овощи, комфортное питание.",
    },
}

DEFAULT_PRODUCTS = default_products_for_seed(limit=12)
DEFAULT_RECIPES = RECIPE_CATALOG


st.set_page_config(
    page_title=APP_NAME,
    page_icon="🥦",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =========================
# Database
# =========================

def get_secret(name: str, default=None):
    try:
        if name in st.secrets:
            return st.secrets[name]
    except Exception:
        pass
    return os.environ.get(name, default)


@st.cache_resource
def get_engine():
    database_url = get_secret("DATABASE_URL")

    if not database_url:
        database_url = "sqlite:///smart_fridge.db"

    kwargs = {"pool_pre_ping": True}

    if database_url.startswith("sqlite"):
        kwargs["connect_args"] = {"check_same_thread": False}

    return create_engine(database_url, **kwargs)


def is_postgres():
    return get_engine().dialect.name.startswith("postgres")


def ensure_schema():
    engine = get_engine()

    with engine.begin() as conn:
        if is_postgres():
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS products (
                    id SERIAL PRIMARY KEY,
                    name TEXT NOT NULL,
                    quantity DOUBLE PRECISION DEFAULT 0,
                    unit TEXT DEFAULT 'шт',
                    calories_per_100g DOUBLE PRECISION DEFAULT 0,
                    category TEXT DEFAULT 'Другое',
                    expiration_date DATE,
                    emoji TEXT DEFAULT '🧺',
                    image_data TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))

            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS shopping_items (
                    id SERIAL PRIMARY KEY,
                    name TEXT NOT NULL,
                    quantity DOUBLE PRECISION DEFAULT 1,
                    unit TEXT DEFAULT 'шт',
                    category TEXT DEFAULT 'Другое',
                    status TEXT DEFAULT 'need',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))

            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS nutrition_diary (
                    id SERIAL PRIMARY KEY,
                    person TEXT,
                    date DATE,
                    meal TEXT,
                    dish TEXT,
                    calories DOUBLE PRECISION DEFAULT 0,
                    protein DOUBLE PRECISION DEFAULT 0,
                    fat DOUBLE PRECISION DEFAULT 0,
                    carbs DOUBLE PRECISION DEFAULT 0,
                    comment TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))

            for sql in [
                "ALTER TABLE products ADD COLUMN IF NOT EXISTS emoji TEXT DEFAULT '🧺'",
                "ALTER TABLE products ADD COLUMN IF NOT EXISTS image_data TEXT",
                "ALTER TABLE shopping_items ADD COLUMN IF NOT EXISTS status TEXT DEFAULT 'need'",
            ]:
                try:
                    conn.execute(text(sql))
                except Exception:
                    pass
        else:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    quantity REAL DEFAULT 0,
                    unit TEXT DEFAULT 'шт',
                    calories_per_100g REAL DEFAULT 0,
                    category TEXT DEFAULT 'Другое',
                    expiration_date TEXT,
                    emoji TEXT DEFAULT '🧺',
                    image_data TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """))

            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS shopping_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    quantity REAL DEFAULT 1,
                    unit TEXT DEFAULT 'шт',
                    category TEXT DEFAULT 'Другое',
                    status TEXT DEFAULT 'need',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """))

            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS nutrition_diary (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    person TEXT,
                    date TEXT,
                    meal TEXT,
                    dish TEXT,
                    calories REAL DEFAULT 0,
                    protein REAL DEFAULT 0,
                    fat REAL DEFAULT 0,
                    carbs REAL DEFAULT 0,
                    comment TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """))

            for table_name, columns in {
                "products": [
                    ("emoji", "TEXT DEFAULT '🧺'"),
                    ("image_data", "TEXT"),
                ],
                "shopping_items": [
                    ("status", "TEXT DEFAULT 'need'"),
                ],
            }.items():
                try:
                    cols = conn.execute(text(f"PRAGMA table_info({table_name})")).fetchall()
                    col_names = {row[1] for row in cols}

                    for col_name, col_type in columns:
                        if col_name not in col_names:
                            conn.execute(text(f"ALTER TABLE {table_name} ADD COLUMN {col_name} {col_type}"))
                except Exception:
                    pass


def execute(sql, params=None):
    ensure_schema()
    with get_engine().begin() as conn:
        conn.execute(text(sql), params or {})


def query_rows(sql, params=None):
    ensure_schema()
    with get_engine().begin() as conn:
        rows = conn.execute(text(sql), params or {}).mappings().all()
    return [dict(row) for row in rows]


def seed_if_empty():
    ensure_schema()

    with get_engine().begin() as conn:
        count = conn.execute(text("SELECT COUNT(*) FROM products")).scalar() or 0

        if count > 0:
            return

        for name, quantity, unit, calories, category, exp, emoji in DEFAULT_PRODUCTS:
            conn.execute(
                text("""
                    INSERT INTO products
                        (name, quantity, unit, calories_per_100g, category, expiration_date, emoji, created_at)
                    VALUES
                        (:name, :quantity, :unit, :calories, :category, :expiration_date, :emoji, CURRENT_TIMESTAMP)
                """),
                {
                    "name": name,
                    "quantity": quantity,
                    "unit": unit,
                    "calories": calories,
                    "category": category,
                    "expiration_date": str(exp),
                    "emoji": emoji,
                },
            )


def get_products():
    return query_rows("""
        SELECT id, name, quantity, unit, calories_per_100g, category, expiration_date, emoji, image_data, created_at
        FROM products
        ORDER BY created_at DESC, id DESC
    """)


def add_product(name, quantity, unit, calories, category, expiration_date, emoji="🧺", image_data=None):
    execute(
        """
        INSERT INTO products
            (name, quantity, unit, calories_per_100g, category, expiration_date, emoji, image_data, created_at)
        VALUES
            (:name, :quantity, :unit, :calories, :category, :expiration_date, :emoji, :image_data, CURRENT_TIMESTAMP)
        """,
        {
            "name": name,
            "quantity": quantity,
            "unit": unit,
            "calories": calories,
            "category": category,
            "expiration_date": str(expiration_date) if expiration_date else None,
            "emoji": emoji,
            "image_data": image_data,
        },
    )


def delete_product(product_id):
    execute("DELETE FROM products WHERE id = :id", {"id": product_id})


def get_shopping_items():
    return query_rows("""
        SELECT id, name, quantity, unit, category, status, created_at
        FROM shopping_items
        ORDER BY created_at DESC, id DESC
    """)


def add_shopping_item(name, quantity, unit, category):
    execute(
        """
        INSERT INTO shopping_items
            (name, quantity, unit, category, status, created_at)
        VALUES
            (:name, :quantity, :unit, :category, 'need', CURRENT_TIMESTAMP)
        """,
        {
            "name": name,
            "quantity": quantity,
            "unit": unit,
            "category": category,
        },
    )


def set_shopping_status(item_id, status):
    execute(
        "UPDATE shopping_items SET status = :status WHERE id = :id",
        {"id": item_id, "status": status},
    )


def get_diary(date_value=None):
    if date_value is None:
        date_value = date.today()

    return query_rows("""
        SELECT id, person, date, meal, dish, calories, protein, fat, carbs, comment, created_at
        FROM nutrition_diary
        WHERE date = :date
        ORDER BY created_at DESC, id DESC
    """, {"date": str(date_value)})


def add_diary(person, date_value, meal, dish, calories, protein, fat, carbs, comment):
    execute(
        """
        INSERT INTO nutrition_diary
            (person, date, meal, dish, calories, protein, fat, carbs, comment, created_at)
        VALUES
            (:person, :date, :meal, :dish, :calories, :protein, :fat, :carbs, :comment, CURRENT_TIMESTAMP)
        """,
        {
            "person": person,
            "date": str(date_value),
            "meal": meal,
            "dish": dish,
            "calories": calories,
            "protein": protein,
            "fat": fat,
            "carbs": carbs,
            "comment": comment,
        },
    )


def image_to_data_url(file):
    if file is None:
        return None

    raw = file.getvalue()
    b64 = base64.b64encode(raw).decode("utf-8")
    return f"data:image/jpeg;base64,{b64}"


# =========================
# Navigation and UI
# =========================

def apply_design():
    st.markdown(
        """
<style>
:root {
    --ink: #10281c;
    --muted: #647067;
    --green: #1f6b43;
    --green-dark: #123321;
    --card: rgba(255,255,255,.94);
    --border: rgba(18,51,33,.10);
    --shadow: 0 18px 42px rgba(15,23,42,.09);
}

html, body, [data-testid="stAppViewContainer"] {
    background:
        radial-gradient(circle at top left, rgba(34,197,94,.08), transparent 30%),
        linear-gradient(180deg, #f8fbf8 0%, #f3f7f4 100%) !important;
}

.block-container {
    max-width: 1320px !important;
    padding-top: 1rem !important;
    padding-bottom: 7rem !important;
}

h1, h2, h3 {
    color: var(--ink) !important;
    line-height: 1.15 !important;
    letter-spacing: -0.035em !important;
    overflow: visible !important;
}

a[href^="#"],
.stDeployButton,
[data-testid="stToolbar"] {
    display: none !important;
}

[data-testid="stSidebar"] {
    background:
        radial-gradient(circle at top left, rgba(34,197,94,.12), transparent 34%),
        linear-gradient(180deg, #f4fff8 0%, #ffffff 100%) !important;
    border-right: 1px solid rgba(18,51,33,.08) !important;
}

div.stButton > button {
    border-radius: 18px !important;
    min-height: 48px !important;
    font-weight: 800 !important;
    border: 1px solid rgba(18,51,33,.12) !important;
    box-shadow: 0 10px 24px rgba(15,23,42,.06) !important;
}

.v2-hero {
    border-radius: 34px;
    padding: 30px;
    background:
        radial-gradient(circle at top right, rgba(255,255,255,.22), transparent 28%),
        linear-gradient(135deg, #123321 0%, #1f6b43 100%);
    color: white;
    box-shadow: 0 24px 58px rgba(15,23,42,.18);
    margin-bottom: 18px;
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

.v2-top-nav {
    position: sticky;
    top: 0;
    z-index: 9999;
    display: grid;
    grid-template-columns: repeat(8, minmax(0, 1fr));
    gap: 8px;
    padding: 10px;
    margin: 0 0 18px 0;
    border-radius: 24px;
    background: rgba(255,255,255,.88);
    border: 1px solid rgba(18,51,33,.10);
    box-shadow: 0 14px 36px rgba(15,23,42,.08);
    backdrop-filter: blur(16px);
}

.v2-top-nav a,
.v2-sidebar-link,
.v2-bottom-nav a,
.v2-action-link {
    text-decoration: none !important;
}

.v2-top-nav a {
    display: flex;
    align-items: center;
    justify-content: center;
    min-height: 44px;
    padding: 9px 10px;
    border-radius: 17px;
    color: #123321 !important;
    font-weight: 900;
    font-size: .92rem;
    border: 1px solid transparent;
}

.v2-top-nav a:hover,
.v2-top-nav a.active {
    background: rgba(34,197,94,.16);
    border-color: rgba(34,197,94,.24);
}

.v2-sidebar-link {
    display: block;
    padding: 10px 12px;
    margin: 5px 0;
    border-radius: 16px;
    color: #123321 !important;
    font-weight: 850;
    border: 1px solid transparent;
}

.v2-sidebar-link:hover,
.v2-sidebar-link.active {
    background: rgba(34,197,94,.16);
    border-color: rgba(34,197,94,.24);
}

.v2-action-grid {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 16px;
    margin: 10px 0 26px 0;
}

.v2-action-link {
    display: flex;
    align-items: center;
    justify-content: center;
    min-height: 54px;
    border-radius: 20px;
    color: #123321 !important;
    font-weight: 900;
    background: rgba(255,255,255,.94);
    border: 1px solid rgba(18,51,33,.12);
    box-shadow: 0 10px 24px rgba(15,23,42,.06);
}

.v2-bottom-nav {
    display: none;
}

.v2-photo-native {
    width: 100%;
    min-height: 150px;
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

@media (max-width: 900px) {
    .block-container {
        padding: .95rem 1rem 7rem 1rem !important;
    }

    .v2-top-nav {
        grid-template-columns: repeat(4, minmax(0, 1fr));
        position: relative;
    }

    .v2-top-nav a {
        font-size: .8rem;
        min-height: 42px;
        white-space: nowrap;
    }

    .v2-action-grid {
        grid-template-columns: 1fr 1fr;
        gap: 10px;
    }

    .v2-hero {
        border-radius: 26px;
        padding: 22px;
    }

    .v2-hero h1 {
        font-size: 2rem !important;
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
        background: rgba(255,255,255,.96);
        border: 1px solid rgba(18,51,33,.12);
        box-shadow: 0 18px 48px rgba(15,23,42,.22);
        backdrop-filter: blur(16px);
        gap: 6px;
    }

    .v2-bottom-nav a {
        color: #123321 !important;
        border-radius: 18px;
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

    .v2-bottom-nav a.active {
        background: rgba(34,197,94,.18);
    }

    .v2-bottom-nav .emoji {
        font-size: 21px;
        line-height: 1;
    }
}
</style>
""",
        unsafe_allow_html=True,
    )


def get_query_tab():
    try:
        tab = st.query_params.get("tab", None)
    except Exception:
        tab = None

    if isinstance(tab, list):
        tab = tab[0] if tab else None

    return tab


def init_state():
    st.session_state["authenticated"] = True

    if "user" not in st.session_state:
        st.session_state["user"] = "Мишка"

    allowed = {
        "today",
        "fridge",
        "scan",
        "recipes",
        "shopping",
        "diary",
        "analytics",
        "settings",
    }

    tab = get_query_tab()

    if tab in allowed:
        st.session_state["tab"] = tab

    if "tab" not in st.session_state:
        st.session_state["tab"] = "today"


def top_nav():
    current = st.session_state.get("tab", "today")

    items = [
        ("today", "🏠 Сегодня"),
        ("fridge", "🧊 Холодильник"),
        ("scan", "📸 Сканер"),
        ("recipes", "🍳 Рецепты"),
        ("shopping", "🛒 Покупки"),
        ("diary", "📔 Дневник"),
        ("analytics", "📊 Аналитика"),
        ("settings", "⚙️ Настройки"),
    ]

    links = []

    for key, label in items:
        active = "active" if current == key else ""
        links.append(f'<a class="{active}" href="?tab={key}" target="_self">{label}</a>')

    st.markdown(
        f"""
<div class="v2-top-nav">
    {''.join(links)}
</div>
""",
        unsafe_allow_html=True,
    )


def bottom_nav():
    current = st.session_state.get("tab", "today")

    items = [
        ("today", "🏠", "Сегодня"),
        ("fridge", "🧊", "Холод."),
        ("scan", "📸", "Сканер"),
        ("recipes", "🍳", "Рецепты"),
        ("shopping", "🛒", "Покупки"),
    ]

    links = []

    for key, emoji, label in items:
        active = "active" if current == key else ""
        links.append(
            f'<a class="{active}" href="?tab={key}" target="_self"><span class="emoji">{emoji}</span><span>{label}</span></a>'
        )

    st.markdown(
        f"""
<div class="v2-bottom-nav">
    {''.join(links)}
</div>
""",
        unsafe_allow_html=True,
    )


def sidebar():
    with st.sidebar:
        st.markdown("## 🥦 Умный холодильник")
        st.caption(f"{APP_VERSION} · {DEVELOPER}")
        st.markdown("---")

        current = st.session_state.get("tab", "today")

        items = [
            ("today", "🏠 Сегодня"),
            ("fridge", "🧊 Холодильник"),
            ("scan", "📸 Сканер"),
            ("recipes", "🍳 Рецепты"),
            ("shopping", "🛒 Покупки"),
            ("diary", "📔 Дневник"),
            ("analytics", "📊 Аналитика"),
            ("settings", "⚙️ Настройки"),
        ]

        html = ""

        for key, label in items:
            active = "active" if current == key else ""
            html += f'<a class="v2-sidebar-link {active}" href="?tab={key}" target="_self">{label}</a>'

        st.markdown(html, unsafe_allow_html=True)

        st.markdown("---")
        user = st.session_state.get("user", "Мишка")
        st.success(f"{USERS[user]['emoji']} {user}")


def hero(title, subtitle, icon="🥦"):
    st.markdown(
        f"""
<div class="v2-hero">
    <h1>{icon} {title}</h1>
    <p>{subtitle}</p>
</div>
""",
        unsafe_allow_html=True,
    )


def action_links():
    st.markdown(
        """
<div class="v2-action-grid">
    <a class="v2-action-link" href="?tab=scan" target="_self">📸 Сканировать</a>
    <a class="v2-action-link" href="?tab=fridge" target="_self">🧊 Холодильник</a>
    <a class="v2-action-link" href="?tab=recipes" target="_self">🍳 Рецепты</a>
    <a class="v2-action-link" href="?tab=shopping" target="_self">🛒 Покупки</a>
</div>
""",
        unsafe_allow_html=True,
    )


def native_chip(text_value):
    st.caption(text_value)


# =========================
# Pages
# =========================

def expiry_status(expiration_date):
    if not expiration_date:
        return "без срока"

    try:
        exp = date.fromisoformat(str(expiration_date)[:10])
        days = (exp - date.today()).days

        if days < 0:
            return "просрочено"
        if days <= 1:
            return "срочно"
        if days <= 3:
            return "скоро"
        return f"{days} дн."
    except Exception:
        return "без срока"


def page_today():
    products = get_products()
    diary = get_diary(date.today())

    hero(
        "Сегодня у Мединки",
        "Главное на одном экране: питание, холодильник, покупки, рецепты и фото-сканер.",
        "🧊",
    )

    attention = 0
    calories_stock = 0

    for p in products:
        status = expiry_status(p.get("expiration_date"))
        if status in ["просрочено", "срочно", "скоро"]:
            attention += 1

        try:
            q = float(p.get("quantity") or 0)
            cal = float(p.get("calories_per_100g") or 0)
            unit = str(p.get("unit") or "")

            if unit in ["г", "мл"]:
                calories_stock += q / 100 * cal
            elif unit in ["кг", "л"]:
                calories_stock += q * 10 * cal
            else:
                calories_stock += cal
        except Exception:
            pass

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Продуктов дома", len(products))
    c2.metric("Требуют внимания", attention)
    c3.metric("Идей блюд", len(DEFAULT_RECIPES))
    c4.metric("Ккал в запасах", int(calories_stock))

    st.markdown("## ⚡ Быстрые действия")
    action_links()

    st.markdown("## 🍽️ Питание сегодня")

    totals = {}
    for user in USERS:
        totals[user] = sum(float(row.get("calories") or 0) for row in diary if row.get("person") == user)

    cols = st.columns(2)

    for col, (user, info) in zip(cols, USERS.items()):
        eaten = int(totals[user])
        left = max(0, info["goal"] - eaten)

        with col:
            with st.container(border=True):
                st.subheader(f"{info['emoji']} {user}")
                st.write(info["description"])
                st.metric("Цель", f"{info['goal']} ккал")
                st.metric("Съедено", f"{eaten} ккал")
                st.metric("Осталось", f"{left} ккал")

    with st.container(border=True):
        st.subheader("💡 Рекомендация дня")
        st.write("Сначала используй продукты, у которых скоро закончится срок годности. Это поможет меньше выбрасывать и проще планировать меню.")


def page_fridge():
    products = get_products()

    hero(
        "Холодильник",
        "Продукты как карточки: фото, количество, сроки годности и быстрые действия.",
        "🧊",
    )

    tab_catalog, tab_manual, tab_cards, tab_table = st.tabs(["Каталог", "Вручную", "Карточки", "Таблица"])

    with tab_catalog:
        st.subheader("🧺 Большой каталог продуктов")
        st.caption("Выбери продукт из каталога, укажи количество и срок годности — он попадёт в холодильник.")

        categories = ["Все категории"] + PRODUCT_CATEGORIES

        c1, c2 = st.columns([1, 2])

        with c1:
            selected_category = st.selectbox("Категория", categories, key="catalog_category_v2")

        with c2:
            search = st.text_input("Поиск", placeholder="Например: молоко, курица, рис", key="catalog_search_v2")

        filtered = PRODUCT_CATALOG

        if selected_category != "Все категории":
            filtered = [p for p in filtered if p["category"] == selected_category]

        if search.strip():
            q = search.strip().lower()
            filtered = [
                p for p in filtered
                if q in p["name"].lower()
                or q in p["category"].lower()
                or q in p["description"].lower()
            ]

        if not filtered:
            st.info("Ничего не найдено.")
        else:
            names = [
                f'{p["emoji"]} {p["name"]} · {p["category"]} · {int(p["calories_per_100g"])} ккал'
                for p in filtered
            ]

            selected_label = st.selectbox("Продукт", names, key="catalog_product_v2")
            item = filtered[names.index(selected_label)]

            with st.container(border=True):
                st.subheader(f'{item["emoji"]} {item["name"]}')
                st.write(item["description"])
                st.write(f'Категория: **{item["category"]}**')
                st.write(f'Калории: **{item["calories_per_100g"]} ккал на 100 г**')
                st.write(f'БЖУ: **Б {item["protein"]} · Ж {item["fat"]} · У {item["carbs"]}**')
                st.write(f'Хранение: примерно **{item["storage_days"]} дн.**')

            with st.form("add_from_catalog_v2"):
                c1, c2, c3 = st.columns(3)

                with c1:
                    quantity = st.number_input("Количество", min_value=0.0, value=1.0, step=0.1)

                with c2:
                    units = ["шт", "г", "кг", "мл", "л", "упак."]
                    default_index = units.index(item["unit"]) if item["unit"] in units else 0
                    unit = st.selectbox("Единица", units, index=default_index)

                with c3:
                    expiration_date = st.date_input(
                        "Срок годности",
                        value=date.today() + timedelta(days=int(item["storage_days"])),
                    )

                submitted = st.form_submit_button("🧊 Добавить из каталога", use_container_width=True)

            if submitted:
                add_product(
                    name=item["name"],
                    quantity=quantity,
                    unit=unit,
                    calories=item["calories_per_100g"],
                    category=item["category"],
                    expiration_date=expiration_date,
                    emoji=item["emoji"],
                    image_data=None,
                )
                st.success(f'Добавлено: {item["name"]}')
                st.rerun()

        with st.expander("Показать весь каталог таблицей"):
            st.dataframe(pd.DataFrame(PRODUCT_CATALOG), use_container_width=True, hide_index=True)

    with tab_manual:
        st.subheader("✍️ Добавить продукт вручную")

        with st.form("add_product_v2_manual"):
            c1, c2 = st.columns(2)

            with c1:
                name = st.text_input("Название", placeholder="Например: молоко")
                category = st.text_input("Категория", value="Другое")
                emoji = st.text_input("Emoji", value="🧺")
                expiration_date = st.date_input("Срок годности", value=date.today() + timedelta(days=7))

            with c2:
                quantity = st.number_input("Количество", min_value=0.0, value=1.0, step=0.1)
                unit = st.selectbox("Единица", ["шт", "г", "кг", "мл", "л", "упак."], key="manual_unit_v2")
                calories = st.number_input("Ккал на 100 г", min_value=0.0, value=0.0, step=1.0)
                photo = st.file_uploader("Фото продукта", type=["jpg", "jpeg", "png", "webp"])

            submitted = st.form_submit_button("➕ Добавить в холодильник", use_container_width=True)

        if submitted:
            if not name.strip():
                st.warning("Укажи название продукта.")
            else:
                add_product(
                    name=name.strip(),
                    quantity=quantity,
                    unit=unit,
                    calories=calories,
                    category=category,
                    expiration_date=expiration_date,
                    emoji=emoji or "🧺",
                    image_data=image_to_data_url(photo),
                )
                st.success("Продукт добавлен.")
                st.rerun()

    with tab_cards:
        if not products:
            st.info("Пока в холодильнике нет продуктов.")
        else:
            cols = st.columns(3)

            for i, p in enumerate(products):
                with cols[i % 3]:
                    with st.container(border=True):
                        image = p.get("image_data")
                        emoji = p.get("emoji") or "🧺"

                        if image:
                            st.image(image, use_container_width=True)
                        else:
                            st.markdown(f"<div class='v2-photo-native'>{emoji}</div>", unsafe_allow_html=True)

                        st.subheader(str(p.get("name")))
                        st.write(f'Количество: **{p.get("quantity")} {p.get("unit")}**')
                        st.write(f'Калории: **{p.get("calories_per_100g")} ккал**')
                        st.write(f'Категория: **{p.get("category") or "Другое"}**')
                        st.write(f'Срок: **{expiry_status(p.get("expiration_date"))}**')

                        if st.button("Удалить", key=f"delete_product_{p.get('id')}", use_container_width=True):
                            delete_product(p.get("id"))
                            st.rerun()

    with tab_table:
        if products:
            st.dataframe(pd.DataFrame(products), use_container_width=True, hide_index=True)
        else:
            st.info("Нет продуктов.")


def page_scan():
    hero(
        "Сканер продуктов",
        "Сфотографируй продукт с телефона, подтверди данные и добавь в холодильник.",
        "📸",
    )

    with st.container(border=True):
        st.subheader("AI-распознавание будет следующим шагом")
        st.write("Сейчас фото можно добавить вручную к продукту. Далее подключим распознавание названия, срока годности, категории и калорий.")

    source = st.radio("Источник фото", ["Камера", "Загрузить файл"], horizontal=True)

    file = None
    if source == "Камера":
        file = st.camera_input("Сделать фото продукта")
    else:
        file = st.file_uploader("Загрузить фото", type=["jpg", "jpeg", "png", "webp"])

    image_data = image_to_data_url(file) if file else None

    if image_data:
        st.image(image_data, use_container_width=True)

    with st.form("scan_confirm_form"):
        c1, c2 = st.columns(2)

        with c1:
            name = st.text_input("Название продукта", placeholder="Например: йогурт")
            category = st.text_input("Категория", value="Другое")
            emoji = st.text_input("Emoji", value="🧺")
            expiration_date = st.date_input("Срок годности", value=date.today() + timedelta(days=7))

        with c2:
            quantity = st.number_input("Количество", min_value=0.0, value=1.0, step=0.1)
            unit = st.selectbox("Единица", ["шт", "г", "кг", "мл", "л", "упак."], key="scan_unit")
            calories = st.number_input("Ккал на 100 г", min_value=0.0, value=0.0, step=1.0)

        submitted = st.form_submit_button("🧊 Добавить в холодильник", use_container_width=True)

    if submitted:
        if not name.strip():
            st.warning("Укажи название.")
        else:
            add_product(
                name=name.strip(),
                quantity=quantity,
                unit=unit,
                calories=calories,
                category=category,
                expiration_date=expiration_date,
                emoji=emoji or "🧺",
                image_data=image_data,
            )
            st.success("Продукт добавлен.")
            st.rerun()


def page_recipes():
    hero(
        "Рецепты и меню",
        "Блюда с фото, калориями, временем и понятной кнопкой “готовить”.",
        "🍳",
    )

    search = st.text_input("Поиск рецепта", placeholder="Например: курица, омлет, суп")

    recipes = DEFAULT_RECIPES

    if search.strip():
        q = search.strip().lower()
        recipes = [
            r for r in recipes
            if q in r["name"].lower()
            or q in r["category"].lower()
            or q in r["description"].lower()
            or q in r["ingredients"].lower()
        ]

    cols = st.columns(3)

    for i, recipe in enumerate(recipes):
        with cols[i % 3]:
            with st.container(border=True):
                st.markdown(f"<div class='v2-photo-native'>{recipe['emoji']}</div>", unsafe_allow_html=True)
                st.subheader(recipe["name"])
                st.write(recipe["description"])
                st.write(f'Категория: **{recipe["category"]}**')
                st.write(f'Время: **{recipe["time"]}**')
                st.write(f'Калории: **{recipe["calories"]} ккал**')
                st.caption(f'Ингредиенты: {recipe["ingredients"]}')

                if st.button("🍽️ Добавить в дневник", key=f"recipe_diary_{recipe['name']}", use_container_width=True):
                    add_diary(
                        person=st.session_state.get("user", "Мишка"),
                        date_value=date.today(),
                        meal="Обед",
                        dish=recipe["name"],
                        calories=recipe["calories"],
                        protein=0,
                        fat=0,
                        carbs=0,
                        comment="Добавлено из рецептов v2",
                    )
                    st.success("Добавлено в дневник.")


def page_shopping():
    hero(
        "Покупки",
        "Что купить, что куплено и что можно перенести в холодильник.",
        "🛒",
    )

    tab_add, tab_need, tab_done = st.tabs(["Добавить", "Нужно купить", "Куплено"])

    with tab_add:
        with st.form("add_shopping_v2"):
            c1, c2, c3, c4 = st.columns(4)

            with c1:
                name = st.text_input("Что купить", placeholder="молоко")
            with c2:
                quantity = st.number_input("Количество", min_value=0.0, value=1.0, step=0.1)
            with c3:
                unit = st.selectbox("Ед.", ["шт", "г", "кг", "мл", "л", "упак."])
            with c4:
                category = st.text_input("Категория", value="Другое")

            submitted = st.form_submit_button("🛒 Добавить", use_container_width=True)

        if submitted:
            if not name.strip():
                st.warning("Укажи название.")
            else:
                add_shopping_item(name.strip(), quantity, unit, category)
                st.success("Добавлено в список покупок.")
                st.rerun()

    items = get_shopping_items()

    with tab_need:
        need = [x for x in items if x.get("status") not in ["bought", "moved"]]

        if not need:
            st.info("Список покупок пуст.")
        else:
            for item in need:
                c1, c2 = st.columns([4, 1])

                with c1:
                    with st.container(border=True):
                        st.subheader(str(item.get("name")))
                        st.write(f'{item.get("quantity")} {item.get("unit")}')
                        st.caption(item.get("category"))

                with c2:
                    if st.button("✅ Куплено", key=f"bought_{item.get('id')}", use_container_width=True):
                        set_shopping_status(item.get("id"), "bought")
                        st.rerun()

    with tab_done:
        done = [x for x in items if x.get("status") == "bought"]

        if not done:
            st.info("Пока нет купленных позиций.")
        else:
            for item in done:
                c1, c2 = st.columns([4, 1])

                with c1:
                    with st.container(border=True):
                        st.subheader(str(item.get("name")))
                        st.write(f'{item.get("quantity")} {item.get("unit")}')
                        st.caption(item.get("category"))

                with c2:
                    if st.button("🧊 В холодильник", key=f"to_fridge_{item.get('id')}", use_container_width=True):
                        add_product(
                            name=item.get("name"),
                            quantity=float(item.get("quantity") or 1),
                            unit=item.get("unit") or "шт",
                            calories=0,
                            category=item.get("category") or "Другое",
                            expiration_date=date.today() + timedelta(days=7),
                            emoji="🧺",
                        )
                        set_shopping_status(item.get("id"), "moved")
                        st.rerun()


def page_diary():
    hero(
        "Дневник питания",
        "Записывай еду Мишки и Мединки, следи за калориями и историей питания.",
        "📔",
    )

    with st.form("diary_add_v2"):
        c1, c2, c3 = st.columns(3)

        with c1:
            person = st.selectbox("Кто", list(USERS.keys()), index=0)
            date_value = st.date_input("Дата", value=date.today())
            meal = st.selectbox("Приём пищи", ["Завтрак", "Обед", "Ужин", "Перекус"])

        with c2:
            dish = st.text_input("Блюдо", placeholder="Омлет")
            calories = st.number_input("Калории", min_value=0.0, value=0.0, step=10.0)
            protein = st.number_input("Белки", min_value=0.0, value=0.0, step=1.0)

        with c3:
            fat = st.number_input("Жиры", min_value=0.0, value=0.0, step=1.0)
            carbs = st.number_input("Углеводы", min_value=0.0, value=0.0, step=1.0)
            comment = st.text_area("Комментарий", height=80)

        submitted = st.form_submit_button("➕ Добавить запись", use_container_width=True)

    if submitted:
        if not dish.strip():
            st.warning("Укажи блюдо.")
        else:
            add_diary(person, date_value, meal, dish, calories, protein, fat, carbs, comment)
            st.success("Запись добавлена.")
            st.rerun()

    rows = get_diary(date.today())

    st.markdown("## Сегодня")

    if rows:
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    else:
        st.info("Сегодня записей пока нет.")


def page_analytics():
    hero(
        "Аналитика",
        "Калории, холодильник, покупки и питание семьи в одном месте.",
        "📊",
    )

    products = get_products()
    diary = get_diary(date.today())
    shopping = get_shopping_items()

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric("Продуктов", len(products))
    with c2:
        st.metric("Записей сегодня", len(diary))
    with c3:
        st.metric("Покупок", len([x for x in shopping if x.get("status") not in ["bought", "moved"]]))
    with c4:
        st.metric("Калорий сегодня", int(sum(float(x.get("calories") or 0) for x in diary)))

    rows = []

    for user, info in USERS.items():
        eaten = sum(float(row.get("calories") or 0) for row in diary if row.get("person") == user)
        rows.append({
            "Кто": user,
            "Цель": info["goal"],
            "Съедено": eaten,
            "Осталось": max(0, info["goal"] - eaten),
        })

    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)


def page_settings():
    hero(
        "Настройки",
        "Семейные профили, версия приложения и служебные действия.",
        "⚙️",
    )

    with st.container(border=True):
        st.subheader(APP_NAME)
        st.write(f"Версия: **{APP_VERSION}**")
        st.write(f"Разработка: **{DEVELOPER}**")
        st.write("Авторизация временно отключена до финальной сборки.")

    st.markdown("## Профили")

    cols = st.columns(2)

    for col, (user, info) in zip(cols, USERS.items()):
        with col:
            with st.container(border=True):
                st.subheader(f"{info['emoji']} {user}")
                st.metric("Цель", f"{info['goal']} ккал/день")
                st.write(info["description"])

    if st.button("Добавить демо-продукты", use_container_width=True):
        for name, quantity, unit, calories, category, exp, emoji in DEFAULT_PRODUCTS:
            add_product(name, quantity, unit, calories, category, exp, emoji)
        st.success("Демо-продукты добавлены.")
        st.rerun()


def render_app():
    apply_design()
    init_state()
    bottom_nav()
    sidebar()
    top_nav()

    tab = st.session_state.get("tab", "today")

    if tab == "fridge":
        page_fridge()
    elif tab == "scan":
        page_scan()
    elif tab == "recipes":
        page_recipes()
    elif tab == "shopping":
        page_shopping()
    elif tab == "diary":
        page_diary()
    elif tab == "analytics":
        page_analytics()
    elif tab == "settings":
        page_settings()
    else:
        page_today()


def main():
    ensure_schema()
    seed_if_empty()
    render_app()


if __name__ == "__main__":
    main()
