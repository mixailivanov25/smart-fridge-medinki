from pathlib import Path
from datetime import datetime
import shutil
import py_compile


PROJECT_DIR = Path(__file__).resolve().parent

APP_FILE = PROJECT_DIR / "app.py"
DB_FILE = PROJECT_DIR / "database.py"
SETTINGS_FILE = PROJECT_DIR / "settings.py"


def backup_files():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = PROJECT_DIR / f"backup_before_v08_{timestamp}"
    backup_dir.mkdir(exist_ok=True)

    for file_path in [
        APP_FILE,
        DB_FILE,
        SETTINGS_FILE,
        PROJECT_DIR / "recipes.py",
        PROJECT_DIR / "demo_data.py",
        PROJECT_DIR / "product_catalog.py",
        PROJECT_DIR / "dish_catalog.py",
        PROJECT_DIR / "menu_engine.py",
    ]:
        if file_path.exists():
            shutil.copy2(file_path, backup_dir / file_path.name)

    print(f"📦 Резервная копия создана: {backup_dir}")
    return backup_dir


def update_settings():
    text = SETTINGS_FILE.read_text(encoding="utf-8")

    text = text.replace('APP_VERSION = "v0.7"', 'APP_VERSION = "v0.8"')
    text = text.replace('APP_VERSION = "v0.6"', 'APP_VERSION = "v0.8"')

    SETTINGS_FILE.write_text(text, encoding="utf-8")
    print("✅ settings.py обновлён до v0.8")


def patch_database():
    text = DB_FILE.read_text(encoding="utf-8")

    if "def ensure_v08_tables(" in text:
        print("ℹ️ database.py уже содержит функции v0.8")
        return

    addition = r'''

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
'''

    text = text.rstrip() + "\n" + addition + "\n"
    DB_FILE.write_text(text, encoding="utf-8")

    print("✅ database.py обновлён функциями v0.8")


def patch_app_imports(text):
    # Добавляем функции БД в большой импорт from database import (...)
    if "ensure_v08_tables" not in text:
        old = '''    get_product_transactions,
    get_accepted_week_menus,
    get_accepted_week_menu_items'''

        new = '''    get_product_transactions,
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
    add_shopping_item_to_fridge'''

        if old in text:
            text = text.replace(old, new)
            print("✅ app.py: добавлены импорты database v0.8")
        else:
            print("⚠️ app.py: не нашёл стандартный блок импорта database. Импорты v0.8 могли не добавиться.")

    # После init_db() добавляем ensure_v08_tables()
    if "ensure_v08_tables()" not in text:
        text = text.replace(
            "init_db()",
            "init_db()\nensure_v08_tables()",
            1
        )
        print("✅ app.py: добавлен вызов ensure_v08_tables()")

    return text


def patch_app_nav(text):
    if '"Дневник питания": "📔 Дневник питания"' in text:
        print("ℹ️ app.py: навигация v0.8 уже добавлена")
        return text

    old = '''    "Сегодня": "📅 Сегодня",'''

    new = '''    "Сегодня": "📅 Сегодня",
    "Дневник питания": "📔 Дневник питания",
    "Умные покупки": "🛒 Умные покупки",'''

    if old in text:
        text = text.replace(old, new)
        print("✅ app.py: добавлены пункты Дневник питания и Умные покупки")
    else:
        print("⚠️ app.py: не нашёл пункт Сегодня в навигации. Добавление пунктов пропущено.")

    return text


def build_diary_page_block():
    return r'''

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
'''


def build_smart_shopping_page_block():
    return r'''

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
'''


def patch_app_pages(text):
    if 'elif page == "Дневник питания":' in text:
        print("ℹ️ app.py: страницы v0.8 уже добавлены")
        return text

    marker = 'elif page == "Мой холодильник":'

    if marker not in text:
        print("⚠️ app.py: не нашёл место вставки перед Мой холодильник.")
        return text

    insertion = build_diary_page_block() + "\n" + build_smart_shopping_page_block() + "\n\n"
    text = text.replace(marker, insertion + marker)

    print("✅ app.py: добавлены страницы Дневник питания и Умные покупки")
    return text


def patch_app():
    text = APP_FILE.read_text(encoding="utf-8")

    text = patch_app_imports(text)
    text = patch_app_nav(text)
    text = patch_app_pages(text)

    APP_FILE.write_text(text, encoding="utf-8")
    print("✅ app.py обновлён до v0.8")


def compile_files():
    print("\nПроверяю синтаксис...")

    files = [
        "app.py",
        "database.py",
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
            print(f"⚠️ Файл не найден: {file_name}")
            continue

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
    print(" Обновление до v0.8")
    print(" Умный холодильник Мединки")
    print("====================================\n")

    backup_files()
    update_settings()
    patch_database()
    patch_app()

    ok = compile_files()

    print("\n====================================")

    if ok:
        print("✅ Обновление до v0.8 завершено.")
        print("")
        print("Запусти приложение:")
        print("python -m streamlit run app.py")
    else:
        print("⚠️ Есть ошибки синтаксиса. Пришли текст ошибки, я поправлю.")


if __name__ == "__main__":
    main()