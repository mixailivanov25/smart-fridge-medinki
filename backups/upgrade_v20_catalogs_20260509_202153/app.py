import os
import io
import base64
from datetime import date, datetime, timedelta

import pandas as pd
import streamlit as st
from sqlalchemy import create_engine, text


APP_NAME = "Умный холодильник Мединки"
APP_VERSION = "v2.0"
DEVELOPER = "Иванов Михаил"

USERS = {
    "Мишка": {
        "emoji": "🐻",
        "pin_secret": "AUTH_PIN_MISHKA",
        "default_pin": "1111",
        "goal": 2300,
        "accent": "#1d4ed8",
        "description": "Домашняя еда, белок, сытное меню.",
    },
    "Мединка": {
        "emoji": "🌸",
        "pin_secret": "AUTH_PIN_MEDINKA",
        "default_pin": "2222",
        "goal": 1800,
        "accent": "#be185d",
        "description": "Лёгкие блюда, овощи, комфортное питание.",
    },
}

DEFAULT_PRODUCTS = [
    ("апельсин", 1, "шт", 47, "Фрукты", date.today() + timedelta(days=14), "🍊"),
    ("гречка", 700, "г", 313, "Крупы и паста", date.today() + timedelta(days=600), "🌾"),
    ("замороженные овощи", 251, "г", 65, "Заморозка", date.today() + timedelta(days=180), "🥦"),
    ("картофель", 0.4, "кг", 77, "Овощи", date.today() + timedelta(days=20), "🥔"),
    ("лук", 3, "шт", 40, "Овощи", date.today() + timedelta(days=25), "🧅"),
    ("морковь", 4, "шт", 41, "Овощи", date.today() + timedelta(days=18), "🥕"),
    ("овсянка", 260, "г", 370, "Крупы и паста", date.today() + timedelta(days=300), "🥣"),
    ("рис", 170, "г", 344, "Крупы и паста", date.today() + timedelta(days=500), "🍚"),
    ("тунец", 2, "шт", 130, "Консервы", date.today() + timedelta(days=365), "🐟"),
    ("фарш", 500, "г", 250, "Мясо и птица", date.today() + timedelta(days=3), "🥩"),
]

DEFAULT_RECIPES = [
    {
        "name": "Омлет",
        "emoji": "🍳",
        "category": "Завтрак",
        "time": "12 минут",
        "calories": 320,
        "description": "Нежный омлет на молоке. Быстрый завтрак для всей семьи.",
        "ingredients": "яйца, молоко, соль",
    },
    {
        "name": "Курица с рисом",
        "emoji": "🍗",
        "category": "Обед",
        "time": "35 минут",
        "calories": 560,
        "description": "Сытное домашнее блюдо с простыми ингредиентами.",
        "ingredients": "курица, рис, морковь, лук",
    },
    {
        "name": "Овсянка на молоке",
        "emoji": "🥣",
        "category": "Завтрак",
        "time": "10 минут",
        "calories": 350,
        "description": "Тёплый завтрак с медленными углеводами.",
        "ingredients": "овсянка, молоко, фрукты",
    },
    {
        "name": "Жареный картофель",
        "emoji": "🥔",
        "category": "Ужин",
        "time": "30 минут",
        "calories": 420,
        "description": "Простое домашнее блюдо из картофеля и лука.",
        "ingredients": "картофель, лук, масло",
    },
    {
        "name": "Салат с тунцом",
        "emoji": "🥗",
        "category": "Ужин",
        "time": "15 минут",
        "calories": 290,
        "description": "Лёгкий белковый салат из консервированного тунца.",
        "ingredients": "тунец, овощи, зелень",
    },
]


# =========================
# Basic config
# =========================

st.set_page_config(
    page_title=APP_NAME,
    page_icon="🥦",
    layout="wide",
    initial_sidebar_state="expanded",
)




# AUTO_AUTH_DISABLED_V2_START
# Авторизация временно отключена на период разработки v2.
try:
    st.session_state["authenticated"] = True
    if "user" not in st.session_state:
        st.session_state["user"] = "Мишка"
except Exception:
    pass
