from pathlib import Path
from datetime import datetime
import shutil
import py_compile
import textwrap


PROJECT_DIR = Path(__file__).resolve().parent

APP_FILE = PROJECT_DIR / "app.py"
DB_FILE = PROJECT_DIR / "database.py"
SETTINGS_FILE = PROJECT_DIR / "settings.py"


def backup_files():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = PROJECT_DIR / f"backup_before_v07_{timestamp}"
    backup_dir.mkdir(exist_ok=True)

    for file_path in [APP_FILE, DB_FILE, SETTINGS_FILE]:
        if file_path.exists():
            shutil.copy2(file_path, backup_dir / file_path.name)

    print(f"📦 Резервная копия создана: {backup_dir}")
    return backup_dir


def update_settings():
    text = SETTINGS_FILE.read_text(encoding="utf-8")

    text = text.replace('APP_VERSION = "v0.6"', 'APP_VERSION = "v0.7"')

    SETTINGS_FILE.write_text(text, encoding="utf-8")
    print("✅ settings.py обновлён до v0.7")


def patch_database():
    text = DB_FILE.read_text(encoding="utf-8")

    if "def get_latest_accepted_week_menu(" in text:
        print("ℹ️ database.py уже содержит функции v0.7")
        return

    addition = r'''

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
'''

    text = text.rstrip() + "\n" + addition + "\n"

    DB_FILE.write_text(text, encoding="utf-8")
    print("✅ database.py обновлён функциями v0.7")


def patch_app_imports(text):
    # Добавляем импорт функций отмены/проверки меню
    if "get_latest_accepted_week_menu" not in text:
        text = text.replace(
            "from recipes import get_recipe_matches, find_product, to_base_unit, get_all_recipes",
            "from database import get_latest_accepted_week_menu, cancel_latest_accepted_week_menu\n"
            "from recipes import get_recipe_matches, find_product, to_base_unit, get_all_recipes"
        )

    return text


def patch_app_nav(text):
    if '"Сегодня": "📅 Сегодня"' in text:
        print("ℹ️ Навигация v0.7 уже добавлена")
        return text

    text = text.replace(
        '    "Главная": "🏠 Главная",',
        '    "Главная": "🏠 Главная",\n'
        '    "Сегодня": "📅 Сегодня",\n'
        '    "Скоро испортится": "⏰ Скоро испортится",'
    )

    print("✅ В навигацию добавлены страницы Сегодня и Скоро испортится")
    return text


def patch_accept_menu_safety(text):
    if "repeat_accept_confirm" in text:
        print("ℹ️ Защита принятия меню уже добавлена")
        return text

    old = '''            confirm = st.checkbox("Я понимаю, что продукты будут списаны из холодильника")

            notes = st.text_area("Заметка к меню", placeholder="Например: меню на следующую неделю")

            if st.button("✅ Принять меню на неделю и списать продукты", disabled=not confirm):'''

    new = '''            latest_menu = get_latest_accepted_week_menu()
            already_accepted_today = False

            if latest_menu:
                latest_menu_id, latest_title, latest_status, latest_notes, latest_accepted_at = latest_menu

                try:
                    latest_date = datetime.fromisoformat(latest_accepted_at).date()
                    already_accepted_today = latest_date == date.today()
                except Exception:
                    already_accepted_today = False

                if already_accepted_today:
                    st.warning(
                        f"Сегодня уже было принято меню: ID {latest_menu_id}. "
                        "Если принять меню повторно, продукты спишутся ещё раз."
                    )

            confirm = st.checkbox("Я понимаю, что продукты будут списаны из холодильника")
            repeat_accept_confirm = True

            if already_accepted_today:
                repeat_accept_confirm = st.checkbox("Я точно хочу принять меню повторно сегодня")

            notes = st.text_area("Заметка к меню", placeholder="Например: меню на следующую неделю")

            accept_disabled = not confirm or not repeat_accept_confirm

            if st.button("✅ Принять меню на неделю и списать продукты", disabled=accept_disabled):'''

    if old not in text:
        print("⚠️ Не нашёл стандартный блок принятия меню. Пропускаю patch_accept_menu_safety.")
        return text

    text = text.replace(old, new)
    print("✅ Добавлена защита от повторного принятия меню")
    return text


