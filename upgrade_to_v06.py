from pathlib import Path
from datetime import datetime
import shutil
import py_compile
import textwrap


PROJECT_DIR = Path(__file__).resolve().parent

FILES_TO_WRITE = {}


FILES_TO_WRITE["settings.py"] = r'''
APP_NAME = "Умный холодильник Мединки"
APP_VERSION = "v0.6"
DEVELOPER = "Иванов Михаил"

PEOPLE = ["Мишка", "Мединка"]

PERSON_GENITIVE = {
    "Мишка": "Мишки",
    "Мединка": "Мединки"
}

PERSON_EMOJI = {
    "Мишка": "🐻",
    "Мединка": "🌸"
}

NUTRITION_GOALS = [
    "Похудение",
    "Поддержание веса",
    "Набор массы",
    "Правильное питание",
    "Быстро и просто",
    "Бюджетное питание",
    "Больше белка",
    "Меньше сахара"
]

APP_TAGLINE = "Холодильник, рецепты, меню, покупки и списание продуктов в одном месте."
'''


FILES_TO_WRITE["database.py"] = r'''
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
'''


FILES_TO_WRITE["product_catalog.py"] = r'''
from datetime import date, timedelta

PRODUCT_CATALOG = [
    {"name": "картофель", "category": "Овощи", "unit": "кг", "calories": 77, "emoji": "🥔", "storage_days": 21, "image_url": "", "description": "Универсальный овощ для супов, пюре, запекания и жарки."},
    {"name": "морковь", "category": "Овощи", "unit": "шт", "calories": 41, "emoji": "🥕", "storage_days": 21, "image_url": "", "description": "Подходит для супов, салатов и гарниров."},
    {"name": "лук", "category": "Овощи", "unit": "шт", "calories": 40, "emoji": "🧅", "storage_days": 30, "image_url": "", "description": "Базовый продукт для супов, жарки и соусов."},
    {"name": "помидоры", "category": "Овощи", "unit": "шт", "calories": 18, "emoji": "🍅", "storage_days": 5, "image_url": "", "description": "Для салатов, яичницы и соусов."},
    {"name": "огурцы", "category": "Овощи", "unit": "шт", "calories": 15, "emoji": "🥒", "storage_days": 5, "image_url": "", "description": "Свежий овощ для салатов и перекусов."},
    {"name": "перец болгарский", "category": "Овощи", "unit": "шт", "calories": 27, "emoji": "🫑", "storage_days": 7, "image_url": "", "description": "Добавляет цвет и сладость блюдам."},
    {"name": "брокколи", "category": "Овощи", "unit": "г", "calories": 34, "emoji": "🥦", "storage_days": 5, "image_url": "", "description": "Полезный овощ для гарниров и ПП-блюд."},
    {"name": "салат листовой", "category": "Зелень", "unit": "шт", "calories": 15, "emoji": "🥬", "storage_days": 3, "image_url": "", "description": "Основа лёгких салатов."},
    {"name": "укроп", "category": "Зелень", "unit": "шт", "calories": 43, "emoji": "🌿", "storage_days": 4, "image_url": "", "description": "Свежая зелень для супов и салатов."},
    {"name": "петрушка", "category": "Зелень", "unit": "шт", "calories": 36, "emoji": "🌿", "storage_days": 4, "image_url": "", "description": "Зелень для салатов и гарниров."},

    {"name": "яблоко", "category": "Фрукты", "unit": "шт", "calories": 52, "emoji": "🍎", "storage_days": 14, "image_url": "", "description": "Фрукт для перекуса, каши и десертов."},
    {"name": "банан", "category": "Фрукты", "unit": "шт", "calories": 89, "emoji": "🍌", "storage_days": 5, "image_url": "", "description": "Быстрый источник энергии."},
    {"name": "груша", "category": "Фрукты", "unit": "шт", "calories": 57, "emoji": "🍐", "storage_days": 7, "image_url": "", "description": "Сладкий фрукт для перекуса."},
    {"name": "апельсин", "category": "Фрукты", "unit": "шт", "calories": 47, "emoji": "🍊", "storage_days": 14, "image_url": "", "description": "Цитрус для перекуса и сока."},
    {"name": "клубника", "category": "Ягоды", "unit": "г", "calories": 32, "emoji": "🍓", "storage_days": 3, "image_url": "", "description": "Ягода для завтраков и десертов."},
    {"name": "черника", "category": "Ягоды", "unit": "г", "calories": 57, "emoji": "🫐", "storage_days": 4, "image_url": "", "description": "Для каш, смузи и творога."},

    {"name": "молоко", "category": "Молочные продукты", "unit": "л", "calories": 60, "emoji": "🥛", "storage_days": 5, "image_url": "", "description": "Для каш, омлетов и напитков."},
    {"name": "кефир", "category": "Молочные продукты", "unit": "л", "calories": 40, "emoji": "🥛", "storage_days": 7, "image_url": "", "description": "Кисломолочный напиток."},
    {"name": "йогурт", "category": "Молочные продукты", "unit": "шт", "calories": 90, "emoji": "🥣", "storage_days": 7, "image_url": "", "description": "Быстрый перекус с фруктами."},
    {"name": "творог", "category": "Молочные продукты", "unit": "г", "calories": 120, "emoji": "🍚", "storage_days": 5, "image_url": "", "description": "Белковый продукт для завтраков."},
    {"name": "сыр", "category": "Молочные продукты", "unit": "г", "calories": 350, "emoji": "🧀", "storage_days": 14, "image_url": "", "description": "Для салатов, пасты и бутербродов."},
    {"name": "сметана", "category": "Молочные продукты", "unit": "г", "calories": 206, "emoji": "🥣", "storage_days": 7, "image_url": "", "description": "Для супов, соусов и заправок."},

    {"name": "яйца", "category": "Яйца", "unit": "шт", "calories": 157, "emoji": "🥚", "storage_days": 21, "image_url": "", "description": "База для завтраков и салатов."},
    {"name": "курица", "category": "Мясо и птица", "unit": "г", "calories": 165, "emoji": "🍗", "storage_days": 3, "image_url": "", "description": "Универсальный белковый продукт."},
    {"name": "куриное филе", "category": "Мясо и птица", "unit": "г", "calories": 110, "emoji": "🍗", "storage_days": 3, "image_url": "", "description": "Нежирный белковый продукт."},
    {"name": "индейка", "category": "Мясо и птица", "unit": "г", "calories": 135, "emoji": "🦃", "storage_days": 3, "image_url": "", "description": "Диетическое мясо."},
    {"name": "говядина", "category": "Мясо и птица", "unit": "г", "calories": 250, "emoji": "🥩", "storage_days": 3, "image_url": "", "description": "Сытное мясо для горячих блюд."},
    {"name": "фарш", "category": "Мясо и птица", "unit": "г", "calories": 250, "emoji": "🥩", "storage_days": 2, "image_url": "", "description": "Для котлет, пасты и запеканок."},
    {"name": "тунец", "category": "Рыба и морепродукты", "unit": "шт", "calories": 130, "emoji": "🐟", "storage_days": 180, "image_url": "", "description": "Белковый продукт для салатов."},
    {"name": "лосось", "category": "Рыба и морепродукты", "unit": "г", "calories": 208, "emoji": "🐟", "storage_days": 2, "image_url": "", "description": "Рыба для запекания и салатов."},

    {"name": "рис", "category": "Крупы и паста", "unit": "г", "calories": 344, "emoji": "🍚", "storage_days": 365, "image_url": "", "description": "Базовая крупа для гарниров."},
    {"name": "гречка", "category": "Крупы и паста", "unit": "г", "calories": 313, "emoji": "🥣", "storage_days": 365, "image_url": "", "description": "Питательная крупа."},
    {"name": "овсянка", "category": "Крупы и паста", "unit": "г", "calories": 370, "emoji": "🥣", "storage_days": 180, "image_url": "", "description": "Классический завтрак."},
    {"name": "макароны", "category": "Крупы и паста", "unit": "г", "calories": 350, "emoji": "🍝", "storage_days": 365, "image_url": "", "description": "Быстрая основа для обеда."},
    {"name": "паста", "category": "Крупы и паста", "unit": "г", "calories": 350, "emoji": "🍝", "storage_days": 365, "image_url": "", "description": "Основа итальянских блюд."},

    {"name": "хлеб", "category": "Хлеб и выпечка", "unit": "шт", "calories": 250, "emoji": "🍞", "storage_days": 4, "image_url": "", "description": "Для бутербродов и тостов."},
    {"name": "батон", "category": "Хлеб и выпечка", "unit": "шт", "calories": 260, "emoji": "🥖", "storage_days": 4, "image_url": "", "description": "Для бутербродов."},

    {"name": "растительное масло", "category": "Бакалея", "unit": "л", "calories": 899, "emoji": "🛢️", "storage_days": 180, "image_url": "", "description": "Для жарки и салатов."},
    {"name": "оливковое масло", "category": "Бакалея", "unit": "л", "calories": 884, "emoji": "🫒", "storage_days": 180, "image_url": "", "description": "Для салатов и пасты."},
    {"name": "соль", "category": "Бакалея", "unit": "г", "calories": 0, "emoji": "🧂", "storage_days": 365, "image_url": "", "description": "Базовая приправа."},
    {"name": "сахар", "category": "Бакалея", "unit": "г", "calories": 387, "emoji": "🍬", "storage_days": 365, "image_url": "", "description": "Для напитков и десертов."},
    {"name": "мука", "category": "Бакалея", "unit": "г", "calories": 364, "emoji": "🌾", "storage_days": 180, "image_url": "", "description": "Для выпечки и соусов."},
    {"name": "мёд", "category": "Бакалея", "unit": "г", "calories": 304, "emoji": "🍯", "storage_days": 365, "image_url": "", "description": "Натуральный подсластитель."},

    {"name": "замороженные овощи", "category": "Заморозка", "unit": "г", "calories": 65, "emoji": "🥦", "storage_days": 180, "image_url": "", "description": "Быстрый гарнир."},
    {"name": "пельмени", "category": "Заморозка", "unit": "г", "calories": 275, "emoji": "🥟", "storage_days": 180, "image_url": "", "description": "Быстрое сытное блюдо."},
    {"name": "вода", "category": "Напитки", "unit": "л", "calories": 0, "emoji": "💧", "storage_days": 365, "image_url": "", "description": "Базовый напиток."},
    {"name": "чай", "category": "Напитки", "unit": "шт", "calories": 0, "emoji": "🍵", "storage_days": 365, "image_url": "", "description": "Горячий напиток."},
    {"name": "кофе", "category": "Напитки", "unit": "г", "calories": 2, "emoji": "☕", "storage_days": 365, "image_url": "", "description": "Напиток для бодрости."},
]


def get_catalog_categories():
    return sorted(list(set(item["category"] for item in PRODUCT_CATALOG)))


def get_catalog_products(category=None, query=""):
    query = query.lower().strip()
    result = PRODUCT_CATALOG

    if category and category != "Все категории":
        result = [item for item in result if item["category"] == category]

    if query:
        result = [
            item for item in result
            if query in item["name"].lower()
            or query in item["category"].lower()
            or query in item.get("description", "").lower()
        ]

    return sorted(result, key=lambda item: item["name"])


def get_product_from_catalog(name):
    name = name.lower().strip()

    for item in PRODUCT_CATALOG:
        if item["name"].lower().strip() == name:
            return item

    return None


def default_expiration_date_for_product(product):
    days = int(product.get("storage_days", 7))
    return date.today() + timedelta(days=days)
'''


