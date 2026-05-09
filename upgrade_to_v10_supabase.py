from pathlib import Path
from datetime import datetime
import shutil
import py_compile
import subprocess


PROJECT_DIR = Path(__file__).resolve().parent

DB_FILE = PROJECT_DIR / "database.py"
SETTINGS_FILE = PROJECT_DIR / "settings.py"
REQ_FILE = PROJECT_DIR / "requirements.txt"


DATABASE_PY = r'''
import os
from datetime import datetime

from sqlalchemy import create_engine, text


DB_PATH = "data/fridge.db"


_ENGINE = None


def get_database_url():
    """
    Приоритет:
    1. DATABASE_URL из переменных окружения
    2. DATABASE_URL из Streamlit secrets
    3. локальная SQLite база
    """
    env_url = os.getenv("DATABASE_URL")

    if env_url:
        return env_url

    try:
        import streamlit as st

        if "DATABASE_URL" in st.secrets:
            return st.secrets["DATABASE_URL"]
    except Exception:
        pass

    os.makedirs("data", exist_ok=True)
    return f"sqlite:///{DB_PATH}"


def normalize_database_url(url):
    """
    Supabase обычно даёт postgresql://...
    SQLAlchemy с psycopg2 понимает postgresql+psycopg2://...
    """
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)

    if url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+psycopg2://", 1)

    return url


def get_engine():
    global _ENGINE

    if _ENGINE is None:
        url = normalize_database_url(get_database_url())

        if url.startswith("sqlite"):
            _ENGINE = create_engine(
                url,
                future=True,
                connect_args={"check_same_thread": False}
            )
        else:
            _ENGINE = create_engine(
                url,
                future=True,
                pool_pre_ping=True
            )

    return _ENGINE


def get_db_kind():
    return get_engine().dialect.name


def execute(sql, params=None):
    params = params or {}

    with get_engine().begin() as conn:
        conn.execute(text(sql), params)


def fetchone(sql, params=None):
    params = params or {}

    with get_engine().connect() as conn:
        row = conn.execute(text(sql), params).fetchone()

    return tuple(row) if row else None


def fetchall(sql, params=None):
    params = params or {}

    with get_engine().connect() as conn:
        rows = conn.execute(text(sql), params).fetchall()

    return [tuple(row) for row in rows]


def insert_and_get_id(sql_sqlite, sql_postgres, params=None):
    params = params or {}

    with get_engine().begin() as conn:
        if get_db_kind() == "postgresql":
            row = conn.execute(text(sql_postgres), params).fetchone()
            return row[0]
        else:
            result = conn.execute(text(sql_sqlite), params)
            return result.lastrowid


def init_db():
    db_kind = get_db_kind()

    if db_kind == "postgresql":
        id_col = "SERIAL PRIMARY KEY"
    else:
        id_col = "INTEGER PRIMARY KEY AUTOINCREMENT"

    execute(f"""
    CREATE TABLE IF NOT EXISTS products (
        id {id_col},
        name TEXT NOT NULL,
        quantity REAL NOT NULL,
        unit TEXT NOT NULL,
        calories_per_100g REAL DEFAULT 0,
        category TEXT,
        expiration_date TEXT,
        created_at TEXT
    )
    """)

    execute(f"""
    CREATE TABLE IF NOT EXISTS cooking_history (
        id {id_col},
        dish_name TEXT NOT NULL,
        ingredients_used TEXT,
        calories REAL,
        cooked_at TEXT
    )
    """)

    execute("""
    CREATE TABLE IF NOT EXISTS user_profiles (
        person TEXT PRIMARY KEY,
        target_calories INTEGER DEFAULT 2000,
        goal TEXT DEFAULT 'Поддержание веса',
        meals_per_day INTEGER DEFAULT 3,
        protein_focus INTEGER DEFAULT 0,
        preferences TEXT DEFAULT '',
        dislikes TEXT DEFAULT '',
        allergies TEXT DEFAULT '',
        updated_at TEXT
    )
    """)

    execute(f"""
    CREATE TABLE IF NOT EXISTS favorite_dishes (
        id {id_col},
        person TEXT NOT NULL,
        dish_name TEXT NOT NULL,
        source TEXT DEFAULT 'recipe',
        rating INTEGER DEFAULT 5,
        notes TEXT,
        created_at TEXT
    )
    """)

    execute(f"""
    CREATE TABLE IF NOT EXISTS accepted_week_menus (
        id {id_col},
        title TEXT NOT NULL,
        status TEXT DEFAULT 'accepted',
        notes TEXT,
        accepted_at TEXT
    )
    """)

    execute(f"""
    CREATE TABLE IF NOT EXISTS accepted_week_menu_items (
        id {id_col},
        menu_id INTEGER NOT NULL,
        person TEXT NOT NULL,
        day TEXT NOT NULL,
        meal_slot TEXT NOT NULL,
        dish_name TEXT NOT NULL,
        calories REAL DEFAULT 0,
        is_favorite INTEGER DEFAULT 0,
        created_at TEXT
    )
    """)

    execute(f"""
    CREATE TABLE IF NOT EXISTS product_transactions (
        id {id_col},
        product_id INTEGER,
        product_name TEXT NOT NULL,
        change_amount REAL NOT NULL,
        unit TEXT NOT NULL,
        action TEXT NOT NULL,
        reason TEXT,
        dish_name TEXT,
        person TEXT,
        day TEXT,
        meal_slot TEXT,
        created_at TEXT
    )
    """)

    ensure_v08_tables()
    ensure_v09_tables()

    default_profiles = [
        ("Мишка", 2300, "Поддержание веса", 4, 1, "курица, рис, творог, мясо, паста", "рыба", ""),
        ("Мединка", 1800, "Правильное питание", 4, 1, "салаты, овощи, творог, курица, овсянка", "жирное", "")
    ]

    for profile in default_profiles:
        existing = get_user_profile(profile[0])

        if not existing:
            update_user_profile(
                person=profile[0],
                target_calories=profile[1],
                goal=profile[2],
                meals_per_day=profile[3],
                protein_focus=profile[4],
                preferences=profile[5],
                dislikes=profile[6],
                allergies=profile[7]
            )


# -----------------------------
# Products
# -----------------------------
def add_product(name, quantity, unit, calories_per_100g=0, category="", expiration_date=""):
    execute("""
    INSERT INTO products
    (name, quantity, unit, calories_per_100g, category, expiration_date, created_at)
    VALUES (:name, :quantity, :unit, :calories_per_100g, :category, :expiration_date, :created_at)
    """, {
        "name": name.lower().strip(),
        "quantity": quantity,
        "unit": unit,
        "calories_per_100g": calories_per_100g,
        "category": category,
        "expiration_date": expiration_date,
        "created_at": datetime.now().isoformat(timespec="seconds")
    })


def add_or_update_product(name, quantity, unit, calories_per_100g=0, category="", expiration_date=""):
    name = name.lower().strip()
    unit = unit.strip()

    existing = fetchone("""
    SELECT id, quantity, calories_per_100g, category, expiration_date
    FROM products
    WHERE LOWER(name) = :name AND unit = :unit
    """, {
        "name": name,
        "unit": unit
    })

    if existing:
        product_id, old_quantity, old_calories, old_category, old_expiration = existing

        execute("""
        UPDATE products
        SET quantity = :quantity,
            calories_per_100g = :calories_per_100g,
            category = :category,
            expiration_date = :expiration_date
        WHERE id = :id
        """, {
            "quantity": old_quantity + quantity,
            "calories_per_100g": calories_per_100g if calories_per_100g else old_calories,
            "category": category if category else old_category,
            "expiration_date": expiration_date if expiration_date else old_expiration,
            "id": product_id
        })
    else:
        add_product(
            name=name,
            quantity=quantity,
            unit=unit,
            calories_per_100g=calories_per_100g,
            category=category,
            expiration_date=expiration_date
        )


def get_products():
    return fetchall("""
    SELECT id, name, quantity, unit, calories_per_100g, category, expiration_date
    FROM products
    ORDER BY name
    """)


def get_product_by_id(product_id):
    return fetchone("""
    SELECT id, name, quantity, unit, calories_per_100g, category, expiration_date
    FROM products
    WHERE id = :id
    """, {
        "id": product_id
    })


def update_product(product_id, name, quantity, unit, calories_per_100g=0, category="", expiration_date=""):
    execute("""
    UPDATE products
    SET name = :name,
        quantity = :quantity,
        unit = :unit,
        calories_per_100g = :calories_per_100g,
        category = :category,
        expiration_date = :expiration_date
    WHERE id = :id
    """, {
        "name": name.lower().strip(),
        "quantity": quantity,
        "unit": unit,
        "calories_per_100g": calories_per_100g,
        "category": category,
        "expiration_date": expiration_date,
        "id": product_id
    })


def reduce_product_quantity(product_id, amount):
    product = get_product_by_id(product_id)

    if not product:
        return

    old_quantity = product[2]
    new_quantity = old_quantity - amount

    if new_quantity <= 0:
        delete_product(product_id)
    else:
        execute("""
        UPDATE products
        SET quantity = :quantity
        WHERE id = :id
        """, {
            "quantity": new_quantity,
            "id": product_id
        })


def delete_product(product_id):
    execute("DELETE FROM products WHERE id = :id", {"id": product_id})


# -----------------------------
# Cooking history
# -----------------------------
def add_cooking_history(dish_name, ingredients_used, calories):
    execute("""
    INSERT INTO cooking_history
    (dish_name, ingredients_used, calories, cooked_at)
    VALUES (:dish_name, :ingredients_used, :calories, :cooked_at)
    """, {
        "dish_name": dish_name,
        "ingredients_used": ingredients_used,
        "calories": calories,
        "cooked_at": datetime.now().isoformat(timespec="seconds")
    })


def get_history():
    return fetchall("""
    SELECT dish_name, ingredients_used, calories, cooked_at
    FROM cooking_history
    ORDER BY cooked_at DESC
    """)


# -----------------------------
# Profiles
# -----------------------------
def get_user_profiles():
    rows = fetchall("""
    SELECT person, target_calories, goal, meals_per_day, protein_focus, preferences, dislikes, allergies, updated_at
    FROM user_profiles
    """)

    order = {"Мишка": 0, "Мединка": 1}
    return sorted(rows, key=lambda row: order.get(row[0], 999))


def get_user_profile(person):
    return fetchone("""
    SELECT person, target_calories, goal, meals_per_day, protein_focus, preferences, dislikes, allergies, updated_at
    FROM user_profiles
    WHERE person = :person
    """, {
        "person": person
    })


def update_user_profile(
    person,
    target_calories,
    goal,
    meals_per_day,
    protein_focus,
    preferences,
    dislikes,
    allergies
):
    existing = get_user_profile(person)

    if existing:
        execute("""
        UPDATE user_profiles
        SET target_calories = :target_calories,
            goal = :goal,
            meals_per_day = :meals_per_day,
            protein_focus = :protein_focus,
            preferences = :preferences,
            dislikes = :dislikes,
            allergies = :allergies,
            updated_at = :updated_at
        WHERE person = :person
        """, {
            "person": person,
            "target_calories": int(target_calories),
            "goal": goal,
            "meals_per_day": int(meals_per_day),
            "protein_focus": int(protein_focus),
            "preferences": preferences,
            "dislikes": dislikes,
            "allergies": allergies,
            "updated_at": datetime.now().isoformat(timespec="seconds")
        })
    else:
        execute("""
        INSERT INTO user_profiles
        (person, target_calories, goal, meals_per_day, protein_focus, preferences, dislikes, allergies, updated_at)
        VALUES (:person, :target_calories, :goal, :meals_per_day, :protein_focus, :preferences, :dislikes, :allergies, :updated_at)
        """, {
            "person": person,
            "target_calories": int(target_calories),
            "goal": goal,
            "meals_per_day": int(meals_per_day),
            "protein_focus": int(protein_focus),
            "preferences": preferences,
            "dislikes": dislikes,
            "allergies": allergies,
            "updated_at": datetime.now().isoformat(timespec="seconds")
        })


# -----------------------------
# Favorite dishes
# -----------------------------
def add_favorite_dish(person, dish_name, source="recipe", rating=5, notes=""):
    execute("""
    INSERT INTO favorite_dishes
    (person, dish_name, source, rating, notes, created_at)
    VALUES (:person, :dish_name, :source, :rating, :notes, :created_at)
    """, {
        "person": person,
        "dish_name": dish_name,
        "source": source,
        "rating": int(rating),
        "notes": notes,
        "created_at": datetime.now().isoformat(timespec="seconds")
    })


def get_favorite_dishes(person=None):
    if person:
        return fetchall("""
        SELECT id, person, dish_name, source, rating, notes, created_at
        FROM favorite_dishes
        WHERE person = :person
        ORDER BY created_at DESC
        """, {
            "person": person
        })

    return fetchall("""
    SELECT id, person, dish_name, source, rating, notes, created_at
    FROM favorite_dishes
    ORDER BY created_at DESC
    """)


def delete_favorite_dish(favorite_id):
    execute("DELETE FROM favorite_dishes WHERE id = :id", {"id": favorite_id})


# -----------------------------
# Accepted week menus
# -----------------------------
def create_accepted_week_menu(title, notes=""):
    params = {
        "title": title,
        "status": "accepted",
        "notes": notes,
        "accepted_at": datetime.now().isoformat(timespec="seconds")
    }

    return insert_and_get_id(
        """
        INSERT INTO accepted_week_menus
        (title, status, notes, accepted_at)
        VALUES (:title, :status, :notes, :accepted_at)
        """,
        """
        INSERT INTO accepted_week_menus
        (title, status, notes, accepted_at)
        VALUES (:title, :status, :notes, :accepted_at)
        RETURNING id
        """,
        params
    )


def add_accepted_week_menu_item(menu_id, person, day, meal_slot, dish_name, calories, is_favorite=False):
    execute("""
    INSERT INTO accepted_week_menu_items
    (menu_id, person, day, meal_slot, dish_name, calories, is_favorite, created_at)
    VALUES (:menu_id, :person, :day, :meal_slot, :dish_name, :calories, :is_favorite, :created_at)
    """, {
        "menu_id": menu_id,
        "person": person,
        "day": day,
        "meal_slot": meal_slot,
        "dish_name": dish_name,
        "calories": calories,
        "is_favorite": int(is_favorite),
        "created_at": datetime.now().isoformat(timespec="seconds")
    })


def get_accepted_week_menus():
    return fetchall("""
    SELECT id, title, status, notes, accepted_at
    FROM accepted_week_menus
    ORDER BY accepted_at DESC
    """)


def get_accepted_week_menu_items(menu_id):
    return fetchall("""
    SELECT id, menu_id, person, day, meal_slot, dish_name, calories, is_favorite, created_at
    FROM accepted_week_menu_items
    WHERE menu_id = :menu_id
    ORDER BY id
    """, {
        "menu_id": menu_id
    })


def get_latest_accepted_week_menu():
    return fetchone("""
    SELECT id, title, status, notes, accepted_at
    FROM accepted_week_menus
    WHERE status = 'accepted'
    ORDER BY accepted_at DESC
    LIMIT 1
    """)


def update_accepted_week_menu_status(menu_id, status, notes=""):
    execute("""
    UPDATE accepted_week_menus
    SET status = :status,
        notes = :notes
    WHERE id = :id
    """, {
        "status": status,
        "notes": notes,
        "id": menu_id
    })


# -----------------------------
# Product transactions
# -----------------------------
def add_product_transaction(
    product_id,
    product_name,
    change_amount,
    unit,
    action,
    reason="",
    dish_name="",
    person="",
    day="",
    meal_slot=""
):
    execute("""
    INSERT INTO product_transactions
    (product_id, product_name, change_amount, unit, action, reason, dish_name, person, day, meal_slot, created_at)
    VALUES (:product_id, :product_name, :change_amount, :unit, :action, :reason, :dish_name, :person, :day, :meal_slot, :created_at)
    """, {
        "product_id": product_id,
        "product_name": product_name,
        "change_amount": change_amount,
        "unit": unit,
        "action": action,
        "reason": reason,
        "dish_name": dish_name,
        "person": person,
        "day": day,
        "meal_slot": meal_slot,
        "created_at": datetime.now().isoformat(timespec="seconds")
    })


def get_product_transactions(limit=300):
    return fetchall("""
    SELECT id, product_id, product_name, change_amount, unit, action, reason, dish_name, person, day, meal_slot, created_at
    FROM product_transactions
    ORDER BY created_at DESC
    LIMIT :limit
    """, {
        "limit": int(limit)
    })


def get_spend_transactions_after(timestamp):
    return fetchall("""
    SELECT id, product_id, product_name, change_amount, unit, action, reason, dish_name, person, day, meal_slot, created_at
    FROM product_transactions
    WHERE created_at >= :timestamp
      AND action IN ('spend', 'spend_partial')
    ORDER BY created_at ASC
    """, {
        "timestamp": timestamp
    })


def cancel_latest_accepted_week_menu():
    latest_menu = get_latest_accepted_week_menu()

    if not latest_menu:
        return {
            "ok": False,
            "message": "Нет принятого меню для отмены.",
            "returned": []
        }

    menu_id, title, status, notes, accepted_at = latest_menu
    transactions = get_spend_transactions_after(accepted_at)

    returned = []

    for tx in transactions:
        (
            tx_id,
            product_id,
            product_name,
            change_amount,
            unit,
            action,
            reason,
            dish_name,
            person,
            day,
            meal_slot,
            created_at
        ) = tx

        if change_amount >= 0:
            continue

        amount_to_return = abs(change_amount)

        add_or_update_product(
            name=product_name,
            quantity=amount_to_return,
            unit=unit,
            calories_per_100g=0,
            category="",
            expiration_date=""
        )

        add_product_transaction(
            product_id=product_id,
            product_name=product_name,
            change_amount=amount_to_return,
            unit=unit,
            action="return",
            reason="cancel_week_menu",
            dish_name=dish_name,
            person=person,
            day=day,
            meal_slot=meal_slot
        )

        returned.append({
            "product_name": product_name,
            "amount": amount_to_return,
            "unit": unit,
            "dish_name": dish_name,
            "person": person,
            "day": day,
            "meal_slot": meal_slot
        })

    new_notes = (notes or "") + f"\\nОтменено: {datetime.now().isoformat(timespec='seconds')}"
    update_accepted_week_menu_status(menu_id, "canceled", new_notes)

    return {
        "ok": True,
        "message": f"Меню ID {menu_id} отменено. Продукты возвращены.",
        "menu_id": menu_id,
        "returned": returned
    }


# -----------------------------
# v0.8 Nutrition diary and smart shopping
# -----------------------------
def ensure_v08_tables():
    db_kind = get_db_kind()

    if db_kind == "postgresql":
        id_col = "SERIAL PRIMARY KEY"
    else:
        id_col = "INTEGER PRIMARY KEY AUTOINCREMENT"

    execute(f"""
    CREATE TABLE IF NOT EXISTS nutrition_diary (
        id {id_col},
        person TEXT NOT NULL,
        diary_date TEXT NOT NULL,
        meal_slot TEXT NOT NULL,
        dish_name TEXT NOT NULL,
        calories REAL DEFAULT 0,
        protein REAL DEFAULT 0,
        fat REAL DEFAULT 0,
        carbs REAL DEFAULT 0,
        comment TEXT DEFAULT '',
        created_at TEXT
    )
    """)

    execute(f"""
    CREATE TABLE IF NOT EXISTS shopping_items (
        id {id_col},
        name TEXT NOT NULL,
        amount REAL NOT NULL,
        unit TEXT NOT NULL,
        category TEXT DEFAULT '',
        calories_per_100g REAL DEFAULT 0,
        expiration_date TEXT DEFAULT '',
        source TEXT DEFAULT 'manual',
        is_bought INTEGER DEFAULT 0,
        created_at TEXT,
        bought_at TEXT
    )
    """)


def add_nutrition_diary_entry(
    person,
    diary_date,
    meal_slot,
    dish_name,
    calories=0,
    protein=0,
    fat=0,
    carbs=0,
    comment=""
):
    ensure_v08_tables()

    execute("""
    INSERT INTO nutrition_diary
    (person, diary_date, meal_slot, dish_name, calories, protein, fat, carbs, comment, created_at)
    VALUES (:person, :diary_date, :meal_slot, :dish_name, :calories, :protein, :fat, :carbs, :comment, :created_at)
    """, {
        "person": person,
        "diary_date": str(diary_date),
        "meal_slot": meal_slot,
        "dish_name": dish_name,
        "calories": float(calories or 0),
        "protein": float(protein or 0),
        "fat": float(fat or 0),
        "carbs": float(carbs or 0),
        "comment": comment,
        "created_at": datetime.now().isoformat(timespec="seconds")
    })


def get_nutrition_diary_entries(person=None, diary_date=None, limit=500):
    ensure_v08_tables()

    sql = """
    SELECT id, person, diary_date, meal_slot, dish_name, calories, protein, fat, carbs, comment, created_at
    FROM nutrition_diary
    WHERE 1 = 1
    """

    params = {}

    if person:
        sql += " AND person = :person"
        params["person"] = person

    if diary_date:
        sql += " AND diary_date = :diary_date"
        params["diary_date"] = str(diary_date)

    sql += " ORDER BY diary_date DESC, created_at DESC LIMIT :limit"
    params["limit"] = int(limit)

    return fetchall(sql, params)


def delete_nutrition_diary_entry(entry_id):
    ensure_v08_tables()
    execute("DELETE FROM nutrition_diary WHERE id = :id", {"id": entry_id})


def get_daily_calories(person, diary_date):
    ensure_v08_tables()

    row = fetchone("""
    SELECT COALESCE(SUM(calories), 0)
    FROM nutrition_diary
    WHERE person = :person AND diary_date = :diary_date
    """, {
        "person": person,
        "diary_date": str(diary_date)
    })

    return round(row[0] if row else 0)


def add_shopping_item(
    name,
    amount,
    unit,
    category="",
    calories_per_100g=0,
    expiration_date="",
    source="manual"
):
    ensure_v08_tables()

    execute("""
    INSERT INTO shopping_items
    (name, amount, unit, category, calories_per_100g, expiration_date, source, is_bought, created_at, bought_at)
    VALUES (:name, :amount, :unit, :category, :calories_per_100g, :expiration_date, :source, :is_bought, :created_at, :bought_at)
    """, {
        "name": name.lower().strip(),
        "amount": float(amount),
        "unit": unit,
        "category": category,
        "calories_per_100g": float(calories_per_100g or 0),
        "expiration_date": expiration_date,
        "source": source,
        "is_bought": 0,
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "bought_at": ""
    })


def get_shopping_items(include_bought=True):
    ensure_v08_tables()

    if include_bought:
        return fetchall("""
        SELECT id, name, amount, unit, category, calories_per_100g, expiration_date, source, is_bought, created_at, bought_at
        FROM shopping_items
        ORDER BY is_bought ASC, category ASC, name ASC
        """)

    return fetchall("""
    SELECT id, name, amount, unit, category, calories_per_100g, expiration_date, source, is_bought, created_at, bought_at
    FROM shopping_items
    WHERE is_bought = 0
    ORDER BY category ASC, name ASC
    """)


def mark_shopping_item_bought(item_id):
    ensure_v08_tables()

    execute("""
    UPDATE shopping_items
    SET is_bought = 1,
        bought_at = :bought_at
    WHERE id = :id
    """, {
        "bought_at": datetime.now().isoformat(timespec="seconds"),
        "id": item_id
    })


def delete_shopping_item(item_id):
    ensure_v08_tables()
    execute("DELETE FROM shopping_items WHERE id = :id", {"id": item_id})


def get_shopping_item_by_id(item_id):
    ensure_v08_tables()

    return fetchone("""
    SELECT id, name, amount, unit, category, calories_per_100g, expiration_date, source, is_bought, created_at, bought_at
    FROM shopping_items
    WHERE id = :id
    """, {
        "id": item_id
    })


def add_shopping_item_to_fridge(item_id):
    ensure_v08_tables()

    item = get_shopping_item_by_id(item_id)

    if not item:
        return {
            "ok": False,
            "message": "Позиция списка покупок не найдена."
        }

    (
        row_id,
        name,
        amount,
        unit,
        category,
        calories_per_100g,
        expiration_date,
        source,
        is_bought,
        created_at,
        bought_at
    ) = item

    add_or_update_product(
        name=name,
        quantity=amount,
        unit=unit,
        calories_per_100g=calories_per_100g,
        category=category,
        expiration_date=expiration_date
    )

    mark_shopping_item_bought(item_id)

    add_product_transaction(
        product_id=None,
        product_name=name,
        change_amount=amount,
        unit=unit,
        action="purchase",
        reason="smart_shopping",
        dish_name="",
        person="",
        day="",
        meal_slot=""
    )

    return {
        "ok": True,
        "message": f"Покупка «{name}» добавлена в холодильник.",
        "name": name,
        "amount": amount,
        "unit": unit
    }


# -----------------------------
# v0.9 Custom recipes
# -----------------------------
def ensure_v09_tables():
    db_kind = get_db_kind()

    if db_kind == "postgresql":
        id_col = "SERIAL PRIMARY KEY"
    else:
        id_col = "INTEGER PRIMARY KEY AUTOINCREMENT"

    execute(f"""
    CREATE TABLE IF NOT EXISTS custom_recipes (
        id {id_col},
        name TEXT NOT NULL,
        category TEXT DEFAULT '',
        cooking_time TEXT DEFAULT '',
        calories REAL DEFAULT 0,
        protein REAL DEFAULT 0,
        fat REAL DEFAULT 0,
        carbs REAL DEFAULT 0,
        ingredients_text TEXT DEFAULT '',
        instructions_text TEXT DEFAULT '',
        history TEXT DEFAULT '',
        origin TEXT DEFAULT '',
        notes TEXT DEFAULT '',
        emoji TEXT DEFAULT '🍽️',
        created_at TEXT
    )
    """)


def add_custom_recipe(
    name,
    category="",
    cooking_time="",
    calories=0,
    protein=0,
    fat=0,
    carbs=0,
    ingredients_text="",
    instructions_text="",
    history="",
    origin="",
    notes="",
    emoji="🍽️"
):
    ensure_v09_tables()

    execute("""
    INSERT INTO custom_recipes
    (
        name, category, cooking_time, calories, protein, fat, carbs,
        ingredients_text, instructions_text, history, origin, notes, emoji, created_at
    )
    VALUES
    (
        :name, :category, :cooking_time, :calories, :protein, :fat, :carbs,
        :ingredients_text, :instructions_text, :history, :origin, :notes, :emoji, :created_at
    )
    """, {
        "name": name.strip(),
        "category": category.strip(),
        "cooking_time": cooking_time.strip(),
        "calories": float(calories or 0),
        "protein": float(protein or 0),
        "fat": float(fat or 0),
        "carbs": float(carbs or 0),
        "ingredients_text": ingredients_text.strip(),
        "instructions_text": instructions_text.strip(),
        "history": history.strip(),
        "origin": origin.strip(),
        "notes": notes.strip(),
        "emoji": emoji.strip() or "🍽️",
        "created_at": datetime.now().isoformat(timespec="seconds")
    })


def get_custom_recipes(query="", category=""):
    ensure_v09_tables()

    sql = """
    SELECT
        id, name, category, cooking_time, calories, protein, fat, carbs,
        ingredients_text, instructions_text, history, origin, notes, emoji, created_at
    FROM custom_recipes
    WHERE 1 = 1
    """

    params = {}

    if query:
        sql += """
        AND (
            LOWER(name) LIKE :query
            OR LOWER(category) LIKE :query
            OR LOWER(ingredients_text) LIKE :query
            OR LOWER(notes) LIKE :query
        )
        """
        params["query"] = f"%{query.lower().strip()}%"

    if category and category != "Все категории":
        sql += " AND category = :category"
        params["category"] = category

    sql += " ORDER BY created_at DESC"

    return fetchall(sql, params)


def get_custom_recipe_by_id(recipe_id):
    ensure_v09_tables()

    return fetchone("""
    SELECT
        id, name, category, cooking_time, calories, protein, fat, carbs,
        ingredients_text, instructions_text, history, origin, notes, emoji, created_at
    FROM custom_recipes
    WHERE id = :id
    """, {
        "id": recipe_id
    })


def delete_custom_recipe(recipe_id):
    ensure_v09_tables()
    execute("DELETE FROM custom_recipes WHERE id = :id", {"id": recipe_id})


def get_custom_recipe_categories():
    ensure_v09_tables()

    rows = fetchall("""
    SELECT DISTINCT category
    FROM custom_recipes
    WHERE category IS NOT NULL AND TRIM(category) != ''
    ORDER BY category
    """)

    return [row[0] for row in rows]


# -----------------------------
# Clear data
# -----------------------------
def clear_products():
    execute("DELETE FROM products")


def clear_all_data():
    execute("DELETE FROM products")
    execute("DELETE FROM cooking_history")
    execute("DELETE FROM favorite_dishes")
    execute("DELETE FROM accepted_week_menu_items")
    execute("DELETE FROM accepted_week_menus")
    execute("DELETE FROM product_transactions")
    ensure_v08_tables()
    ensure_v09_tables()
    execute("DELETE FROM nutrition_diary")
    execute("DELETE FROM shopping_items")
    execute("DELETE FROM custom_recipes")
'''


