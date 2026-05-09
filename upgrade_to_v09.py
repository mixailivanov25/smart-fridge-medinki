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
    backup_dir = PROJECT_DIR / f"backup_before_v09_{timestamp}"
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

    for version in ["v0.6", "v0.7", "v0.8"]:
        text = text.replace(f'APP_VERSION = "{version}"', 'APP_VERSION = "v0.9"')

    SETTINGS_FILE.write_text(text, encoding="utf-8")
    print("✅ settings.py обновлён до v0.9")


def patch_database():
    text = DB_FILE.read_text(encoding="utf-8")

    if "def ensure_v09_tables(" in text:
        print("ℹ️ database.py уже содержит функции v0.9")
        return

    addition = r'''

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
'''

    text = text.rstrip() + "\n" + addition + "\n"
    DB_FILE.write_text(text, encoding="utf-8")

    print("✅ database.py обновлён функциями v0.9")


def patch_app_imports(text):
    if "ensure_v09_tables" in text:
        print("ℹ️ app.py уже содержит импорты v0.9")
        return text

    # Вставляем импорты v0.9 после add_shopping_item_to_fridge, если есть v0.8
    old = '''    add_shopping_item_to_fridge'''

    new = '''    add_shopping_item_to_fridge,
    ensure_v09_tables,
    add_custom_recipe,
    get_custom_recipes,
    get_custom_recipe_by_id,
    delete_custom_recipe,
    get_custom_recipe_categories'''

    if old in text:
        text = text.replace(old, new, 1)
        print("✅ app.py: добавлены импорты database v0.9")
    else:
        print("⚠️ app.py: не найден add_shopping_item_to_fridge. Пробую альтернативную вставку.")

        old_alt = '''    get_accepted_week_menu_items'''

        new_alt = '''    get_accepted_week_menu_items,
    ensure_v09_tables,
    add_custom_recipe,
    get_custom_recipes,
    get_custom_recipe_by_id,
    delete_custom_recipe,
    get_custom_recipe_categories'''

        if old_alt in text:
            text = text.replace(old_alt, new_alt, 1)
            print("✅ app.py: импорты v0.9 добавлены альтернативным способом.")
        else:
            print("❌ app.py: не удалось автоматически добавить импорты v0.9.")

    if "ensure_v09_tables()" not in text:
        if "ensure_v08_tables()" in text:
            text = text.replace(
                "ensure_v08_tables()",
                "ensure_v08_tables()\nensure_v09_tables()",
                1
            )
            print("✅ app.py: добавлен вызов ensure_v09_tables()")
        else:
            text = text.replace(
                "init_db()",
                "init_db()\nensure_v09_tables()",
                1
            )
            print("✅ app.py: добавлен вызов ensure_v09_tables() после init_db()")

    return text


def patch_sidebar_radio_key(text):
    if 'key="main_navigation"' in text:
        print("ℹ️ app.py: key для навигации уже есть")
        return text

    old = '''page = st.sidebar.radio("Навигация", list(nav_labels.keys()), format_func=lambda item: nav_labels[item])'''

    new = '''page = st.sidebar.radio(
    "Навигация",
    list(nav_labels.keys()),
    format_func=lambda item: nav_labels[item],
    key="main_navigation"
)'''

    if old in text:
        text = text.replace(old, new)
        print("✅ app.py: добавлен key для навигации")
    else:
        print("⚠️ app.py: стандартная строка sidebar.radio не найдена. Возможно, key уже добавлен или формат другой.")

    return text


def patch_nav(text):
    if '"Аналитика": "📊 Аналитика"' in text:
        print("ℹ️ app.py: навигация v0.9 уже добавлена")
        return text

    # Добавляем после Дневник питания, если есть
    if '"Дневник питания": "📔 Дневник питания",' in text:
        text = text.replace(
            '    "Дневник питания": "📔 Дневник питания",',
            '    "Дневник питания": "📔 Дневник питания",\n'
            '    "Аналитика": "📊 Аналитика",\n'
            '    "Мои рецепты": "📝 Мои рецепты",'
        )
        print("✅ app.py: добавлены пункты Аналитика и Мои рецепты")
        return text

    # Если v0.8 не был установлен, добавляем после Сегодня
    if '"Сегодня": "📅 Сегодня",' in text:
        text = text.replace(
            '    "Сегодня": "📅 Сегодня",',
            '    "Сегодня": "📅 Сегодня",\n'
            '    "Аналитика": "📊 Аналитика",\n'
            '    "Мои рецепты": "📝 Мои рецепты",'
        )
        print("✅ app.py: добавлены пункты Аналитика и Мои рецепты после Сегодня")
        return text

    print("⚠️ app.py: не найдено место для добавления пунктов навигации v0.9")
    return text