FILES_TO_WRITE["recipes.py"] = r'''
DAYS = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]


RECIPES = [
    {
        "name": "Омлет",
        "category": "Завтрак",
        "time": "12 минут",
        "calories": 320,
        "description": "Нежный омлет на молоке.",
        "ingredients": [
            {"name": "яйца", "amount": 3, "unit": "шт", "variants": ["яйца", "яйцо"]},
            {"name": "молоко", "amount": 100, "unit": "мл", "variants": ["молоко"]},
            {"name": "сыр", "amount": 30, "unit": "г", "variants": ["сыр"], "optional": True},
        ],
        "instructions": ["Смешайте яйца и молоко.", "Вылейте на сковороду.", "Готовьте под крышкой 5–7 минут."]
    },
    {
        "name": "Яичница с помидорами",
        "category": "Завтрак",
        "time": "10 минут",
        "calories": 280,
        "description": "Быстрый завтрак из яиц и помидоров.",
        "ingredients": [
            {"name": "яйца", "amount": 2, "unit": "шт", "variants": ["яйца", "яйцо"]},
            {"name": "помидоры", "amount": 1, "unit": "шт", "variants": ["помидоры", "помидор", "томаты"]},
        ],
        "instructions": ["Нарежьте помидор.", "Добавьте яйца.", "Готовьте 3–5 минут."]
    },
    {
        "name": "Овсянка на молоке",
        "category": "Завтрак",
        "time": "10 минут",
        "calories": 350,
        "description": "Сытный завтрак с медленными углеводами.",
        "ingredients": [
            {"name": "овсянка", "amount": 60, "unit": "г", "variants": ["овсянка", "овсяные хлопья", "геркулес"]},
            {"name": "молоко", "amount": 250, "unit": "мл", "variants": ["молоко"]},
        ],
        "instructions": ["Налейте молоко в кастрюлю.", "Добавьте овсянку.", "Варите 5–7 минут."]
    },
    {
        "name": "Творог с фруктами",
        "category": "Завтрак",
        "time": "5 минут",
        "calories": 300,
        "description": "Быстрый белковый завтрак.",
        "ingredients": [
            {"name": "творог", "amount": 200, "unit": "г", "variants": ["творог"]},
            {"name": "банан", "amount": 1, "unit": "шт", "variants": ["банан", "бананы"], "optional": True},
        ],
        "instructions": ["Положите творог в тарелку.", "Добавьте фрукты."]
    },
    {
        "name": "Овощной салат",
        "category": "Салат",
        "time": "10 минут",
        "calories": 180,
        "description": "Лёгкий салат из свежих овощей.",
        "ingredients": [
            {"name": "помидоры", "amount": 2, "unit": "шт", "variants": ["помидоры", "помидор", "томаты"]},
            {"name": "огурцы", "amount": 2, "unit": "шт", "variants": ["огурцы", "огурец"]},
        ],
        "instructions": ["Нарежьте овощи.", "Добавьте соль.", "Перемешайте."]
    },
    {
        "name": "Греческий салат",
        "category": "Салат",
        "time": "15 минут",
        "calories": 260,
        "description": "Овощной салат с сыром.",
        "ingredients": [
            {"name": "помидоры", "amount": 2, "unit": "шт", "variants": ["помидоры", "помидор", "томаты"]},
            {"name": "огурцы", "amount": 2, "unit": "шт", "variants": ["огурцы", "огурец"]},
            {"name": "сыр", "amount": 80, "unit": "г", "variants": ["сыр", "фета", "брынза"]},
        ],
        "instructions": ["Нарежьте овощи.", "Добавьте сыр.", "Перемешайте."]
    },
    {
        "name": "Курица с рисом",
        "category": "Обед",
        "time": "40 минут",
        "calories": 560,
        "description": "Классический сытный обед.",
        "ingredients": [
            {"name": "курица", "amount": 250, "unit": "г", "variants": ["курица", "куриное филе", "филе курицы"]},
            {"name": "рис", "amount": 100, "unit": "г", "variants": ["рис"]},
        ],
        "instructions": ["Отварите рис.", "Курицу обжарьте или запеките.", "Подавайте вместе."]
    },
    {
        "name": "Гречка с курицей",
        "category": "Обед",
        "time": "35 минут",
        "calories": 520,
        "description": "Простой белковый обед.",
        "ingredients": [
            {"name": "курица", "amount": 250, "unit": "г", "variants": ["курица", "куриное филе"]},
            {"name": "гречка", "amount": 100, "unit": "г", "variants": ["гречка", "гречневая крупа"]},
        ],
        "instructions": ["Отварите гречку.", "Приготовьте курицу.", "Подавайте вместе."]
    },
    {
        "name": "Паста с сыром",
        "category": "Обед",
        "time": "20 минут",
        "calories": 480,
        "description": "Быстрое блюдо из макарон и сыра.",
        "ingredients": [
            {"name": "макароны", "amount": 120, "unit": "г", "variants": ["макароны", "паста", "спагетти"]},
            {"name": "сыр", "amount": 50, "unit": "г", "variants": ["сыр"]},
        ],
        "instructions": ["Отварите макароны.", "Добавьте сыр.", "Перемешайте."]
    },
    {
        "name": "Паста с курицей",
        "category": "Обед",
        "time": "30 минут",
        "calories": 760,
        "description": "Сытная паста с курицей.",
        "ingredients": [
            {"name": "макароны", "amount": 150, "unit": "г", "variants": ["макароны", "паста"]},
            {"name": "курица", "amount": 250, "unit": "г", "variants": ["курица", "куриное филе"]},
            {"name": "сыр", "amount": 40, "unit": "г", "variants": ["сыр"], "optional": True},
        ],
        "instructions": ["Отварите пасту.", "Обжарьте курицу.", "Смешайте."]
    },
    {
        "name": "Рис с курицей и овощами",
        "category": "Обед",
        "time": "35 минут",
        "calories": 690,
        "description": "Сытное блюдо на обед или ужин.",
        "ingredients": [
            {"name": "рис", "amount": 130, "unit": "г", "variants": ["рис"]},
            {"name": "курица", "amount": 250, "unit": "г", "variants": ["курица", "куриное филе"]},
            {"name": "овощи", "amount": 150, "unit": "г", "variants": ["овощи", "замороженные овощи", "морковь", "перец"]},
        ],
        "instructions": ["Отварите рис.", "Обжарьте курицу и овощи.", "Соедините."]
    },
    {
        "name": "Жареный картофель",
        "category": "Ужин",
        "time": "30 минут",
        "calories": 420,
        "description": "Простое домашнее блюдо.",
        "ingredients": [
            {"name": "картофель", "amount": 400, "unit": "г", "variants": ["картофель", "картошка"]},
        ],
        "instructions": ["Нарежьте картофель.", "Жарьте до готовности."]
    },
    {
        "name": "Картофельное пюре",
        "category": "Ужин",
        "time": "30 минут",
        "calories": 360,
        "description": "Мягкое пюре как гарнир или отдельное блюдо.",
        "ingredients": [
            {"name": "картофель", "amount": 500, "unit": "г", "variants": ["картофель", "картошка"]},
            {"name": "молоко", "amount": 100, "unit": "мл", "variants": ["молоко"], "optional": True},
        ],
        "instructions": ["Отварите картофель.", "Разомните.", "Добавьте молоко."]
    },
    {
        "name": "Куриный суп",
        "category": "Обед",
        "time": "60 минут",
        "calories": 390,
        "description": "Лёгкий суп из курицы и овощей.",
        "ingredients": [
            {"name": "курица", "amount": 300, "unit": "г", "variants": ["курица", "куриное филе"]},
            {"name": "картофель", "amount": 300, "unit": "г", "variants": ["картофель", "картошка"]},
        ],
        "instructions": ["Отварите курицу.", "Добавьте картофель.", "Варите до готовности."]
    },
    {
        "name": "Бутерброды с сыром",
        "category": "Перекус",
        "time": "5 минут",
        "calories": 300,
        "description": "Быстрый перекус.",
        "ingredients": [
            {"name": "хлеб", "amount": 2, "unit": "шт", "variants": ["хлеб", "батон"]},
            {"name": "сыр", "amount": 40, "unit": "г", "variants": ["сыр"]},
        ],
        "instructions": ["Нарежьте хлеб.", "Положите сыр."]
    },
    {
        "name": "Банан с йогуртом",
        "category": "Перекус",
        "time": "3 минуты",
        "calories": 230,
        "description": "Быстрый сладкий перекус.",
        "ingredients": [
            {"name": "банан", "amount": 1, "unit": "шт", "variants": ["банан", "бананы"]},
            {"name": "йогурт", "amount": 1, "unit": "шт", "variants": ["йогурт"]},
        ],
        "instructions": ["Нарежьте банан.", "Добавьте йогурт."]
    },
    {
        "name": "Творожный перекус",
        "category": "Перекус",
        "time": "5 минут",
        "calories": 250,
        "description": "Белковый перекус.",
        "ingredients": [
            {"name": "творог", "amount": 150, "unit": "г", "variants": ["творог"]},
        ],
        "instructions": ["Положите творог в тарелку.", "Добавьте мёд или фрукты по желанию."]
    },
]


def normalize_text(text):
    return str(text).lower().strip()


def product_name_matches(product_name, variants):
    product_name = normalize_text(product_name)

    for variant in variants:
        variant = normalize_text(variant)

        if product_name == variant:
            return True

        if variant in product_name:
            return True

        if product_name in variant:
            return True

    return False


def find_product(products, variants):
    for product in products:
        product_name = product[1]

        if product_name_matches(product_name, variants):
            return product

    return None


def to_base_unit(amount, unit):
    unit = normalize_text(unit)

    if unit in ["г", "гр", "грамм", "граммов"]:
        return amount, "г"

    if unit in ["кг", "килограмм", "килограммов"]:
        return amount * 1000, "г"

    if unit in ["мл", "миллилитр", "миллилитров"]:
        return amount, "мл"

    if unit in ["л", "литр", "литров"]:
        return amount * 1000, "мл"

    if unit in ["шт", "штука", "штук"]:
        return amount, "шт"

    return amount, unit


def has_enough(product, ingredient):
    product_quantity = product[2]
    product_unit = product[3]

    needed_amount = ingredient.get("amount", 0)
    needed_unit = ingredient.get("unit", "")

    product_base_amount, product_base_unit = to_base_unit(product_quantity, product_unit)
    needed_base_amount, needed_base_unit = to_base_unit(needed_amount, needed_unit)

    if product_base_unit != needed_base_unit:
        return True

    return product_base_amount >= needed_base_amount


def check_recipe(recipe, products):
    required_ingredients = [
        ingredient for ingredient in recipe["ingredients"]
        if not ingredient.get("optional", False)
    ]

    available = []
    missing = []

    for ingredient in required_ingredients:
        product = find_product(products, ingredient["variants"])

        if not product:
            missing.append({
                "name": ingredient["name"],
                "amount": ingredient["amount"],
                "unit": ingredient["unit"],
                "reason": "нет в наличии"
            })
        else:
            if has_enough(product, ingredient):
                available.append(ingredient)
            else:
                missing.append({
                    "name": ingredient["name"],
                    "amount": ingredient["amount"],
                    "unit": ingredient["unit"],
                    "reason": f"мало, есть {product[2]} {product[3]}"
                })

    total = len(required_ingredients)
    available_count = len(available)

    score = 0
    if total > 0:
        score = round((available_count / total) * 100)

    return {
        "recipe": recipe,
        "available": available,
        "missing": missing,
        "score": score,
        "can_make": len(missing) == 0
    }


def get_recipe_matches(products):
    results = []

    for recipe in RECIPES:
        results.append(check_recipe(recipe, products))

    results.sort(
        key=lambda item: (
            item["can_make"],
            item["score"],
            item["recipe"]["calories"]
        ),
        reverse=True
    )

    return results


def get_all_recipes():
    return RECIPES
'''