def run(command, check=False):
    print(f"\n▶️ {command}")

    result = subprocess.run(
        command,
        shell=True,
        cwd=PROJECT_DIR,
        text=True,
        capture_output=True
    )

    if result.stdout:
        print(result.stdout)

    if result.stderr:
        print(result.stderr)

    if check and result.returncode != 0:
        raise RuntimeError(f"Команда завершилась с ошибкой: {command}")

    return result


def backup_files():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = PROJECT_DIR / f"backup_before_v10_supabase_{timestamp}"
    backup_dir.mkdir(exist_ok=True)

    for file_path in [DB_FILE, SETTINGS_FILE, REQ_FILE]:
        if file_path.exists():
            shutil.copy2(file_path, backup_dir / file_path.name)

    print(f"📦 Backup создан: {backup_dir.name}")


def update_settings():
    if SETTINGS_FILE.exists():
        text = SETTINGS_FILE.read_text(encoding="utf-8")
    else:
        text = ""

    if "APP_VERSION" in text:
        import re
        text = re.sub(r'APP_VERSION\s*=\s*"[^"]+"', 'APP_VERSION = "v1.0"', text)
    else:
        text += '\nAPP_VERSION = "v1.0"\n'

    SETTINGS_FILE.write_text(text, encoding="utf-8")
    print("✅ settings.py обновлён до v1.0")