def build_datetime_helpers():
    return r'''

def get_russian_weekday(dt):
    weekdays = [
        "понедельник",
        "вторник",
        "среда",
        "четверг",
        "пятница",
        "суббота",
        "воскресенье"
    ]

    return weekdays[dt.weekday()]


def get_russian_month(dt):
    months = [
        "января",
        "февраля",
        "марта",
        "апреля",
        "мая",
        "июня",
        "июля",
        "августа",
        "сентября",
        "октября",
        "ноября",
        "декабря"
    ]

    return months[dt.month - 1]


def render_current_datetime_card():
    now = datetime.now()

    weekday = get_russian_weekday(now)
    month = get_russian_month(now)

    date_text = f"{now.day} {month} {now.year}"
    time_text = now.strftime("%H:%M")

    st.markdown(f"""
    <div class="soft-card">
        <h3>🕒 Сегодня: {date_text}</h3>
        <p>
            <span class="status-pill pill-blue">День недели: {weekday}</span>
            <span class="status-pill pill-green">Текущее время: {time_text}</span>
            <span class="status-pill pill-purple">Версия: {APP_VERSION}</span>
        </p>
        <p class="muted">Время обновляется при перезагрузке страницы.</p>
    </div>
    """, unsafe_allow_html=True)


def render_quick_actions():
    st.subheader("⚡ Быстрые действия")

    c1, c2, c3 = st.columns(3)

    with c1:
        if st.button("➕ Добавить еду", use_container_width=True):
            st.session_state["main_navigation"] = "Дневник питания"
            st.rerun()

    with c2:
        if st.button("🛒 Добавить покупку", use_container_width=True):
            st.session_state["main_navigation"] = "Умные покупки"
            st.rerun()

    with c3:
        if st.button("🧊 Открыть холодильник", use_container_width=True):
            st.session_state["main_navigation"] = "Мой холодильник"
            st.rerun()


def render_today_calorie_cards():
    today_str = str(date.today())

    st.subheader("🍽️ Калории сегодня")

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

        if left >= 0:
            status_class = "pill-green"
            status_text = f"Осталось: {left} ккал"
        else:
            status_class = "pill-red"
            status_text = f"Перебор: {abs(left)} ккал"

        with cols[index % 2]:
            st.markdown(f"""
            <div class="person-card">
                <h3>{get_person_emoji(person)} {person}</h3>
                <span class="status-pill pill-blue">Цель: {target_calories} ккал</span>
                <span class="status-pill pill-purple">Съедено: {eaten} ккал</span>
                <span class="status-pill {status_class}">{status_text}</span>
            </div>
            """, unsafe_allow_html=True)

            st.progress(progress)
'''


def patch_datetime_helpers(text):
    if "def render_current_datetime_card(" in text:
        print("ℹ️ app.py: helpers даты/времени уже есть")
        return text

    marker = "def render_person_card(profile):"

    if marker not in text:
        print("⚠️ app.py: не найден marker render_person_card для вставки helpers.")
        return text

    text = text.replace(marker, build_datetime_helpers() + "\n\n" + marker)
    print("✅ app.py: добавлены helpers даты, времени и быстрых действий")
    return text


def patch_home_page(text):
    if "render_current_datetime_card()" in text and "render_quick_actions()" in text:
        print("ℹ️ app.py: главная уже обновлена v0.9")
        return text

    marker = '''    c1, c2, c3, c4 = st.columns(4)'''

    if marker not in text:
        print("⚠️ app.py: не найден блок метрик главной.")
        return text

    insertion = '''    render_current_datetime_card()

    render_quick_actions()

    render_today_calorie_cards()

'''

    text = text.replace(marker, insertion + marker, 1)
    print("✅ app.py: на главную добавлены дата, время, калории и быстрые кнопки")
    return text