FILES_TO_WRITE["dish_catalog.py"] = r'''
DISH_METADATA = {
    "Омлет": {
        "emoji": "🥚",
        "image_url": "",
        "origin": "Европейская кухня",
        "where_popular": "Франция, Европа, домашняя кухня по всему миру.",
        "history": "Омлет часто связывают с французской кухней, хотя блюда из взбитых яиц готовили в разных культурах задолго до современного рецепта.",
        "interesting_fact": "Классический французский омлет готовят нежным, без сильной корочки."
    },
    "Курица с рисом": {
        "emoji": "🍗",
        "image_url": "",
        "origin": "Домашняя кухня",
        "where_popular": "Во многих странах как базовое сытное блюдо.",
        "history": "Сочетание риса и курицы встречается во множестве кухонь: от плова до азиатских рисовых тарелок.",
        "interesting_fact": "Это одно из самых популярных блюд для meal prep — заготовки еды на несколько дней."
    },
    "Греческий салат": {
        "emoji": "🥗",
        "image_url": "",
        "origin": "Греция",
        "where_popular": "Греция, Средиземноморье, рестораны по всему миру.",
        "history": "Греческий салат, или хориатики, традиционно готовят из помидоров, огурцов, сыра фета, оливок и масла.",
        "interesting_fact": "В классическом варианте листья салата обычно не добавляют."
    },
    "Паста с курицей": {
        "emoji": "🍝",
        "image_url": "",
        "origin": "Итальянская и домашняя кухня",
        "where_popular": "Европа, США, домашняя кухня.",
        "history": "Паста с курицей — адаптация итальянской пасты под более сытный домашний формат.",
        "interesting_fact": "Можно сделать сливочную, томатную или сырную версию."
    },
    "Овсянка на молоке": {
        "emoji": "🥣",
        "image_url": "",
        "origin": "Северная Европа",
        "where_popular": "Великобритания, Скандинавия, Россия, фитнес-питание.",
        "history": "Овсяная каша стала популярной благодаря доступности овса и высокой питательности.",
        "interesting_fact": "Овсянка содержит медленные углеводы и хорошо насыщает."
    },
    "Овощной салат": {
        "emoji": "🥗",
        "image_url": "",
        "origin": "Домашняя кухня",
        "where_popular": "Практически по всему миру.",
        "history": "Свежие овощные салаты появились как простое сезонное блюдо из доступных овощей.",
        "interesting_fact": "Овощной салат легко адаптировать под продукты в холодильнике."
    },
}


def get_dish_metadata(dish_name):
    default = {
        "emoji": "🍽️",
        "image_url": "",
        "origin": "Домашняя кухня",
        "where_popular": "Популярно в домашнем питании.",
        "history": "Это блюдо можно адаптировать под продукты, которые есть в холодильнике.",
        "interesting_fact": "Состав блюда можно менять под вкус и цели питания."
    }

    return DISH_METADATA.get(dish_name, default)


def enrich_recipe(recipe):
    metadata = get_dish_metadata(recipe["name"])
    enriched = dict(recipe)
    enriched.update(metadata)
    return enriched


def get_enriched_recipes(recipes):
    return [enrich_recipe(recipe) for recipe in recipes]


def search_dish_metadata(query=""):
    query = query.lower().strip()
    items = []

    for dish_name, metadata in DISH_METADATA.items():
        row = {"name": dish_name, **metadata}

        if not query:
            items.append(row)
        else:
            haystack = " ".join([
                dish_name,
                metadata.get("origin", ""),
                metadata.get("where_popular", ""),
                metadata.get("history", ""),
                metadata.get("interesting_fact", "")
            ]).lower()

            if query in haystack:
                items.append(row)

    return sorted(items, key=lambda item: item["name"])
'''


