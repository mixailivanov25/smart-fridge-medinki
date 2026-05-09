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
