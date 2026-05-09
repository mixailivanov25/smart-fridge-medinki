import sqlite3
from datetime import datetime
import os

DB_PATH = "data/fridge.db"


def get_connection():
    os.makedirs("data", exist_ok=True)
    return sqlite3.connect(DB_PATH)


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        quantity REAL NOT NULL,
        unit TEXT NOT NULL,
        calories_per_100g REAL DEFAULT 0,
        category TEXT,
        expiration_date TEXT,
        created_at TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS cooking_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        dish_name TEXT NOT NULL,
        ingredients_used TEXT,
        calories REAL,
        cooked_at TEXT
    )
    """)

    cursor.execute("""
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

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS favorite_dishes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        person TEXT NOT NULL,
        dish_name TEXT NOT NULL,
        source TEXT DEFAULT 'recipe',
        rating INTEGER DEFAULT 5,
        notes TEXT,
        created_at TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS accepted_week_menus (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        status TEXT DEFAULT 'accepted',
        notes TEXT,
        accepted_at TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS accepted_week_menu_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
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

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS product_transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
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

    default_profiles = [
        ("Мишка", 2300, "Поддержание веса", 4, 1, "курица, рис, творог, мясо, паста", "рыба", ""),
        ("Мединка", 1800, "Правильное питание", 4, 1, "салаты, овощи, творог, курица, овсянка", "жирное", "")
    ]

    for profile in default_profiles:
        cursor.execute("""
        INSERT OR IGNORE INTO user_profiles
        (person, target_calories, goal, meals_per_day, protein_focus, preferences, dislikes, allergies, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            profile[0],
            profile[1],
            profile[2],
            profile[3],
            profile[4],
            profile[5],
            profile[6],
            profile[7],
            datetime.now().isoformat(timespec="seconds")
        ))

    conn.commit()
    conn.close()


def add_or_update_product(name, quantity, unit, calories_per_100g=0, category="", expiration_date=""):
    name = name.lower().strip()
    unit = unit.strip()

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT id, quantity, calories_per_100g, category, expiration_date
    FROM products
    WHERE LOWER(name) = ? AND unit = ?
    """, (name, unit))

    existing = cursor.fetchone()

    if existing:
        product_id, old_quantity, old_calories, old_category, old_expiration = existing

        cursor.execute("""
        UPDATE products
        SET quantity = ?, calories_per_100g = ?, category = ?, expiration_date = ?
        WHERE id = ?
        """, (
            old_quantity + quantity,
            calories_per_100g if calories_per_100g else old_calories,
            category if category else old_category,
            expiration_date if expiration_date else old_expiration,
            product_id
        ))
    else:
        cursor.execute("""
        INSERT INTO products 
        (name, quantity, unit, calories_per_100g, category, expiration_date, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            name,
            quantity,
            unit,
            calories_per_100g,
            category,
            expiration_date,
            datetime.now().isoformat(timespec="seconds")
        ))

    conn.commit()
    conn.close()


def get_products():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT id, name, quantity, unit, calories_per_100g, category, expiration_date
    FROM products
    ORDER BY name
    """)

    rows = cursor.fetchall()
    conn.close()
    return rows


def get_product_by_id(product_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT id, name, quantity, unit, calories_per_100g, category, expiration_date
    FROM products
    WHERE id = ?
    """, (product_id,))

    row = cursor.fetchone()
    conn.close()
    return row


def update_product(product_id, name, quantity, unit, calories_per_100g=0, category="", expiration_date=""):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE products
    SET name = ?, quantity = ?, unit = ?, calories_per_100g = ?, category = ?, expiration_date = ?
    WHERE id = ?
    """, (
        name.lower().strip(),
        quantity,
        unit,
        calories_per_100g,
        category,
        expiration_date,
        product_id
    ))

    conn.commit()
    conn.close()


def reduce_product_quantity(product_id, amount):
    product = get_product_by_id(product_id)

    if not product:
        return

    old_quantity = product[2]
    new_quantity = old_quantity - amount

    conn = get_connection()
    cursor = conn.cursor()

    if new_quantity <= 0:
        cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
    else:
        cursor.execute("""
        UPDATE products
        SET quantity = ?
        WHERE id = ?
        """, (new_quantity, product_id))

    conn.commit()
    conn.close()


def delete_product(product_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
    conn.commit()
    conn.close()


def add_cooking_history(dish_name, ingredients_used, calories):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO cooking_history
    (dish_name, ingredients_used, calories, cooked_at)
    VALUES (?, ?, ?, ?)
    """, (
        dish_name,
        ingredients_used,
        calories,
        datetime.now().isoformat(timespec="seconds")
    ))

    conn.commit()
    conn.close()


def get_history():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT dish_name, ingredients_used, calories, cooked_at
    FROM cooking_history
    ORDER BY cooked_at DESC
    """)

    rows = cursor.fetchall()
    conn.close()
    return rows


def get_user_profiles():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT person, target_calories, goal, meals_per_day, protein_focus, preferences, dislikes, allergies, updated_at
    FROM user_profiles
    """)

    rows = cursor.fetchall()
    conn.close()

    order = {"Мишка": 0, "Мединка": 1}
    return sorted(rows, key=lambda row: order.get(row[0], 999))


def get_user_profile(person):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT person, target_calories, goal, meals_per_day, protein_focus, preferences, dislikes, allergies, updated_at
    FROM user_profiles
    WHERE person = ?
    """, (person,))

    row = cursor.fetchone()
    conn.close()
    return row