def build_analytics_page():
    return r'''

elif page == "Аналитика":
    st.header("📊 Аналитика")

    render_page_intro(
        "Сводка по питанию, покупкам и холодильнику",
        "Здесь собраны ключевые показатели: калории, дневник, история готовки, списания и покупки.",
        "📊"
    )

    today_str = str(date.today())

    st.subheader("🍽️ Калории за сегодня")

    calorie_rows = []

    for person in PEOPLE:
        profile = get_user_profile(person)
        target = profile[1] if profile else 2000
        eaten = get_daily_calories(person, today_str)
        left = target - eaten

        calorie_rows.append({
            "Кто": person,
            "Цель": target,
            "Съедено": eaten,
            "Осталось": left,
            "Выполнено %": round((eaten / target) * 100) if target else 0
        })

    st.dataframe(pd.DataFrame(calorie_rows), use_container_width=True, hide_index=True)

    c1, c2, c3, c4 = st.columns(4)

    history = get_history()
    transactions = get_product_transactions()
    shopping_items = get_shopping_items(include_bought=True)
    diary_today = get_nutrition_diary_entries(diary_date=today_str, limit=500)

    with c1:
        st.metric("Записей в дневнике сегодня", len(diary_today))

    with c2:
        st.metric("Блюд в истории", len(history))

    with c3:
        st.metric("Операций списания/покупок", len(transactions))

    with c4:
        bought_count = len([item for item in shopping_items if item[8] == 1])
        st.metric("Купленных позиций", bought_count)

    st.divider()

    tab1, tab2, tab3, tab4 = st.tabs([
        "📔 Дневник",
        "📜 История блюд",
        "📉 Списания",
        "🛒 Покупки"
    ])

    with tab1:
        st.subheader("Дневник питания за сегодня")

        if not diary_today:
            st.info("Сегодня ещё нет записей в дневнике.")
        else:
            df = pd.DataFrame(
                diary_today,
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

    with tab2:
        st.subheader("История приготовленных блюд")

        if not history:
            st.info("История пока пустая.")
        else:
            df = pd.DataFrame(
                history,
                columns=["Блюдо", "Списано", "Калории", "Дата"]
            )

            st.dataframe(df.head(30), use_container_width=True, hide_index=True)

    with tab3:
        st.subheader("Последние операции с продуктами")

        if not transactions:
            st.info("Операций пока нет.")
        else:
            df = pd.DataFrame(
                transactions,
                columns=[
                    "ID",
                    "Product ID",
                    "Продукт",
                    "Изменение",
                    "Ед.",
                    "Действие",
                    "Причина",
                    "Блюдо",
                    "Кто",
                    "День",
                    "Приём",
                    "Дата"
                ]
            )

            st.dataframe(df.head(50), use_container_width=True, hide_index=True)

    with tab4:
        st.subheader("Покупки")

        if not shopping_items:
            st.info("Список покупок пуст.")
        else:
            df = pd.DataFrame(
                shopping_items,
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

            st.dataframe(df.head(50), use_container_width=True, hide_index=True)
'''