def update_requirements():
    existing = ""

    if REQ_FILE.exists():
        existing = REQ_FILE.read_text(encoding="utf-8")

    required = [
        "streamlit",
        "pandas",
        "SQLAlchemy",
        "psycopg2-binary"
    ]

    lines = [line.strip() for line in existing.splitlines() if line.strip()]
    lower = {line.lower() for line in lines}

    for item in required:
        if item.lower() not in lower:
            lines.append(item)

    REQ_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("✅ requirements.txt обновлён")


def write_database():
    DB_FILE.write_text(DATABASE_PY.strip() + "\n", encoding="utf-8")
    print("✅ database.py заменён на Supabase-ready версию")


def compile_files():
    print("\nПроверяю синтаксис...")

    files = [
        "database.py",
        "app.py",
        "settings.py",
        "recipes.py",
        "demo_data.py",
        "product_catalog.py",
        "dish_catalog.py",
        "menu_engine.py"
    ]

    ok = True

    for file_name in files:
        path = PROJECT_DIR / file_name

        if not path.exists():
            print(f"⚠️ Нет файла: {file_name}")
            continue

        try:
            py_compile.compile(str(path), doraise=True)
            print(f"✅ OK: {file_name}")
        except Exception as e:
            ok = False
            print(f"❌ Ошибка в {file_name}:")
            print(e)

    return ok