def update_user_profile(person, target_calories, goal, meals_per_day, protein_focus, preferences, dislikes, allergies):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO user_profiles
    (person, target_calories, goal, meals_per_day, protein_focus, preferences, dislikes, allergies, updated_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ON CONFLICT(person) DO UPDATE SET
        target_calories = excluded.target_calories,
        goal = excluded.goal,
        meals_per_day = excluded.meals_per_day,
        protein_focus = excluded.protein_focus,
        preferences = excluded.preferences,
        dislikes = excluded.dislikes,
        allergies = excluded.allergies,
        updated_at = excluded.updated_at
    """, (
        person,
        int(target_calories),
        goal,
        int(meals_per_day),
        int(protein_focus),
        preferences,
        dislikes,
        allergies,
        datetime.now().isoformat(timespec="seconds")
    ))

    conn.commit()
    conn.close()


def add_favorite_dish(person, dish_name, source="recipe", rating=5, notes=""):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO favorite_dishes
    (person, dish_name, source, rating, notes, created_at)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (
        person,
        dish_name,
        source,
        int(rating),
        notes,
        datetime.now().isoformat(timespec="seconds")
    ))

    conn.commit()
    conn.close()


def get_favorite_dishes(person=None):
    conn = get_connection()
    cursor = conn.cursor()

    if person:
        cursor.execute("""
        SELECT id, person, dish_name, source, rating, notes, created_at
        FROM favorite_dishes
        WHERE person = ?
        ORDER BY created_at DESC
        """, (person,))
    else:
        cursor.execute("""
        SELECT id, person, dish_name, source, rating, notes, created_at
        FROM favorite_dishes
        ORDER BY created_at DESC
        """)

    rows = cursor.fetchall()
    conn.close()
    return rows


def delete_favorite_dish(favorite_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM favorite_dishes WHERE id = ?", (favorite_id,))
    conn.commit()
    conn.close()


def create_accepted_week_menu(title, notes=""):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO accepted_week_menus
    (title, status, notes, accepted_at)
    VALUES (?, ?, ?, ?)
    """, (
        title,
        "accepted",
        notes,
        datetime.now().isoformat(timespec="seconds")
    ))

    menu_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return menu_id


def add_accepted_week_menu_item(menu_id, person, day, meal_slot, dish_name, calories, is_favorite=False):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO accepted_week_menu_items
    (menu_id, person, day, meal_slot, dish_name, calories, is_favorite, created_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        menu_id,
        person,
        day,
        meal_slot,
        dish_name,
        calories,
        int(is_favorite),
        datetime.now().isoformat(timespec="seconds")
    ))

    conn.commit()
    conn.close()


def get_accepted_week_menus():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT id, title, status, notes, accepted_at
    FROM accepted_week_menus
    ORDER BY accepted_at DESC
    """)

    rows = cursor.fetchall()
    conn.close()
    return rows


def get_accepted_week_menu_items(menu_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT id, menu_id, person, day, meal_slot, dish_name, calories, is_favorite, created_at
    FROM accepted_week_menu_items
    WHERE menu_id = ?
    ORDER BY id
    """, (menu_id,))

    rows = cursor.fetchall()
    conn.close()
    return rows