# AUTO_AUTH_DISABLED_V2_END

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
    try:
        return get_engine().dialect.name.startswith("postgres")
    except Exception:
        return False


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

            cols = conn.execute(text("PRAGMA table_info(products)")).fetchall()
            col_names = {row[1] for row in cols}
            if "emoji" not in col_names:
                conn.execute(text("ALTER TABLE products ADD COLUMN emoji TEXT DEFAULT '🧺'"))
            if "image_data" not in col_names:
                conn.execute(text("ALTER TABLE products ADD COLUMN image_data TEXT"))

            cols = conn.execute(text("PRAGMA table_info(shopping_items)")).fetchall()
            col_names = {row[1] for row in cols}
            if "status" not in col_names:
                conn.execute(text("ALTER TABLE shopping_items ADD COLUMN status TEXT DEFAULT 'need'"))


def seed_if_empty():
    engine = get_engine()

    with engine.begin() as conn:
        count = conn.execute(text("SELECT COUNT(*) FROM products")).scalar() or 0

        if count == 0:
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


def query_rows(sql, params=None):
    ensure_schema()
    engine = get_engine()

    with engine.begin() as conn:
        rows = conn.execute(text(sql), params or {}).mappings().all()

    return [dict(row) for row in rows]


def execute(sql, params=None):
    ensure_schema()
    engine = get_engine()

    with engine.begin() as conn:
        conn.execute(text(sql), params or {})


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
        {"status": status, "id": item_id},
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
# UI
# =========================