FILES_TO_WRITE["menu_engine.py"] = r'''
import re
from collections import defaultdict

from settings import PEOPLE, PERSON_GENITIVE, PERSON_EMOJI

from database import (
    get_user_profile,
    get_favorite_dishes,
    get_products,
    reduce_product_quantity,
    add_cooking_history,
    create_accepted_week_menu,
    add_accepted_week_menu_item,
    add_product_transaction
)

from recipes import DAYS, get_recipe_matches, find_product, to_base_unit


def get_person_emoji(person):
    return PERSON_EMOJI.get(person, "👤")


def get_person_genitive(person):
    return PERSON_GENITIVE.get(person, person)


def split_text_items(text):
    if not text:
        return []
    parts = re.split(r"[,;\n]+", str(text).lower())
    return [part.strip() for part in parts if part.strip()]


def recipe_contains_terms(recipe, terms):
    if not terms:
        return False

    haystack = recipe["name"].lower() + " " + recipe.get("description", "").lower()

    for ingredient in recipe.get("ingredients", []):
        haystack += " " + ingredient.get("name", "").lower()
        haystack += " " + " ".join(ingredient.get("variants", [])).lower()

    for term in terms:
        if term and term in haystack:
            return True

    return False


def get_favorites_map(person):
    favorites = get_favorite_dishes(person)
    result = {}

    for row in favorites:
        favorite_id, row_person, dish_name, source, rating, notes, created_at = row
        result[dish_name.lower().strip()] = {
            "rating": int(rating),
            "notes": notes,
            "source": source
        }

    return result


def meal_slots_for_profile(meals_per_day):
    meals_per_day = int(meals_per_day)

    if meals_per_day <= 1:
        return ["Основной приём пищи"]
    if meals_per_day == 2:
        return ["Завтрак", "Ужин"]
    if meals_per_day == 3:
        return ["Завтрак", "Обед", "Ужин"]
    if meals_per_day == 4:
        return ["Завтрак", "Обед", "Ужин", "Перекус"]
    return ["Завтрак", "Обед", "Ужин", "Перекус", "Дополнительно"]


def preferred_categories_for_slot(slot):
    if slot == "Завтрак":
        return ["Завтрак"]
    if slot == "Обед":
        return ["Обед", "Салат"]
    if slot == "Ужин":
        return ["Ужин", "Обед", "Салат"]
    if slot in ["Перекус", "Дополнительно"]:
        return ["Перекус", "Завтрак"]
    return ["Обед", "Ужин", "Салат", "Завтрак", "Перекус"]


def score_recipe_for_person(item, slot, profile, favorites_map, used_counts, daily_calories):
    recipe = item["recipe"]
    person_name, target_calories, goal, meals_per_day, protein_focus, preferences, dislikes, allergies, updated_at = profile

    score = item["score"]

    if item["can_make"]:
        score += 20

    if recipe["category"] in preferred_categories_for_slot(slot):
        score += 30

    recipe_key = recipe["name"].lower().strip()

    if recipe_key in favorites_map:
        rating = favorites_map[recipe_key]["rating"]
        score += 40 + rating * 10

    if recipe_contains_terms(recipe, split_text_items(preferences)):
        score += 12

    if recipe_contains_terms(recipe, split_text_items(dislikes)):
        score -= 90

    if recipe_contains_terms(recipe, split_text_items(allergies)):
        score -= 250

    if protein_focus:
        if recipe_contains_terms(recipe, ["курица", "творог", "яйца", "тунец", "сыр", "индейка", "говядина"]):
            score += 12

    remaining_target = target_calories - daily_calories

    if recipe["calories"] <= remaining_target:
        score += 10
    else:
        score -= 8

    score -= used_counts[recipe["name"]] * 14

    return score


def build_personal_week_menu(person, products):
    profile = get_user_profile(person)

    if not profile:
        return None

    person_name, target_calories, goal, meals_per_day, protein_focus, preferences, dislikes, allergies, updated_at = profile
    matches = get_recipe_matches(products)
    favorites_map = get_favorites_map(person)
    used_counts = defaultdict(int)

    week = []
    slots = meal_slots_for_profile(int(meals_per_day))

    for day in DAYS:
        meals = []
        daily_calories = 0

        for slot in slots:
            best_item = None
            best_score = -999999

            for item in matches:
                score = score_recipe_for_person(
                    item=item,
                    slot=slot,
                    profile=profile,
                    favorites_map=favorites_map,
                    used_counts=used_counts,
                    daily_calories=daily_calories
                )

                if score > best_score:
                    best_score = score
                    best_item = item

            if best_item:
                recipe = best_item["recipe"]
                recipe_key = recipe["name"].lower().strip()
                favorite_info = favorites_map.get(recipe_key)

                meals.append({
                    "slot": slot,
                    "recipe": recipe,
                    "calories": recipe["calories"],
                    "can_make": best_item["can_make"],
                    "score": best_item["score"],
                    "missing": best_item["missing"],
                    "is_favorite": recipe_key in favorites_map,
                    "favorite_rating": favorite_info["rating"] if favorite_info else None,
                    "favorite_notes": favorite_info["notes"] if favorite_info else ""
                })

                daily_calories += recipe["calories"]
                used_counts[recipe["name"]] += 1

        diff = daily_calories - target_calories
        diff_percent = abs(diff) / target_calories if target_calories else 0

        if diff_percent <= 0.12:
            status = "✅ близко к цели"
            status_color = "green"
        elif diff < 0:
            status = "⚠️ ниже цели"
            status_color = "yellow"
        else:
            status = "🔥 выше цели"
            status_color = "red"

        week.append({
            "person": person,
            "day": day,
            "target_calories": target_calories,
            "meals": meals,
            "calories": daily_calories,
            "diff": diff,
            "status": status,
            "status_color": status_color
        })

    avg_calories = round(sum(day["calories"] for day in week) / len(week))
    avg_diff = avg_calories - target_calories
    favorites_used = sum(1 for day in week for meal in day["meals"] if meal["is_favorite"])

    return {
        "person": person,
        "profile": profile,
        "week": week,
        "avg_calories": avg_calories,
        "avg_diff": avg_diff,
        "favorites_used": favorites_used
    }


def build_all_personal_week_menus(products):
    return {person: build_personal_week_menu(person, products) for person in PEOPLE}


def build_shopping_list_for_menu(menu_data, products):
    if not menu_data:
        return []

    inventory = {}

    for product in products:
        product_id, name, quantity, unit, calories, category, exp_date = product
        base_amount, base_unit = to_base_unit(quantity, unit)
        inventory[product_id] = {"product": product, "amount": base_amount, "unit": base_unit}

    shopping = {}

    for day in menu_data["week"]:
        for meal in day["meals"]:
            recipe = meal["recipe"]

            for ingredient in recipe.get("ingredients", []):
                if ingredient.get("optional", False):
                    continue

                needed_amount, needed_unit = to_base_unit(ingredient["amount"], ingredient["unit"])
                product = find_product(products, ingredient["variants"])
                key = f"{ingredient['name']}|{needed_unit}"

                if not product:
                    shopping.setdefault(key, {"name": ingredient["name"], "amount": 0, "unit": needed_unit, "recipes": []})
                    shopping[key]["amount"] += needed_amount
                    if recipe["name"] not in shopping[key]["recipes"]:
                        shopping[key]["recipes"].append(recipe["name"])
                    continue

                product_id = product[0]

                if product_id not in inventory:
                    continue

                if inventory[product_id]["unit"] != needed_unit:
                    continue

                if inventory[product_id]["amount"] >= needed_amount:
                    inventory[product_id]["amount"] -= needed_amount
                else:
                    shortage = needed_amount - inventory[product_id]["amount"]
                    inventory[product_id]["amount"] = 0

                    shopping.setdefault(key, {"name": ingredient["name"], "amount": 0, "unit": needed_unit, "recipes": []})
                    shopping[key]["amount"] += shortage
                    if recipe["name"] not in shopping[key]["recipes"]:
                        shopping[key]["recipes"].append(recipe["name"])

    return list(shopping.values())


def combine_shopping_lists(*shopping_lists):
    combined = {}

    for shopping_list in shopping_lists:
        for item in shopping_list:
            key = f"{item['name']}|{item['unit']}"
            combined.setdefault(key, {"name": item["name"], "amount": 0, "unit": item["unit"], "recipes": []})
            combined[key]["amount"] += item["amount"]

            for recipe in item.get("recipes", []):
                if recipe not in combined[key]["recipes"]:
                    combined[key]["recipes"].append(recipe)

    return list(combined.values())


def convert_base_amount_to_product_unit(base_amount, base_unit, product_unit):
    _, product_base_unit = to_base_unit(1, product_unit)

    if base_unit != product_base_unit:
        return None

    product_unit = product_unit.lower().strip()

    if product_unit == "кг":
        return base_amount / 1000
    if product_unit == "л":
        return base_amount / 1000
    return base_amount


def spend_ingredient_for_menu(ingredient, recipe_name, person, day, meal_slot):
    current_products = get_products()
    product = find_product(current_products, ingredient["variants"])

    needed_base_amount, needed_base_unit = to_base_unit(ingredient["amount"], ingredient["unit"])

    if not product:
        return {
            "spent": False,
            "missing": True,
            "product_name": ingredient["name"],
            "amount": needed_base_amount,
            "unit": needed_base_unit,
            "reason": "нет в наличии"
        }

    product_id, product_name, product_quantity, product_unit, calories, category, exp_date = product
    product_base_amount, product_base_unit = to_base_unit(product_quantity, product_unit)

    if product_base_unit != needed_base_unit:
        return {
            "spent": False,
            "missing": True,
            "product_name": ingredient["name"],
            "amount": needed_base_amount,
            "unit": needed_base_unit,
            "reason": f"несовместимые единицы: нужно {needed_base_unit}, есть {product_unit}"
        }

    amount_in_product_unit = convert_base_amount_to_product_unit(needed_base_amount, needed_base_unit, product_unit)

    if product_base_amount >= needed_base_amount:
        reduce_product_quantity(product_id, amount_in_product_unit)

        add_product_transaction(
            product_id=product_id,
            product_name=product_name,
            change_amount=-amount_in_product_unit,
            unit=product_unit,
            action="spend",
            reason="accepted_week_menu",
            dish_name=recipe_name,
            person=person,
            day=day,
            meal_slot=meal_slot
        )

        return {
            "spent": True,
            "missing": False,
            "product_name": product_name,
            "amount": amount_in_product_unit,
            "unit": product_unit,
            "reason": ""
        }

    available_in_product_unit = product_quantity
    shortage_base = needed_base_amount - product_base_amount

    if available_in_product_unit > 0:
        reduce_product_quantity(product_id, available_in_product_unit)

        add_product_transaction(
            product_id=product_id,
            product_name=product_name,
            change_amount=-available_in_product_unit,
            unit=product_unit,
            action="spend_partial",
            reason="accepted_week_menu",
            dish_name=recipe_name,
            person=person,
            day=day,
            meal_slot=meal_slot
        )

    return {
        "spent": True,
        "missing": True,
        "product_name": product_name,
        "amount": shortage_base,
        "unit": needed_base_unit,
        "reason": "частично списано, не хватило"
    }


def accept_week_menus(menu_mishka, menu_medinka, title="Принятое меню на неделю", notes=""):
    menu_id = create_accepted_week_menu(title=title, notes=notes)

    report = {
        "menu_id": menu_id,
        "spent": [],
        "missing": [],
        "items_saved": 0
    }

    all_menus = []
    if menu_mishka:
        all_menus.append(menu_mishka)
    if menu_medinka:
        all_menus.append(menu_medinka)

    for menu_data in all_menus:
        person = menu_data["person"]

        for day in menu_data["week"]:
            day_name = day["day"]

            for meal in day["meals"]:
                recipe = meal["recipe"]
                meal_slot = meal["slot"]

                add_accepted_week_menu_item(
                    menu_id=menu_id,
                    person=person,
                    day=day_name,
                    meal_slot=meal_slot,
                    dish_name=recipe["name"],
                    calories=recipe["calories"],
                    is_favorite=meal.get("is_favorite", False)
                )

                report["items_saved"] += 1
                spent_strings = []

                for ingredient in recipe.get("ingredients", []):
                    if ingredient.get("optional", False):
                        continue

                    result = spend_ingredient_for_menu(
                        ingredient=ingredient,
                        recipe_name=recipe["name"],
                        person=person,
                        day=day_name,
                        meal_slot=meal_slot
                    )

                    if result["spent"] and not result["missing"]:
                        report["spent"].append({
                            "person": person,
                            "day": day_name,
                            "meal_slot": meal_slot,
                            "dish_name": recipe["name"],
                            "product_name": result["product_name"],
                            "amount": result["amount"],
                            "unit": result["unit"]
                        })

                        spent_strings.append(f"{result['product_name']}: {round(result['amount'], 2)} {result['unit']}")

                    if result["missing"]:
                        report["missing"].append({
                            "person": person,
                            "day": day_name,
                            "meal_slot": meal_slot,
                            "dish_name": recipe["name"],
                            "product_name": result["product_name"],
                            "amount": result["amount"],
                            "unit": result["unit"],
                            "reason": result["reason"]
                        })

                ingredients_used = ", ".join(spent_strings) if spent_strings else "Ингредиенты не списаны"

                add_cooking_history(
                    dish_name=f"{recipe['name']} — {person}, {day_name}, {meal_slot}",
                    ingredients_used=ingredients_used,
                    calories=recipe["calories"]
                )

    return report
'''