def add_product_transaction(product_id, product_name, change_amount, unit, action, reason="", dish_name="", person="", day="", meal_slot=""):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO product_transactions
    (product_id, product_name, change_amount, unit, action, reason, dish_name, person, day, meal_slot, created_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
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
        datetime.now().isoformat(timespec="seconds")
    ))

    conn.commit()
    conn.close()


def get_product_transactions(limit=300):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT id, product_id, product_name, change_amount, unit, action, reason, dish_name, person, day, meal_slot, created_at
    FROM product_transactions
    ORDER BY created_at DESC
    LIMIT ?
    """, (limit,))

    rows = cursor.fetchall()
    conn.close()
    return rows


def clear_products():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM products")
    conn.commit()
    conn.close()


def clear_all_data():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM products")
    cursor.execute("DELETE FROM cooking_history")
    cursor.execute("DELETE FROM favorite_dishes")
    cursor.execute("DELETE FROM accepted_week_menu_items")
    cursor.execute("DELETE FROM accepted_week_menus")
    cursor.execute("DELETE FROM product_transactions")

    conn.commit()
    conn.close()


# -----------------------------
# v0.7 Menu safety and cancel
# -----------------------------
def get_latest_accepted_week_menu():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT id, title, status, notes, accepted_at
    FROM accepted_week_menus
    WHERE status = 'accepted'
    ORDER BY accepted_at DESC
    LIMIT 1
    """)

    row = cursor.fetchone()
    conn.close()

    return row


def update_accepted_week_menu_status(menu_id, status, notes=""):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE accepted_week_menus
    SET status = ?, notes = ?
    WHERE id = ?
    """, (
        status,
        notes,
        menu_id
    ))

    conn.commit()
    conn.close()


def get_spend_transactions_after(timestamp):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT id, product_id, product_name, change_amount, unit, action, reason, dish_name, person, day, meal_slot, created_at
    FROM product_transactions
    WHERE created_at >= ?
      AND action IN ('spend', 'spend_partial')
    ORDER BY created_at ASC
    """, (timestamp,))

    rows = cursor.fetchall()
    conn.close()

    return rows


def cancel_latest_accepted_week_menu():
    """
    Отменяет последнее принятое меню:
    - находит последнее меню со статусом accepted;
    - возвращает продукты по транзакциям списания после даты принятия меню;
    - добавляет обратные транзакции return;
    - помечает меню как canceled.

    Важно: восстановление продукта идёт по названию и единице.
    Если продукт был полностью удалён, он вернётся без категории и калорийности.
    """
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
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS nutrition_diary (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
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

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS shopping_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
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

    conn.commit()
    conn.close()


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

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO nutrition_diary
    (person, diary_date, meal_slot, dish_name, calories, protein, fat, carbs, comment, created_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        person,
        str(diary_date),
        meal_slot,
        dish_name,
        float(calories or 0),
        float(protein or 0),
        float(fat or 0),
        float(carbs or 0),
        comment,
        datetime.now().isoformat(timespec="seconds")
    ))

    conn.commit()
    conn.close()


def get_nutrition_diary_entries(person=None, diary_date=None, limit=500):
    ensure_v08_tables()

    conn = get_connection()
    cursor = conn.cursor()

    query = """
    SELECT id, person, diary_date, meal_slot, dish_name, calories, protein, fat, carbs, comment, created_at
    FROM nutrition_diary
    WHERE 1 = 1
    """

    params = []

    if person:
        query += " AND person = ?"
        params.append(person)

    if diary_date:
        query += " AND diary_date = ?"
        params.append(str(diary_date))

    query += " ORDER BY diary_date DESC, created_at DESC LIMIT ?"
    params.append(int(limit))

    cursor.execute(query, params)

    rows = cursor.fetchall()
    conn.close()

    return rows


def delete_nutrition_diary_entry(entry_id):
    ensure_v08_tables()

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM nutrition_diary WHERE id = ?", (entry_id,))

    conn.commit()
    conn.close()


