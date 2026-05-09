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