FILES_TO_WRITE["demo_data.py"] = r'''
from datetime import date, timedelta

from database import (
    add_or_update_product,
    clear_products,
    clear_all_data,
    add_favorite_dish,
    update_user_profile
)


def get_demo_products():
    today = date.today()

    return [
        {"name": "яйца", "quantity": 16, "unit": "шт", "calories": 157, "category": "Яйца", "expiration": today + timedelta(days=12)},
        {"name": "молоко", "quantity": 2, "unit": "л", "calories": 60, "category": "Молочные продукты", "expiration": today + timedelta(days=2)},
        {"name": "творог", "quantity": 900, "unit": "г", "calories": 120, "category": "Молочные продукты", "expiration": today + timedelta(days=3)},
        {"name": "сыр", "quantity": 400, "unit": "г", "calories": 350, "category": "Молочные продукты", "expiration": today + timedelta(days=20)},
        {"name": "курица", "quantity": 2500, "unit": "г", "calories": 165, "category": "Мясо и птица", "expiration": today + timedelta(days=3)},
        {"name": "рис", "quantity": 1500, "unit": "г", "calories": 344, "category": "Крупы и паста", "expiration": today + timedelta(days=300)},
        {"name": "гречка", "quantity": 1200, "unit": "г", "calories": 313, "category": "Крупы и паста", "expiration": today + timedelta(days=250)},
        {"name": "макароны", "quantity": 1300, "unit": "г", "calories": 350, "category": "Крупы и паста", "expiration": today + timedelta(days=240)},
        {"name": "овсянка", "quantity": 800, "unit": "г", "calories": 370, "category": "Крупы и паста", "expiration": today + timedelta(days=180)},
        {"name": "картофель", "quantity": 4, "unit": "кг", "calories": 77, "category": "Овощи", "expiration": today + timedelta(days=14)},
        {"name": "помидоры", "quantity": 10, "unit": "шт", "calories": 18, "category": "Овощи", "expiration": today + timedelta(days=4)},
        {"name": "огурцы", "quantity": 8, "unit": "шт", "calories": 15, "category": "Овощи", "expiration": today + timedelta(days=3)},
        {"name": "морковь", "quantity": 6, "unit": "шт", "calories": 41, "category": "Овощи", "expiration": today + timedelta(days=18)},
        {"name": "банан", "quantity": 6, "unit": "шт", "calories": 89, "category": "Фрукты", "expiration": today + timedelta(days=2)},
        {"name": "яблоко", "quantity": 8, "unit": "шт", "calories": 52, "category": "Фрукты", "expiration": today + timedelta(days=10)},
        {"name": "хлеб", "quantity": 2, "unit": "шт", "calories": 250, "category": "Хлеб и выпечка", "expiration": today + timedelta(days=2)},
        {"name": "йогурт", "quantity": 4, "unit": "шт", "calories": 90, "category": "Молочные продукты", "expiration": today + timedelta(days=5)},
        {"name": "замороженные овощи", "quantity": 1000, "unit": "г", "calories": 65, "category": "Заморозка", "expiration": today + timedelta(days=120)},
    ]


def load_demo_products(reset=False):
    if reset:
        clear_products()

    products = get_demo_products()

    for item in products:
        add_or_update_product(
            name=item["name"],
            quantity=item["quantity"],
            unit=item["unit"],
            calories_per_100g=item["calories"],
            category=item["category"],
            expiration_date=str(item["expiration"])
        )

    return len(products)


def load_demo_profiles_and_favorites():
    update_user_profile(
        person="Мишка",
        target_calories=2300,
        goal="Поддержание веса",
        meals_per_day=4,
        protein_focus=True,
        preferences="курица, рис, творог, мясо, паста",
        dislikes="рыба",
        allergies=""
    )

    update_user_profile(
        person="Мединка",
        target_calories=1800,
        goal="Правильное питание",
        meals_per_day=4,
        protein_focus=True,
        preferences="салаты, овощи, творог, курица, овсянка",
        dislikes="жирное",
        allergies=""
    )

    favorites = [
        ("Мишка", "Курица с рисом", "recipe", 5, "Любимое сытное блюдо."),
        ("Мишка", "Омлет", "recipe", 4, "Хорошо на завтрак."),
        ("Мишка", "Паста с сыром", "recipe", 5, "Быстро и вкусно."),
        ("Мишка", "Жареный картофель", "recipe", 5, "Домашняя классика."),
        ("Мишка", "Паста с курицей", "recipe", 5, "Очень сытно."),
        ("Мединка", "Овощной салат", "recipe", 5, "Лёгкий вариант."),
        ("Мединка", "Творог с фруктами", "recipe", 5, "Любимый завтрак."),
        ("Мединка", "Овсянка на молоке", "recipe", 4, "Хорошо утром."),
        ("Мединка", "Греческий салат", "recipe", 5, "Любит с сыром."),
        ("Мединка", "Банан с йогуртом", "recipe", 4, "Быстрый перекус."),
    ]

    for person, dish_name, source, rating, notes in favorites:
        add_favorite_dish(person, dish_name, source, rating, notes)


def reset_everything_and_load_demo():
    clear_all_data()
    count = load_demo_products(reset=False)
    load_demo_profiles_and_favorites()
    return count
'''


