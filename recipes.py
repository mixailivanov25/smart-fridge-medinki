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