def patch_cancel_menu_ui(text):
    if "Отменить последнее принятое меню" in text:
        print("ℹ️ Интерфейс отмены меню уже добавлен")
        return text

    old = '''        with tabs[4]:
            menus = get_accepted_week_menus()'''

    new = '''        with tabs[4]:
            st.subheader("↩️ Управление принятыми меню")

            latest_menu = get_latest_accepted_week_menu()

            if latest_menu:
                latest_menu_id, latest_title, latest_status, latest_notes, latest_accepted_at = latest_menu

                st.info(
                    f"Последнее активное меню: ID {latest_menu_id} · "
                    f"{latest_title} · принято: {latest_accepted_at}"
                )

                cancel_confirm = st.checkbox(
                    "Я понимаю, что отмена вернёт продукты по последнему принятому меню",
                    key="cancel_latest_menu_confirm"
                )

                if st.button("↩️ Отменить последнее принятое меню", disabled=not cancel_confirm):
                    cancel_report = cancel_latest_accepted_week_menu()

                    if cancel_report["ok"]:
                        st.success(cancel_report["message"])

                        if cancel_report["returned"]:
                            st.write("### Возвращено в холодильник")
                            st.dataframe(
                                pd.DataFrame(cancel_report["returned"]),
                                use_container_width=True,
                                hide_index=True
                            )

                        st.info("Откройте «Мой холодильник» и «Списания», чтобы проверить изменения.")
                        st.rerun()
                    else:
                        st.warning(cancel_report["message"])
            else:
                st.info("Активных принятых меню для отмены нет.")

            st.divider()

            menus = get_accepted_week_menus()'''

    if old not in text:
        print("⚠️ Не нашёл блок tabs[4] для принятых меню. Пропускаю patch_cancel_menu_ui.")
        return text

    text = text.replace(old, new)
    print("✅ Добавлена отмена последнего принятого меню")
    return text


def build_today_page_block():
    return r'''

elif page == "Сегодня":
    st.header("📅 Сегодня")

    render_page_intro(
        "План на сегодня",
        "Здесь собраны блюда на текущий день для Мишки и Мединки, а также продукты, которые лучше использовать быстрее.",
        "📅"
    )

    if not products:
        st.info("Сначала добавьте продукты или загрузите демо-данные.")
    else:
        day_names = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]
        today_name = day_names[date.today().weekday()]

        st.subheader(f"Сегодня: {today_name}")

        menu_mishka_today = build_personal_week_menu("Мишка", products)
        menu_medinka_today = build_personal_week_menu("Мединка", products)

        today_tabs = st.tabs(["🐻 Мишка", "🌸 Мединка", "⚠️ Срочно использовать"])

        with today_tabs[0]:
            if menu_mishka_today:
                day_plan = next((day for day in menu_mishka_today["week"] if day["day"] == today_name), None)

                if day_plan:
                    st.markdown(f"""
                    <div class="gradient-card">
                        <h3>🐻 Меню Мишки на сегодня</h3>
                        <p>Итого: {day_plan["calories"]} ккал · Цель: {day_plan["target_calories"]} ккал · {day_plan["status"]}</p>
                    </div>
                    """, unsafe_allow_html=True)

                    for meal in day_plan["meals"]:
                        recipe = meal["recipe"]
                        meta = get_dish_metadata(recipe["name"])
                        fav = "❤️" if meal["is_favorite"] else ""

                        st.markdown(f"""
                        <div class="menu-meal">
                            <b>{meal["slot"]}:</b> {meta.get("emoji", "🍽️")} {recipe["name"]} {fav}<br>
                            <span class="status-pill pill-blue">{recipe["calories"]} ккал</span>
                            <span class="status-pill pill-purple">{recipe["category"]}</span>
                        </div>
                        """, unsafe_allow_html=True)

        with today_tabs[1]:
            if menu_medinka_today:
                day_plan = next((day for day in menu_medinka_today["week"] if day["day"] == today_name), None)

                if day_plan:
                    st.markdown(f"""
                    <div class="gradient-card">
                        <h3>🌸 Меню Мединки на сегодня</h3>
                        <p>Итого: {day_plan["calories"]} ккал · Цель: {day_plan["target_calories"]} ккал · {day_plan["status"]}</p>
                    </div>
                    """, unsafe_allow_html=True)

                    for meal in day_plan["meals"]:
                        recipe = meal["recipe"]
                        meta = get_dish_metadata(recipe["name"])
                        fav = "❤️" if meal["is_favorite"] else ""

                        st.markdown(f"""
                        <div class="menu-meal">
                            <b>{meal["slot"]}:</b> {meta.get("emoji", "🍽️")} {recipe["name"]} {fav}<br>
                            <span class="status-pill pill-blue">{recipe["calories"]} ккал</span>
                            <span class="status-pill pill-purple">{recipe["category"]}</span>
                        </div>
                        """, unsafe_allow_html=True)

        with today_tabs[2]:
            urgent_products = []

            for product in products:
                status_text, status_color = expiration_status(product[6])

                if status_color in ["yellow", "red"]:
                    urgent_products.append((product, status_text, status_color))

            if not urgent_products:
                st.success("Срочных продуктов нет.")
            else:
                for product, status_text, status_color in urgent_products:
                    badge = "badge-red" if status_color == "red" else "badge-yellow"

                    st.markdown(f"""
                    <div class="card">
                        <h3>{product[1]}</h3>
                        <p><b>{product[2]}</b> {product[3]} · {product[5] or "Без категории"}</p>
                        <span class="{badge}">{status_text}</span>
                    </div>
                    """, unsafe_allow_html=True)
'''


