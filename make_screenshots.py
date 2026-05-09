from pathlib import Path

from playwright.sync_api import sync_playwright

from database import init_db, add_favorite_dish, add_cooking_history
from demo_data import reset_everything_and_load_demo


APP_URL = "http://localhost:8501"
OUT_DIR = Path("screenshots_v04")

PREPARE_DEMO_DATA = True
WAIT_MS = 1400


NAV_LABELS = {
    "Главная": ["🏠 Главная", "Главная"],
    "Мой холодильник": ["🧊 Мой холодильник", "Мой холодильник"],
    "Добавить продукты": ["➕ Добавить продукты", "Добавить продукты"],
    "Рецепты": ["🍳 Рецепты", "Рецепты"],
    "Меню на неделю": ["🗓️ Меню на неделю", "Меню на неделю"],
    "Список покупок": ["🛒 Список покупок", "Список покупок"],
    "Питание и цели": ["🎯 Питание и цели", "Питание и цели"],
    "Любимые блюда": ["❤️ Любимые блюда", "Любимые блюда"],
    "Демо-режим": ["🧪 Демо-режим", "Демо-режим"],
    "История": ["📜 История", "История"],
}


def prepare_demo_data():
    """
    Готовим данные для красивых скриншотов:
    - очищаем продукты и историю;
    - загружаем демо-продукты;
    - добавляем любимые блюда;
    - добавляем пару записей истории.
    """
    init_db()
    reset_everything_and_load_demo()

    favorite_items = [
        ("Мишка", "Курица с рисом", "recipe", 5, "Любимое сытное блюдо."),
        ("Мишка", "Омлет", "recipe", 4, "Хорошо на завтрак."),
        ("Мишка", "Паста с сыром", "recipe", 5, "Быстро и вкусно."),
        ("Мишка", "Жареный картофель", "recipe", 5, "Домашняя классика."),

        ("Мединка", "Овощной салат", "recipe", 5, "Лёгкий вариант на ужин."),
        ("Мединка", "Творог с фруктами", "recipe", 5, "Любимый завтрак."),
        ("Мединка", "Овсянка на молоке", "recipe", 4, "Хорошо утром."),
        ("Мединка", "Греческий салат", "recipe", 5, "Любит с сыром."),
    ]

    for person, dish_name, source, rating, notes in favorite_items:
        add_favorite_dish(
            person=person,
            dish_name=dish_name,
            source=source,
            rating=rating,
            notes=notes
        )

    add_cooking_history(
        dish_name="Омлет",
        ingredients_used="яйца: 3 шт, молоко: 100 мл",
        calories=320
    )

    add_cooking_history(
        dish_name="Курица с рисом",
        ingredients_used="курица: 250 г, рис: 100 г",
        calories=560
    )


def wait_app(page):
    page.wait_for_timeout(WAIT_MS)


def go_nav(page, page_name):
    sidebar = page.locator('[data-testid="stSidebar"]')

    labels = NAV_LABELS[page_name]

    for label in labels:
        try:
            sidebar.get_by_text(label, exact=True).click(timeout=3000)
            wait_app(page)
            return
        except Exception:
            pass

    for label in labels:
        try:
            sidebar.get_by_text(label, exact=False).click(timeout=3000)
            wait_app(page)
            return
        except Exception:
            pass

    raise RuntimeError(f"Не смог открыть раздел: {page_name}")


def click_tab(page, tab_name):
    try:
        page.get_by_role("tab", name=tab_name).click(timeout=3000)
        wait_app(page)
        return
    except Exception:
        pass

    try:
        page.get_by_text(tab_name, exact=True).click(timeout=3000)
        wait_app(page)
        return
    except Exception:
        pass

    raise RuntimeError(f"Не смог открыть вкладку: {tab_name}")


def save_screenshot(page, filename):
    OUT_DIR.mkdir(exist_ok=True)

    path = OUT_DIR / f"{filename}.png"

    page.screenshot(
        path=str(path),
        full_page=True
    )

    print(f"Скриншот сохранён: {path}")


def main():
    if PREPARE_DEMO_DATA:
        print("Готовлю демо-данные...")
        prepare_demo_data()
        print("Демо-данные готовы.")

    OUT_DIR.mkdir(exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True
        )

        page = browser.new_page(
            viewport={
                "width": 1440,
                "height": 1100
            },
            device_scale_factor=1
        )

        print(f"Открываю приложение: {APP_URL}")

        page.goto(APP_URL, wait_until="domcontentloaded", timeout=30000)
        wait_app(page)

        # 1. Главная
        go_nav(page, "Главная")
        save_screenshot(page, "01_glavnaya")

        # 2-4. Мой холодильник
        go_nav(page, "Мой холодильник")
        click_tab(page, "Таблица")
        save_screenshot(page, "02_holodilnik_tablica")

        click_tab(page, "Карточки")
        save_screenshot(page, "03_holodilnik_kartochki")

        click_tab(page, "Редактировать")
        save_screenshot(page, "04_holodilnik_redaktirovanie")

        # 5-6. Добавить продукты
        go_nav(page, "Добавить продукты")
        click_tab(page, "Один продукт")
        save_screenshot(page, "05_dobavit_odin")

        click_tab(page, "Списком")
        save_screenshot(page, "06_dobavit_spiskom")

        # 7. Рецепты
        go_nav(page, "Рецепты")
        save_screenshot(page, "07_recepty")

        # 8. Меню на неделю
        go_nav(page, "Меню на неделю")
        save_screenshot(page, "08_menu_na_nedelyu")

        # 9. Список покупок
        go_nav(page, "Список покупок")
        save_screenshot(page, "09_spisok_pokupok")

        # 10. Питание и цели
        go_nav(page, "Питание и цели")
        save_screenshot(page, "10_pitanie_i_celi")

        # 11. Любимые блюда
        go_nav(page, "Любимые блюда")
        save_screenshot(page, "11_lyubimye_blyuda_mishka")

        try:
            click_tab(page, "🌸 Мединка")
            save_screenshot(page, "11_lyubimye_blyuda_medinka")
        except Exception:
            print("Не удалось отдельно открыть вкладку Мединки, общий скриншот уже сохранён.")

        # 12. Демо-режим
        go_nav(page, "Демо-режим")
        save_screenshot(page, "12_demo_rezhim")

        # 13. История
        go_nav(page, "История")
        save_screenshot(page, "13_istoriya")

        browser.close()

    print("")
    print("Готово.")
    print(f"Все скриншоты лежат в папке: {OUT_DIR.resolve()}")


if __name__ == "__main__":
    main()