def apply_design():
    st.markdown(
        """
<style>
:root {
    --bg: #f6f8f5;
    --ink: #10281c;
    --muted: #647067;
    --green: #1f6b43;
    --green-dark: #123321;
    --mint: #eafaf0;
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
    padding-top: 1.1rem !important;
    padding-bottom: 6.7rem !important;
}

h1, h2, h3 {
    color: var(--ink) !important;
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

[data-testid="stSidebar"] input[type="radio"],
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
    background: var(--card);
    border: 1px solid var(--border);
    box-shadow: var(--shadow);
    margin-bottom: 16px;
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
    color: var(--ink);
    letter-spacing: -.04em;
}

.v2-label {
    color: var(--muted);
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

.v2-chip-green { background: #dcfce7; color: #166534; }
.v2-chip-blue { background: #dbeafe; color: #1d4ed8; }
.v2-chip-purple { background: #ede9fe; color: #6d28d9; }
.v2-chip-orange { background: #ffedd5; color: #c2410c; }
.v2-chip-red { background: #fee2e2; color: #b91c1c; }

.v2-photo {
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
    overflow: hidden;
}

.v2-photo img {
    width: 100%;
    height: 170px;
    object-fit: cover;
    border-radius: 22px;
}

.v2-bottom-nav {
    display: none;
}

.table-scroll {
    overflow-x: auto;
}

@media (max-width: 900px) {
    .block-container {
        padding: .95rem 1rem 7rem 1rem !important;
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
        background: rgba(255,255,255,.95);
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


def init_tab():
    tab = get_query_tab()

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

    if tab in allowed:
        st.session_state["tab"] = tab

    if "tab" not in st.session_state:
        st.session_state["tab"] = "today"


def auth_screen():
    apply_design()

    st.markdown(
        """
<div class="v2-hero">
    <h1>🥦 Умный холодильник Мединки</h1>
    <p>Семейный вход в холодильник, меню, покупки, рецепты и дневник питания.</p>
</div>
""",
        unsafe_allow_html=True,
    )

    st.markdown("## Кто входит?")

    if "login_user" not in st.session_state:
        st.session_state["login_user"] = "Мишка"

    c1, c2 = st.columns(2)

    for col, name in [(c1, "Мишка"), (c2, "Мединка")]:
        with col:
            info = USERS[name]
            active = st.session_state["login_user"] == name
            st.markdown(
                f"""
<div class="v2-card {'v2-card-soft' if active else ''}">
    <h2>{info['emoji']} {name}</h2>
    <p>{info['description']}</p>
    <span class="v2-chip v2-chip-green">{info['goal']} ккал/день</span>
</div>
""",
                unsafe_allow_html=True,
            )
            if st.button(f"Выбрать {name}", key=f"login_choose_{name}", use_container_width=True):
                st.session_state["login_user"] = name
                st.rerun()

    selected = st.session_state["login_user"]

    with st.form("login_form_v2"):
        pin = st.text_input("PIN-код", type="password", placeholder="Введите PIN")
        submitted = st.form_submit_button("🔓 Войти", use_container_width=True)

    if submitted:
        user_info = USERS[selected]
        expected = get_secret(user_info["pin_secret"], user_info["default_pin"])

        if str(pin) == str(expected):
            st.session_state["authenticated"] = True
            st.session_state["user"] = selected
            st.rerun()
        else:
            st.error("Неверный PIN-код.")


def require_auth():
    if not st.session_state.get("authenticated"):
        auth_screen()
        st.stop()


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


def metric_grid(products):
    total_products = len(products)

    attention = 0
    today_value = date.today()

    for p in products:
        exp = p.get("expiration_date")
        if exp:
            try:
                exp_date = date.fromisoformat(str(exp)[:10])
                if (exp_date - today_value).days <= 3:
                    attention += 1
            except Exception:
                pass

    calories_stock = 0
    for p in products:
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

    st.markdown(
        f"""
<div class="v2-grid-4">
    <div class="v2-card"><div class="v2-metric">{total_products}</div><div class="v2-label">продуктов дома</div></div>
    <div class="v2-card"><div class="v2-metric">{attention}</div><div class="v2-label">требуют внимания</div></div>
    <div class="v2-card"><div class="v2-metric">{len(DEFAULT_RECIPES)}</div><div class="v2-label">идей блюд</div></div>
    <div class="v2-card"><div class="v2-metric">{int(calories_stock)}</div><div class="v2-label">ккал в запасах</div></div>
</div>
""",
        unsafe_allow_html=True,
    )


def page_today():
    products = get_products()
    diary = get_diary(date.today())

    hero(
        "Сегодня у Мединки",
        "Главное на одном экране: питание, холодильник, покупки, рецепты и фото-сканер.",
        "🧊",
    )

    metric_grid(products)

    st.markdown("## ⚡ Быстрые действия")

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        if st.button("📸 Сканировать", use_container_width=True):
            set_tab("scan")
    with c2:
        if st.button("🧊 Холодильник", use_container_width=True):
            set_tab("fridge")
    with c3:
        if st.button("🍳 Рецепты", use_container_width=True):
            set_tab("recipes")
    with c4:
        if st.button("🛒 Покупки", use_container_width=True):
            set_tab("shopping")

    st.markdown("## 🍽️ Питание сегодня")

    totals = {}
    for user in USERS:
        totals[user] = sum(float(row.get("calories") or 0) for row in diary if row.get("person") == user)

    cards = []

    for user, info in USERS.items():
        eaten = int(totals[user])
        left = max(0, info["goal"] - eaten)
        cards.append(
            f"""
<div class="v2-card v2-card-soft">
    <h2>{info['emoji']} {user}</h2>
    <span class="v2-chip v2-chip-green">цель: {info['goal']} ккал</span>
    <span class="v2-chip v2-chip-blue">съедено: {eaten}</span>
    <span class="v2-chip v2-chip-purple">осталось: {left}</span>
    <p class="v2-label">{info['description']}</p>
</div>
"""
        )

    st.markdown(f'<div class="v2-grid-2">{"".join(cards)}</div>', unsafe_allow_html=True)

    st.markdown(
        """
<div class="v2-card v2-card-warm">
    <h2>💡 Рекомендация дня</h2>
    <p>Сначала используй продукты, у которых скоро закончится срок годности. Это поможет меньше выбрасывать и проще планировать меню.</p>
    <span class="v2-chip v2-chip-orange">умный совет</span>
    <span class="v2-chip v2-chip-green">экономия продуктов</span>
</div>
""",
        unsafe_allow_html=True,
    )


def expiry_status(expiration_date):
    if not expiration_date:
        return "без срока", "v2-chip-blue"

    try:
        exp = date.fromisoformat(str(expiration_date)[:10])
        days = (exp - date.today()).days

        if days < 0:
            return "просрочено", "v2-chip-red"
        if days <= 1:
            return "срочно", "v2-chip-red"
        if days <= 3:
            return "скоро", "v2-chip-orange"
        return f"{days} дн.", "v2-chip-green"
    except Exception:
        return "без срока", "v2-chip-blue"


def page_fridge():
    products = get_products()

    hero(
        "Холодильник",
        "Продукты как карточки: фото, количество, сроки годности и быстрые действия.",
        "🧊",
    )

    tab_cards, tab_add, tab_table = st.tabs(["Карточки", "Добавить", "Таблица"])

    with tab_cards:
        if not products:
            st.info("Пока в холодильнике нет продуктов.")
        else:
            cols = st.columns(3)

            for i, p in enumerate(products):
                status, cls = expiry_status(p.get("expiration_date"))
                emoji = p.get("emoji") or "🧺"
                image = p.get("image_data")

                with cols[i % 3]:
                    if image:
                        photo_html = f'<div class="v2-photo"><img src="{image}"></div>'
                    else:
                        photo_html = f'<div class="v2-photo">{emoji}</div>'

                    st.markdown(
                        f"""
<div class="v2-card">
    {photo_html}
    <h2>{p.get("name")}</h2>
    <span class="v2-chip v2-chip-green">{p.get("quantity")} {p.get("unit")}</span>
    <span class="v2-chip v2-chip-blue">{p.get("calories_per_100g")} ккал</span>
    <span class="v2-chip {cls}">{status}</span>
    <p class="v2-label">{p.get("category") or "Другое"}</p>
</div>
""",
                        unsafe_allow_html=True,
                    )

                    if st.button("Удалить", key=f"delete_product_{p.get('id')}", use_container_width=True):
                        delete_product(p.get("id"))
                        st.rerun()

    with tab_add:
        with st.form("add_product_v2"):
            c1, c2 = st.columns(2)

            with c1:
                name = st.text_input("Название", placeholder="Например: молоко")
                category = st.text_input("Категория", value="Другое")
                emoji = st.text_input("Emoji", value="🧺")
                expiration_date = st.date_input("Срок годности", value=date.today() + timedelta(days=7))

            with c2:
                quantity = st.number_input("Количество", min_value=0.0, value=1.0, step=0.1)
                unit = st.selectbox("Единица", ["шт", "г", "кг", "мл", "л", "упак."])
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

    st.markdown(
        """
<div class="v2-card v2-card-warm">
    <h2>AI-распознавание будет следующим шагом</h2>
    <p>Сейчас фото можно добавить вручную к продукту. Далее подключим распознавание названия, срока годности, категории и калорий.</p>
    <span class="v2-chip v2-chip-purple">камера</span>
    <span class="v2-chip v2-chip-blue">AI Vision</span>
    <span class="v2-chip v2-chip-green">подтверждение</span>
</div>
""",
        unsafe_allow_html=True,
    )

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

    cols = st.columns(3)

    for i, recipe in enumerate(DEFAULT_RECIPES):
        with cols[i % 3]:
            st.markdown(
                f"""
<div class="v2-card">
    <div class="v2-photo">{recipe['emoji']}</div>
    <h2>{recipe['name']}</h2>
    <p>{recipe['description']}</p>
    <span class="v2-chip v2-chip-purple">{recipe['category']}</span>
    <span class="v2-chip v2-chip-blue">{recipe['time']}</span>
    <span class="v2-chip v2-chip-green">{recipe['calories']} ккал</span>
    <p class="v2-label">Ингредиенты: {recipe['ingredients']}</p>
</div>
""",
                unsafe_allow_html=True,
            )

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
        need = [x for x in items if x.get("status") != "bought"]

        if not need:
            st.info("Список покупок пуст.")
        else:
            for item in need:
                c1, c2 = st.columns([4, 1])

                with c1:
                    st.markdown(
                        f"""
<div class="v2-card">
    <h3>{item.get('name')}</h3>
    <span class="v2-chip v2-chip-green">{item.get('quantity')} {item.get('unit')}</span>
    <span class="v2-chip v2-chip-blue">{item.get('category')}</span>
</div>
""",
                        unsafe_allow_html=True,
                    )

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
                    st.markdown(
                        f"""
<div class="v2-card">
    <h3>{item.get('name')}</h3>
    <span class="v2-chip v2-chip-green">{item.get('quantity')} {item.get('unit')}</span>
    <span class="v2-chip v2-chip-blue">{item.get('category')}</span>
</div>
""",
                        unsafe_allow_html=True,
                    )

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
        st.metric("Покупок", len([x for x in shopping if x.get("status") != "bought"]))
    with c4:
        st.metric("Калорий сегодня", int(sum(float(x.get("calories") or 0) for x in diary)))

    st.markdown("## Калории по пользователям")

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

    st.markdown(
        f"""
<div class="v2-card">
    <h2>{APP_NAME}</h2>
    <p>Версия: <b>{APP_VERSION}</b></p>
    <p>Разработка: <b>{DEVELOPER}</b></p>
</div>
""",
        unsafe_allow_html=True,
    )

    st.markdown("## Профили")

    cols = st.columns(2)

    for col, (user, info) in zip(cols, USERS.items()):
        with col:
            st.markdown(
                f"""
<div class="v2-card v2-card-soft">
    <h2>{info['emoji']} {user}</h2>
    <span class="v2-chip v2-chip-green">{info['goal']} ккал/день</span>
    <p>{info['description']}</p>
</div>
""",
                unsafe_allow_html=True,
            )

    if st.button("Добавить демо-продукты", use_container_width=True):
        for name, quantity, unit, calories, category, exp, emoji in DEFAULT_PRODUCTS:
            add_product(name, quantity, unit, calories, category, exp, emoji)
        st.success("Демо-продукты добавлены.")
        st.rerun()


def nav_url(tab):
    return f"?tab={tab}"


def set_tab(tab):
    st.session_state["tab"] = tab
    try:
        st.query_params["tab"] = tab
    except Exception:
        pass
    st.rerun()


def render_nav_styles():
    st.markdown(
        """
<style>
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
    background: rgba(255,255,255,.86);
    border: 1px solid rgba(18,51,33,.10);
    box-shadow: 0 14px 36px rgba(15,23,42,.08);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
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
    transition: all .15s ease;
    border: 1px solid transparent;
}