FILES_TO_WRITE["app.py"] = r'''
import re
from datetime import datetime, date

import pandas as pd
import streamlit as st

from settings import APP_NAME, APP_VERSION, DEVELOPER, PEOPLE, NUTRITION_GOALS, APP_TAGLINE
from demo_data import load_demo_products, reset_everything_and_load_demo
from database import (
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
    get_accepted_week_menu_items
)
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


st.set_page_config(
    page_title=APP_NAME,
    page_icon="🥦",
    layout="wide"
)

init_db()


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


def render_page_intro(title, text, icon="✨"):
    st.markdown(f"""
    <div class="soft-card">
        <h3>{icon} {title}</h3>
        <p>{text}</p>
    </div>
    """, unsafe_allow_html=True)


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

    st.download_button(
        "📥 Скачать список покупок",
        data="\n".join(text_lines),
        file_name="shopping_list_medinki.txt",
        mime="text/plain"
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


st.sidebar.markdown(f"## 🥦 {APP_NAME}")
st.sidebar.markdown(f"<div class='sidebar-text'>{APP_TAGLINE}</div>", unsafe_allow_html=True)
st.sidebar.divider()

if st.sidebar.button("🧪 Быстро заполнить демо-данными"):
    count = reset_everything_and_load_demo()
    st.sidebar.success(f"Загружено демо-продуктов: {count}")
    st.rerun()

st.sidebar.caption(f"{APP_VERSION} · {DEVELOPER}")

nav_labels = {
    "Главная": "🏠 Главная",
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

page = st.sidebar.radio("Навигация", list(nav_labels.keys()), format_func=lambda item: nav_labels[item])
products = get_products()

st.markdown(f"<div class='app-title'>🥦 {APP_NAME}</div>", unsafe_allow_html=True)
st.markdown("<div class='app-subtitle'>Холодильник, меню, рецепты, покупки и списание продуктов.</div>", unsafe_allow_html=True)


if page == "Главная":
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

            confirm = st.checkbox("Я понимаю, что продукты будут списаны из холодильника")

            notes = st.text_area("Заметка к меню", placeholder="Например: меню на следующую неделю")

            if st.button("✅ Принять меню на неделю и списать продукты", disabled=not confirm):
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
'''