def get_daily_calories(person, diary_date):
    ensure_v08_tables()

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT COALESCE(SUM(calories), 0)
    FROM nutrition_diary
    WHERE person = ? AND diary_date = ?
    """, (
        person,
        str(diary_date)
    ))

    value = cursor.fetchone()[0] or 0
    conn.close()

    return round(value)


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

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO shopping_items
    (name, amount, unit, category, calories_per_100g, expiration_date, source, is_bought, created_at, bought_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        name.lower().strip(),
        float(amount),
        unit,
        category,
        float(calories_per_100g or 0),
        expiration_date,
        source,
        0,
        datetime.now().isoformat(timespec="seconds"),
        ""
    ))

    conn.commit()
    conn.close()


def get_shopping_items(include_bought=True):
    ensure_v08_tables()

    conn = get_connection()
    cursor = conn.cursor()

    if include_bought:
        cursor.execute("""
        SELECT id, name, amount, unit, category, calories_per_100g, expiration_date, source, is_bought, created_at, bought_at
        FROM shopping_items
        ORDER BY is_bought ASC, category ASC, name ASC
        """)
    else:
        cursor.execute("""
        SELECT id, name, amount, unit, category, calories_per_100g, expiration_date, source, is_bought, created_at, bought_at
        FROM shopping_items
        WHERE is_bought = 0
        ORDER BY category ASC, name ASC
        """)

    rows = cursor.fetchall()
    conn.close()

    return rows


def mark_shopping_item_bought(item_id):
    ensure_v08_tables()

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE shopping_items
    SET is_bought = 1, bought_at = ?
    WHERE id = ?
    """, (
        datetime.now().isoformat(timespec="seconds"),
        item_id
    ))

    conn.commit()
    conn.close()


def delete_shopping_item(item_id):
    ensure_v08_tables()

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM shopping_items WHERE id = ?", (item_id,))

    conn.commit()
    conn.close()


def get_shopping_item_by_id(item_id):
    ensure_v08_tables()

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT id, name, amount, unit, category, calories_per_100g, expiration_date, source, is_bought, created_at, bought_at
    FROM shopping_items
    WHERE id = ?
    """, (item_id,))

    row = cursor.fetchone()
    conn.close()

    return row


def add_shopping_item_to_fridge(item_id):
    """
    Помечает покупку купленной и добавляет продукт в холодильник.
    """
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
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS custom_recipes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
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

    conn.commit()
    conn.close()


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

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO custom_recipes
    (
        name,
        category,
        cooking_time,
        calories,
        protein,
        fat,
        carbs,
        ingredients_text,
        instructions_text,
        history,
        origin,
        notes,
        emoji,
        created_at
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        name.strip(),
        category.strip(),
        cooking_time.strip(),
        float(calories or 0),
        float(protein or 0),
        float(fat or 0),
        float(carbs or 0),
        ingredients_text.strip(),
        instructions_text.strip(),
        history.strip(),
        origin.strip(),
        notes.strip(),
        emoji.strip() or "🍽️",
        datetime.now().isoformat(timespec="seconds")
    ))

    conn.commit()
    conn.close()


def get_custom_recipes(query="", category=""):
    ensure_v09_tables()

    conn = get_connection()
    cursor = conn.cursor()

    sql = """
    SELECT
        id,
        name,
        category,
        cooking_time,
        calories,
        protein,
        fat,
        carbs,
        ingredients_text,
        instructions_text,
        history,
        origin,
        notes,
        emoji,
        created_at
    FROM custom_recipes
    WHERE 1 = 1
    """

    params = []

    if query:
        sql += """
        AND (
            LOWER(name) LIKE ?
            OR LOWER(category) LIKE ?
            OR LOWER(ingredients_text) LIKE ?
            OR LOWER(notes) LIKE ?
        )
        """
        q = f"%{query.lower().strip()}%"
        params.extend([q, q, q, q])

    if category and category != "Все категории":
        sql += " AND category = ?"
        params.append(category)

    sql += " ORDER BY created_at DESC"

    cursor.execute(sql, params)

    rows = cursor.fetchall()
    conn.close()

    return rows


def get_custom_recipe_by_id(recipe_id):
    ensure_v09_tables()

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT
        id,
        name,
        category,
        cooking_time,
        calories,
        protein,
        fat,
        carbs,
        ingredients_text,
        instructions_text,
        history,
        origin,
        notes,
        emoji,
        created_at
    FROM custom_recipes
    WHERE id = ?
    """, (recipe_id,))

    row = cursor.fetchone()
    conn.close()

    return row


def delete_custom_recipe(recipe_id):
    ensure_v09_tables()

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM custom_recipes WHERE id = ?", (recipe_id,))

    conn.commit()
    conn.close()


def get_custom_recipe_categories():
    ensure_v09_tables()

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT DISTINCT category
    FROM custom_recipes
    WHERE category IS NOT NULL AND TRIM(category) != ''
    ORDER BY category
    """)

    rows = cursor.fetchall()
    conn.close()

    return [row[0] for row in rows]