def build_my_recipes_page():
    return r'''

elif page == "Мои рецепты":
    st.header("📝 Мои рецепты")

    render_page_intro(
        "Собственная книга рецептов",
        "Добавляйте свои блюда, сохраняйте ингредиенты, шаги приготовления, калории, БЖУ, историю блюда и заметки.",
        "📝"
    )

    tab1, tab2, tab3 = st.tabs(["➕ Добавить рецепт", "📚 Мои рецепты", "❤️ В избранное / дневник"])

    with tab1:
        st.subheader("Добавить новый рецепт")

        with st.form("custom_recipe_form"):
            c1, c2 = st.columns(2)

            with c1:
                name = st.text_input("Название блюда", placeholder="Например: сырники Мединки")
                emoji = st.text_input("Иконка", value="🍽️")
                category = st.selectbox(
                    "Категория",
                    ["Завтрак", "Обед", "Ужин", "Перекус", "Салат", "Суп", "Десерт", "Другое"]
                )
                cooking_time = st.text_input("Время приготовления", placeholder="Например: 25 минут")

            with c2:
                calories = st.number_input("Калории", min_value=0.0, value=0.0, step=10.0)
                protein = st.number_input("Белки, г", min_value=0.0, value=0.0, step=1.0)
                fat = st.number_input("Жиры, г", min_value=0.0, value=0.0, step=1.0)
                carbs = st.number_input("Углеводы, г", min_value=0.0, value=0.0, step=1.0)

            ingredients_text = st.text_area(
                "Ингредиенты",
                height=140,
                placeholder="Например:\nтворог — 300 г\nяйцо — 1 шт\nмука — 50 г"
            )

            instructions_text = st.text_area(
                "Шаги приготовления",
                height=160,
                placeholder="Например:\n1. Смешать ингредиенты\n2. Сформировать сырники\n3. Обжарить на сковороде"
            )

            c3, c4 = st.columns(2)

            with c3:
                origin = st.text_input("Происхождение / кухня", placeholder="Например: домашняя кухня")

            with c4:
                history_text = st.text_area(
                    "История блюда",
                    placeholder="Например: семейный рецепт, который часто готовим на завтрак"
                )

            notes = st.text_area("Заметки", placeholder="Например: Мединке нравится со сметаной, Мишке — с мёдом")

            submitted = st.form_submit_button("💾 Сохранить рецепт")

            if submitted:
                if not name.strip():
                    st.error("Введите название блюда.")
                else:
                    add_custom_recipe(
                        name=name,
                        category=category,
                        cooking_time=cooking_time,
                        calories=calories,
                        protein=protein,
                        fat=fat,
                        carbs=carbs,
                        ingredients_text=ingredients_text,
                        instructions_text=instructions_text,
                        history=history_text,
                        origin=origin,
                        notes=notes,
                        emoji=emoji
                    )

                    st.success(f"Рецепт «{name}» сохранён.")
                    st.rerun()

    with tab2:
        st.subheader("Список моих рецептов")

        c1, c2 = st.columns(2)

        with c1:
            query = st.text_input("Поиск по рецептам", placeholder="Например: сырники, курица, завтрак")

        with c2:
            categories = ["Все категории"] + get_custom_recipe_categories()
            selected_category = st.selectbox("Категория", categories)

        recipes = get_custom_recipes(query=query, category=selected_category)

        if not recipes:
            st.info("Своих рецептов пока нет.")
        else:
            cols = st.columns(2)

            for index, recipe in enumerate(recipes):
                (
                    recipe_id,
                    name,
                    category,
                    cooking_time,
                    calories,
                    protein,
                    fat,
                    carbs,
                    ingredients_text,
                    instructions_text,
                    history_text,
                    origin,
                    notes,
                    emoji,
                    created_at
                ) = recipe

                with cols[index % 2]:
                    st.markdown(f"""
                    <div class="dish-card">
                        <div class="emoji-big">{emoji or "🍽️"}</div>
                        <h3>{name}</h3>
                        <span class="status-pill pill-purple">{category or "Без категории"}</span>
                        <span class="status-pill pill-blue">{cooking_time or "Время не указано"}</span>
                        <span class="status-pill pill-green">{calories or 0} ккал</span>
                        <br><br>
                        <b>БЖУ:</b> белки {protein or 0} г · жиры {fat or 0} г · углеводы {carbs or 0} г<br>
                        <b>Происхождение:</b> {origin or "не указано"}<br>
                        <p class="muted">{notes or ""}</p>
                    </div>
                    """, unsafe_allow_html=True)

                    with st.expander(f"Подробнее: {name}"):
                        st.write("### Ингредиенты")
                        st.text(ingredients_text or "Ингредиенты не указаны")

                        st.write("### Приготовление")
                        st.text(instructions_text or "Шаги не указаны")

                        st.write("### История блюда")
                        st.write(history_text or "История не указана")

                        st.write("### Заметки")
                        st.write(notes or "Заметок нет")

                        if st.button("🗑️ Удалить рецепт", key=f"delete_custom_recipe_{recipe_id}"):
                            delete_custom_recipe(recipe_id)
                            st.success("Рецепт удалён.")
                            st.rerun()

    with tab3:
        st.subheader("Добавить свой рецепт в дневник или любимые")

        recipes = get_custom_recipes()

        if not recipes:
            st.info("Сначала добавьте хотя бы один свой рецепт.")
        else:
            recipe_labels = [
                f"{row[0]} — {row[13] or '🍽️'} {row[1]} · {row[2]} · {row[4]} ккал"
                for row in recipes
            ]

            selected_label = st.selectbox("Выберите рецепт", recipe_labels)
            selected_id = int(selected_label.split(" — ")[0])
            recipe = get_custom_recipe_by_id(selected_id)

            if recipe:
                (
                    recipe_id,
                    name,
                    category,
                    cooking_time,
                    calories,
                    protein,
                    fat,
                    carbs,
                    ingredients_text,
                    instructions_text,
                    history_text,
                    origin,
                    notes,
                    emoji,
                    created_at
                ) = recipe

                st.markdown(f"""
                <div class="dish-card">
                    <div class="emoji-big">{emoji or "🍽️"}</div>
                    <h3>{name}</h3>
                    <span class="status-pill pill-purple">{category or "Без категории"}</span>
                    <span class="status-pill pill-blue">{cooking_time or "Время не указано"}</span>
                    <span class="status-pill pill-green">{calories or 0} ккал</span>
                </div>
                """, unsafe_allow_html=True)

                action_tabs = st.tabs(["📔 В дневник питания", "❤️ В любимые блюда"])

                with action_tabs[0]:
                    with st.form("custom_recipe_to_diary_form"):
                        c1, c2 = st.columns(2)

                        with c1:
                            person = st.selectbox("Кто", PEOPLE, key="custom_recipe_diary_person")
                            diary_date = st.date_input("Дата", value=date.today(), key="custom_recipe_diary_date")
                            meal_slot = st.selectbox(
                                "Приём пищи",
                                ["Завтрак", "Обед", "Ужин", "Перекус", "Дополнительно"],
                                key="custom_recipe_diary_slot"
                            )

                        with c2:
                            diary_calories = st.number_input(
                                "Калории",
                                min_value=0.0,
                                value=float(calories or 0),
                                step=10.0,
                                key="custom_recipe_diary_calories"
                            )
                            diary_protein = st.number_input(
                                "Белки",
                                min_value=0.0,
                                value=float(protein or 0),
                                step=1.0,
                                key="custom_recipe_diary_protein"
                            )
                            diary_fat = st.number_input(
                                "Жиры",
                                min_value=0.0,
                                value=float(fat or 0),
                                step=1.0,
                                key="custom_recipe_diary_fat"
                            )
                            diary_carbs = st.number_input(
                                "Углеводы",
                                min_value=0.0,
                                value=float(carbs or 0),
                                step=1.0,
                                key="custom_recipe_diary_carbs"
                            )

                        comment = st.text_area("Комментарий", value=notes or "", key="custom_recipe_diary_comment")

                        submitted = st.form_submit_button("➕ Добавить в дневник питания")

                        if submitted:
                            add_nutrition_diary_entry(
                                person=person,
                                diary_date=str(diary_date),
                                meal_slot=meal_slot,
                                dish_name=name,
                                calories=diary_calories,
                                protein=diary_protein,
                                fat=diary_fat,
                                carbs=diary_carbs,
                                comment=comment
                            )

                            st.success(f"«{name}» добавлено в дневник питания.")
                            st.rerun()

                with action_tabs[1]:
                    with st.form("custom_recipe_to_favorites_form"):
                        person = st.selectbox("Для кого добавить в любимые", PEOPLE, key="custom_recipe_favorite_person")
                        rating = st.slider("Оценка", min_value=1, max_value=5, value=5, key="custom_recipe_favorite_rating")
                        fav_notes = st.text_area("Заметка", value=notes or "", key="custom_recipe_favorite_notes")

                        submitted = st.form_submit_button("❤️ Добавить в любимые")

                        if submitted:
                            add_favorite_dish(
                                person=person,
                                dish_name=name,
                                source="custom_recipe",
                                rating=rating,
                                notes=fav_notes
                            )

                            st.success(f"«{name}» добавлено в любимые блюда {get_person_genitive(person)}.")
                            st.rerun()
'''