.v2-top-nav a:hover {
    background: rgba(34,197,94,.13);
    border-color: rgba(34,197,94,.20);
    transform: translateY(-1px);
}

.v2-top-nav a.active {
    background: linear-gradient(135deg, rgba(34,197,94,.22), rgba(240,253,244,.96));
    border-color: rgba(34,197,94,.30);
    box-shadow: 0 8px 20px rgba(15,23,42,.07);
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

.v2-sidebar-link:hover {
    background: rgba(34,197,94,.12);
    border-color: rgba(34,197,94,.18);
}

.v2-sidebar-link.active {
    background: linear-gradient(135deg, rgba(34,197,94,.22), rgba(240,253,244,.96));
    border-color: rgba(34,197,94,.30);
    box-shadow: 0 8px 20px rgba(15,23,42,.06);
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

.v2-action-link:hover {
    background: rgba(34,197,94,.11);
    transform: translateY(-1px);
}

.v2-bottom-nav {
    display: none;
}

@media (max-width: 900px) {
    .v2-top-nav {
        grid-template-columns: repeat(4, minmax(0, 1fr));
        overflow-x: auto;
        position: relative;
        top: auto;
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
        -webkit-backdrop-filter: blur(16px);
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


def render_top_nav():
    render_nav_styles()

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


def render_sidebar():
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
        info = USERS.get(user, USERS["Мишка"])

        st.markdown(
            f"""
<div class="v2-card v2-card-soft" style="padding:14px;border-radius:18px;margin-top:10px;">
    <b>{info["emoji"]} Активный пользователь</b><br>
    <span style="color:#647067;">{user}</span>
</div>
""",
            unsafe_allow_html=True,
        )

        st.caption("PIN и авторизация временно отключены до финальной сборки.")

def render_action_links():
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

def render_app():
    apply_design()
    init_tab()
    bottom_nav()
    render_sidebar()
    render_top_nav()

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
    """
    Временно отключенная авторизация для активной разработки v2.

    Сейчас приложение сразу открывается без PIN.
    Пользователь по умолчанию: Мишка.

    Авторизацию вернём в конце, когда закончим дизайн, каталоги,
    фото, сканер и основную логику.
    """
    ensure_schema()
    seed_if_empty()

    if "user" not in st.session_state:
        st.session_state["user"] = "Мишка"

    st.session_state["authenticated"] = True

    render_app()

if __name__ == "__main__":
    main()