def git_commit_push():
    if not (PROJECT_DIR / ".git").exists():
        print("ℹ️ Git не найден, push пропущен.")
        return

    run("git add .")
    status = run("git status --short")

    if not status.stdout.strip():
        print("ℹ️ Нет изменений для коммита.")
        return

    run('git commit -m "v1.0 Supabase persistent database"', check=False)
    push = run("git push", check=False)

    if push.returncode == 0:
        print("✅ Изменения отправлены на GitHub.")
    else:
        print("⚠️ Не удалось сделать git push автоматически.")
        print("Выполни вручную:")
        print("git add .")
        print('git commit -m "v1.0 Supabase persistent database"')
        print("git push")


def main():
    print("====================================")
    print(" v1.0 Supabase Edition")
    print(" Умный холодильник Мединки")
    print("====================================")

    backup_files()
    update_settings()
    update_requirements()
    write_database()

    ok = compile_files()

    if not ok:
        print("⚠️ Есть ошибки синтаксиса. Пришли текст ошибки.")
        return

    git_commit_push()

    print("\n✅ Готово.")
    print("")
    print("Теперь нужно:")
    print("1. В Streamlit Cloud открыть приложение.")
    print("2. Settings → Secrets.")
    print("3. Добавить DATABASE_URL.")
    print("4. Reboot app.")
    print("")
    print("Формат секрета:")
    print('DATABASE_URL = "postgresql://postgres.xxxxx:password@host:6543/postgres"')


if __name__ == "__main__":
    main()