def patch_pages(text):
    if 'elif page == "Аналитика":' in text and 'elif page == "Мои рецепты":' in text:
        print("ℹ️ app.py: страницы v0.9 уже добавлены")
        return text

    marker = 'elif page == "Мой холодильник":'

    if marker not in text:
        print("⚠️ app.py: не найдено место для вставки страниц v0.9.")
        return text

    insertion = ""

    if 'elif page == "Аналитика":' not in text:
        insertion += build_analytics_page() + "\n\n"

    if 'elif page == "Мои рецепты":' not in text:
        insertion += build_my_recipes_page() + "\n\n"

    text = text.replace(marker, insertion + marker, 1)

    print("✅ app.py: добавлены страницы Аналитика и Мои рецепты")
    return text


def patch_app():
    text = APP_FILE.read_text(encoding="utf-8")

    text = patch_app_imports(text)
    text = patch_sidebar_radio_key(text)
    text = patch_nav(text)
    text = patch_datetime_helpers(text)
    text = patch_home_page(text)
    text = patch_pages(text)

    APP_FILE.write_text(text, encoding="utf-8")
    print("✅ app.py обновлён до v0.9")


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
    print(" Обновление до v0.9")
    print(" Умный холодильник Мединки")
    print("====================================\n")

    backup_files()
    update_settings()
    patch_database()
    patch_app()

    ok = compile_files()

    print("\n====================================")

    if ok:
        print("✅ Обновление до v0.9 завершено.")
        print("")
        print("Запусти приложение:")
        print("python -m streamlit run app.py")
    else:
        print("⚠️ Есть ошибки синтаксиса. Пришли текст ошибки, я поправлю.")


if __name__ == "__main__":
    main()