def build_expiring_page_block():
    return r'''

elif page == "Скоро испортится":
    st.header("⏰ Скоро испортится")

    render_page_intro(
        "Продукты, которые лучше использовать первыми",
        "Приложение показывает продукты с коротким сроком годности и рецепты, куда их можно применить.",
        "⏰"
    )

    if not products:
        st.info("Пока продуктов нет.")
    else:
        urgent_products = []
        normal_products = []

        for product in products:
            status_text, status_color = expiration_status(product[6])

            if status_color in ["yellow", "red"]:
                urgent_products.append((product, status_text, status_color))
            else:
                normal_products.append((product, status_text, status_color))

        col1, col2 = st.columns(2)

        with col1:
            st.metric("Требуют внимания", len(urgent_products))

        with col2:
            st.metric("Остальные продукты", len(normal_products))

        if not urgent_products:
            st.success("Отлично, продуктов с критичным сроком годности нет.")
        else:
            recipe_matches = get_recipe_matches(products)

            for product, status_text, status_color in urgent_products:
                badge = "badge-red" if status_color == "red" else "badge-yellow"

                st.markdown(f"""
                <div class="card">
                    <h3>{product[1]}</h3>
                    <p><b>{product[2]}</b> {product[3]} · {product[5] or "Без категории"}</p>
                    <span class="{badge}">{status_text}</span>
                </div>
                """, unsafe_allow_html=True)

                product_name = str(product[1]).lower()

                suitable = []

                for item in recipe_matches:
                    recipe = item["recipe"]
                    haystack = recipe["name"].lower() + " " + recipe.get("description", "").lower()

                    for ingredient in recipe.get("ingredients", []):
                        haystack += " " + ingredient.get("name", "").lower()
                        haystack += " " + " ".join(ingredient.get("variants", [])).lower()

                    if product_name in haystack:
                        suitable.append(item)

                if suitable:
                    with st.expander(f"Рецепты с продуктом «{product[1]}»"):
                        for item in suitable[:5]:
                            recipe = item["recipe"]
                            meta = get_dish_metadata(recipe["name"])

                            if item["can_make"]:
                                status_badge = "<span class='badge-green'>Можно приготовить</span>"
                            else:
                                status_badge = "<span class='badge-yellow'>Нужно докупить</span>"

                            st.markdown(f"""
                            <div class="menu-meal">
                                <b>{meta.get("emoji", "🍽️")} {recipe["name"]}</b><br>
                                <span class="status-pill pill-blue">{recipe["calories"]} ккал</span>
                                <span class="status-pill pill-purple">{recipe["category"]}</span>
                                {status_badge}
                            </div>
                            """, unsafe_allow_html=True)
                else:
                    st.caption("Пока нет рецептов с этим продуктом.")
'''


def patch_new_pages(text):
    if 'elif page == "Сегодня":' in text:
        print("ℹ️ Страницы Сегодня / Скоро испортится уже добавлены")
        return text

    marker = 'elif page == "Мой холодильник":'

    if marker not in text:
        print("⚠️ Не нашёл место для вставки новых страниц.")
        return text

    insertion = build_today_page_block() + "\n" + build_expiring_page_block() + "\n\n"
    text = text.replace(marker, insertion + marker)

    print("✅ Добавлены страницы Сегодня и Скоро испортится")
    return text


def patch_app():
    text = APP_FILE.read_text(encoding="utf-8")

    text = patch_app_imports(text)
    text = patch_app_nav(text)
    text = patch_accept_menu_safety(text)
    text = patch_cancel_menu_ui(text)
    text = patch_new_pages(text)

    APP_FILE.write_text(text, encoding="utf-8")
    print("✅ app.py обновлён до v0.7")


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
    print(" Обновление до v0.7")
    print(" Умный холодильник Мединки")
    print("====================================\n")

    backup_files()
    update_settings()
    patch_database()
    patch_app()

    ok = compile_files()

    print("\n====================================")

    if ok:
        print("✅ Обновление до v0.7 завершено.")
        print("")
        print("Запусти приложение:")
        print("python -m streamlit run app.py")
    else:
        print("⚠️ Есть ошибки синтаксиса. Пришли текст ошибки, я поправлю.")


if __name__ == "__main__":
    main()