def create_backup():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = PROJECT_DIR / f"backup_before_v06_{timestamp}"
    backup_dir.mkdir(exist_ok=True)

    file_names = list(FILES_TO_WRITE.keys())

    for file_name in file_names:
        src = PROJECT_DIR / file_name
        if src.exists():
            shutil.copy2(src, backup_dir / file_name)

    return backup_dir


def write_files():
    for file_name, content in FILES_TO_WRITE.items():
        path = PROJECT_DIR / file_name
        cleaned = textwrap.dedent(content).strip() + "\n"
        path.write_text(cleaned, encoding="utf-8")
        print(f"✅ Записан файл: {file_name}")


def compile_files():
    print("\nПроверяю синтаксис файлов...")

    ok = True

    for file_name in FILES_TO_WRITE.keys():
        path = PROJECT_DIR / file_name

        try:
            py_compile.compile(str(path), doraise=True)
            print(f"✅ OK: {file_name}")
        except Exception as e:
            ok = False
            print(f"❌ Ошибка в {file_name}:")
            print(e)

    return ok


def main():
    print("====================================")
    print(" Обновление проекта до v0.6")
    print(" Умный холодильник Мединки")
    print("====================================\n")

    backup_dir = create_backup()
    print(f"📦 Резервная копия создана: {backup_dir.name}\n")

    write_files()

    ok = compile_files()

    print("\n====================================")

    if ok:
        print("✅ Обновление до v0.6 завершено успешно.")
        print("")
        print("Теперь запусти приложение:")
        print("python -m streamlit run app.py")
        print("")
        print("Если захочешь откатиться, файлы лежат в папке:")
        print(backup_dir)
    else:
        print("⚠️ Обновление записало файлы, но есть ошибки синтаксиса.")
        print("Пришли текст ошибки, я поправлю.")
        print("")
        print("Резервная копия лежит в папке:")
        print(backup_dir)


if __name__ == "__main__":
        main()