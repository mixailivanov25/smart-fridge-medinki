from pathlib import Path
from datetime import datetime
import shutil
import py_compile
import subprocess
import re


PROJECT_DIR = Path(__file__).resolve().parent

APP_FILE = PROJECT_DIR / "app.py"
SETTINGS_FILE = PROJECT_DIR / "settings.py"


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
    backup_dir = PROJECT_DIR / f"backup_before_v112_stress_perf_{timestamp}"
    backup_dir.mkdir(exist_ok=True)

    for file_path in [APP_FILE, SETTINGS_FILE]:
        if file_path.exists():
            shutil.copy2(file_path, backup_dir / file_path.name)

    print(f"📦 Резервная копия создана: {backup_dir.name}")


def update_settings():
    if not SETTINGS_FILE.exists():
        print("❌ settings.py не найден.")
        return False

    text = SETTINGS_FILE.read_text(encoding="utf-8")

    if "APP_VERSION" in text:
        text = re.sub(
            r'APP_VERSION\s*=\s*"[^"]+"',
            'APP_VERSION = "v1.1.2"',
            text
        )
    else:
        text += '\nAPP_VERSION = "v1.1.2"\n'

    SETTINGS_FILE.write_text(text, encoding="utf-8")
    print("✅ settings.py обновлён до v1.1.2")
    return True


def patch_database_imports(text):
    if "get_db_kind" in text:
        print("ℹ️ get_db_kind уже импортирован или используется")
    else:
        text = text.replace(
            "from database import (",
            "from database import (\n    get_db_kind,",
            1
        )
        print("✅ Добавлен импорт get_db_kind")

    # На всякий случай добавляем delete_shopping_item, если его нет
    if "delete_shopping_item" not in text:
        if "get_shopping_items," in text:
            text = text.replace(
                "get_shopping_items,",
                "get_shopping_items,\n    delete_shopping_item,",
                1
            )
            print("✅ Добавлен импорт delete_shopping_item")
        else:
            print("⚠️ Не нашёл get_shopping_items для добавления delete_shopping_item")

    return text


def patch_bootstrap_performance(text):
    """
    Убираем повторную инициализацию таблиц на каждый rerun Streamlit.
    Это особенно важно для Supabase, потому что каждый клик создавал лишние DDL-запросы.
    """

    if "def bootstrap_database_once()" in text:
        print("ℹ️ bootstrap_database_once уже добавлен")
        return text

    exact = """init_db()
ensure_v08_tables()
ensure_v09_tables()"""

    replacement = """@st.cache_resource
def bootstrap_database_once():
    init_db()
    ensure_v08_tables()
    ensure_v09_tables()
    return True


bootstrap_database_once()"""

    if exact in text:
        text = text.replace(exact, replacement, 1)
        print("✅ Инициализация БД обёрнута в st.cache_resource")
        return text

    # Запасной вариант, если в app.py только init_db()
    if "init_db()" in text:
        text = text.replace(
            "init_db()",
            """@st.cache_resource
def bootstrap_database_once():
    init_db()
    try:
        ensure_v08_tables()
        ensure_v09_tables()
    except Exception:
        pass
    return True


bootstrap_database_once()""",
            1
        )
        print("✅ Инициализация БД оптимизирована запасным способом")
        return text

    print("⚠️ Не нашёл init_db() для оптимизации")
    return text


def patch_nav(text):
    if '"Стресс-тест": "🧪 Стресс-тест"' in text:
        print("ℹ️ Стресс-тест уже есть в навигации")
        return text

    # Лучше добавить рядом с Аналитикой
    if '"Аналитика": "📊 Аналитика",' in text:
        text = text.replace(
            '    "Аналитика": "📊 Аналитика",',
            '    "Аналитика": "📊 Аналитика",\n'
            '    "Стресс-тест": "🧪 Стресс-тест",',
            1
        )
        print("✅ Стресс-тест добавлен после Аналитики")
        return text

    # Запасной вариант — после Главной
    if '"Главная": "🏠 Главная",' in text:
        text = text.replace(
            '    "Главная": "🏠 Главная",',
            '    "Главная": "🏠 Главная",\n'
            '    "Стресс-тест": "🧪 Стресс-тест",',
            1
        )
        print("✅ Стресс-тест добавлен после Главной")
        return text

    print("⚠️ Не нашёл место для добавления Стресс-теста в навигацию")
    return text


def build_stress_page():
    return r'''

elif page == "Стресс-тест":
    st.header("🧪 Стресс-тест приложения")

    render_page_intro(
        "Проверка связок приложения, облака и базы данных",
        "Этот раздел проверяет ключевые функции: базу данных, холодильник, дневник, покупки, любимые блюда, свои рецепты, меню и историю.",
        "🧪"
    )

    st.warning(
        "Стресс-тест создаёт временные записи с префиксом __stress_test__ "
        "и затем пытается их удалить. Тест не принимает недельное меню и не списывает реальные продукты."
    )

    def add_result(results, name, ok, details=""):
        results.append({
            "Проверка": name,
            "Статус": "✅ OK" if ok else "❌ Ошибка",
            "Детали": details
        })

    def cleanup_products_by_name(product_name):
        deleted = 0

        for product in get_products():
            if str(product[1]).lower().strip() == product_name.lower().strip():
                delete_product(product[0])
                deleted += 1

        return deleted

    def cleanup_shopping_by_name(product_name):
        deleted = 0

        try:
            items = get_shopping_items(include_bought=True)

            for item in items:
                if str(item[1]).lower().strip() == product_name.lower().strip():
                    delete_shopping_item(item[0])
                    deleted += 1
        except Exception:
            pass

        return deleted

    def cleanup_diary_by_dish(dish_name):
        deleted = 0

        try:
            entries = get_nutrition_diary_entries(limit=1000)

            for entry in entries:
                if str(entry[4]).lower().strip() == dish_name.lower().strip():
                    delete_nutrition_diary_entry(entry[0])
                    deleted += 1
        except Exception:
            pass

        return deleted

    def cleanup_favorites_by_dish(dish_name):
        deleted = 0

        try:
            favorites = get_favorite_dishes()

            for favorite in favorites:
                if str(favorite[2]).lower().strip() == dish_name.lower().strip():
                    delete_favorite_dish(favorite[0])
                    deleted += 1
        except Exception:
            pass

        return deleted

    def cleanup_custom_recipes_by_name(recipe_name):
        deleted = 0

        try:
            recipes = get_custom_recipes(query=recipe_name)

            for recipe in recipes:
                if str(recipe[1]).lower().strip() == recipe_name.lower().strip():
                    delete_custom_recipe(recipe[0])
                    deleted += 1
        except Exception:
            pass

        return deleted

    def run_stress_test():
        results = []

        suffix = datetime.now().strftime("%Y%m%d_%H%M%S")
        test_product = f"__stress_test_product_{suffix}"
        test_dish = f"__stress_test_dish_{suffix}"
        test_recipe = f"__stress_test_recipe_{suffix}"
        today_str = str(date.today())

        # 1. DB kind
        try:
            db_kind = get_db_kind()
            add_result(results, "Тип базы данных", True, db_kind)
        except Exception as e:
            add_result(results, "Тип базы данных", False, str(e))

        # 2. Products read
        try:
            products_before = get_products()
            add_result(results, "Чтение холодильника", True, f"Продуктов: {len(products_before)}")
        except Exception as e:
            add_result(results, "Чтение холодильника", False, str(e))

        # 3. Product create/read/delete
        try:
            add_or_update_product(
                name=test_product,
                quantity=1,
                unit="шт",
                calories_per_100g=10,
                category="Стресс-тест",
                expiration_date=today_str
            )

            found = [
                product for product in get_products()
                if str(product[1]).lower().strip() == test_product.lower().strip()
            ]

            if not found:
                raise RuntimeError("Тестовый продукт не найден после добавления")

            deleted = cleanup_products_by_name(test_product)

            add_result(
                results,
                "Добавление/удаление продукта",
                True,
                f"Создано: {len(found)}, удалено: {deleted}"
            )
        except Exception as e:
            add_result(results, "Добавление/удаление продукта", False, str(e))

        # 4. Nutrition diary
        try:
            add_nutrition_diary_entry(
                person="Мишка",
                diary_date=today_str,
                meal_slot="Перекус",
                dish_name=test_dish,
                calories=123,
                protein=1,
                fat=2,
                carbs=3,
                comment="stress test"
            )

            entries = get_nutrition_diary_entries(
                person="Мишка",
                diary_date=today_str,
                limit=500
            )

            found = [
                entry for entry in entries
                if str(entry[4]).lower().strip() == test_dish.lower().strip()
            ]

            if not found:
                raise RuntimeError("Запись дневника не найдена после добавления")

            deleted = cleanup_diary_by_dish(test_dish)

            add_result(
                results,
                "Дневник питания",
                True,
                f"Создано: {len(found)}, удалено: {deleted}"
            )
        except Exception as e:
            add_result(results, "Дневник питания", False, str(e))

        # 5. Smart shopping
        try:
            add_shopping_item(
                name=test_product,
                amount=2,
                unit="шт",
                category="Стресс-тест",
                calories_per_100g=10,
                expiration_date=today_str,
                source="stress_test"
            )

            items = get_shopping_items(include_bought=True)

            found = [
                item for item in items
                if str(item[1]).lower().strip() == test_product.lower().strip()
            ]

            if not found:
                raise RuntimeError("Покупка не найдена после добавления")

            deleted = cleanup_shopping_by_name(test_product)

            add_result(
                results,
                "Умные покупки",
                True,
                f"Создано: {len(found)}, удалено: {deleted}"
            )
        except Exception as e:
            add_result(results, "Умные покупки", False, str(e))

        # 6. Favorites
        try:
            add_favorite_dish(
                person="Мишка",
                dish_name=test_dish,
                source="stress_test",
                rating=5,
                notes="stress test"
            )

            favorites = get_favorite_dishes("Мишка")

            found = [
                favorite for favorite in favorites
                if str(favorite[2]).lower().strip() == test_dish.lower().strip()
            ]

            if not found:
                raise RuntimeError("Любимое блюдо не найдено после добавления")

            deleted = cleanup_favorites_by_dish(test_dish)

            add_result(
                results,
                "Любимые блюда",
                True,
                f"Создано: {len(found)}, удалено: {deleted}"
            )
        except Exception as e:
            add_result(results, "Любимые блюда", False, str(e))

        # 7. Custom recipes
        try:
            add_custom_recipe(
                name=test_recipe,
                category="Стресс-тест",
                cooking_time="1 минута",
                calories=111,
                protein=1,
                fat=1,
                carbs=1,
                ingredients_text="тестовый ингредиент",
                instructions_text="тестовый шаг",
                history="тестовая история",
                origin="стресс-тест",
                notes="stress test",
                emoji="🧪"
            )

            recipes = get_custom_recipes(query=test_recipe)

            found = [
                recipe for recipe in recipes
                if str(recipe[1]).lower().strip() == test_recipe.lower().strip()
            ]

            if not found:
                raise RuntimeError("Свой рецепт не найден после добавления")

            deleted = cleanup_custom_recipes_by_name(test_recipe)

            add_result(
                results,
                "Мои рецепты",
                True,
                f"Создано: {len(found)}, удалено: {deleted}"
            )
        except Exception as e:
            add_result(results, "Мои рецепты", False, str(e))

        # 8. Menu build
        try:
            current_products = get_products()

            menu_mishka = build_personal_week_menu("Мишка", current_products)
            menu_medinka = build_personal_week_menu("Мединка", current_products)

            if not menu_mishka or not menu_medinka:
                raise RuntimeError("Меню для одного из пользователей не построилось")

            add_result(
                results,
                "Построение меню",
                True,
                f"Мишка: {len(menu_mishka['week'])} дней, Мединка: {len(menu_medinka['week'])} дней"
            )
        except Exception as e:
            add_result(results, "Построение меню", False, str(e))

        # 9. Shopping list for menu
        try:
            current_products = get_products()
            menu_mishka = build_personal_week_menu("Мишка", current_products)
            menu_medinka = build_personal_week_menu("Мединка", current_products)

            shopping_mishka = build_shopping_list_for_menu(menu_mishka, current_products)
            shopping_medinka = build_shopping_list_for_menu(menu_medinka, current_products)

            add_result(
                results,
                "Список покупок для меню",
                True,
                f"Мишка: {len(shopping_mishka)}, Мединка: {len(shopping_medinka)}"
            )
        except Exception as e:
            add_result(results, "Список покупок для меню", False, str(e))

        # 10. History read
        try:
            history = get_history()
            add_result(results, "История блюд", True, f"Записей: {len(history)}")
        except Exception as e:
            add_result(results, "История блюд", False, str(e))

        # 11. Transactions read
        try:
            transactions = get_product_transactions()
            add_result(results, "Списания/транзакции", True, f"Записей: {len(transactions)}")
        except Exception as e:
            add_result(results, "Списания/транзакции", False, str(e))

        # 12. Accepted menus read
        try:
            accepted_menus = get_accepted_week_menus()
            add_result(results, "Принятые меню", True, f"Записей: {len(accepted_menus)}")
        except Exception as e:
            add_result(results, "Принятые меню", False, str(e))

        return results

    st.subheader("🚦 Быстрая проверка")

    col1, col2, col3 = st.columns(3)

    with col1:
        try:
            st.metric("База", get_db_kind())
        except Exception:
            st.metric("База", "ошибка")

    with col2:
        try:
            st.metric("Продуктов", len(get_products()))
        except Exception:
            st.metric("Продуктов", "ошибка")

    with col3:
        try:
            st.metric("Записей истории", len(get_history()))
        except Exception:
            st.metric("История", "ошибка")

    st.divider()

    if st.button("🧪 Запустить стресс-тест", use_container_width=True):
        with st.spinner("Проверяю приложение, облако и базу данных..."):
            results = run_stress_test()

        df = pd.DataFrame(results)

        st.dataframe(df, use_container_width=True, hide_index=True)

        errors = [row for row in results if not row["Статус"].startswith("✅")]

        if errors:
            st.error(f"Найдены ошибки: {len(errors)}")
            st.write("Ошибки:")
            st.dataframe(pd.DataFrame(errors), use_container_width=True, hide_index=True)
        else:
            st.success("Все базовые связки прошли стресс-тест ✅")

    st.divider()

    st.subheader("📱 Почему мобильная версия может тормозить")

    st.markdown("""
    Возможные причины:

    - бесплатный Streamlit Cloud может «засыпать», первый запуск после паузы медленный;
    - Supabase находится в другом регионе, запросы идут дольше;
    - Streamlit перерисовывает страницу после каждого действия;
    - тяжёлые страницы с таблицами и меню грузятся дольше на телефоне;
    - мобильный интернет может быть медленнее Wi-Fi.

    Что уже оптимизировано:

    - инициализация базы теперь кэшируется через `st.cache_resource`;
    - стресс-тест проверяет Supabase изнутри облачного приложения.

    Что можно сделать дальше:

    - добавить кэширование чтения продуктов и рецептов на 10–30 секунд;
    - сделать главную страницу легче;
    - вынести тяжёлые таблицы в отдельные вкладки;
    - подключить сервис, который будет держать Streamlit Cloud «проснувшимся».
    """)
'''


def patch_stress_page(text):
    if 'elif page == "Стресс-тест":' in text:
        print("ℹ️ Страница Стресс-тест уже добавлена")
        return text

    marker = 'elif page == "Мой холодильник":'

    if marker not in text:
        print("⚠️ Не найдено место для вставки страницы Стресс-тест")
        return text

    text = text.replace(marker, build_stress_page() + "\n\n" + marker, 1)
    print("✅ Добавлена страница Стресс-тест")
    return text


def patch_app():
    if not APP_FILE.exists():
        print("❌ app.py не найден.")
        return False

    text = APP_FILE.read_text(encoding="utf-8")

    text = patch_database_imports(text)
    text = patch_bootstrap_performance(text)
    text = patch_nav(text)
    text = patch_stress_page(text)

    APP_FILE.write_text(text, encoding="utf-8")
    print("✅ app.py обновлён")
    return True


def compile_files():
    print("\n==============================")
    print("Проверяю синтаксис")
    print("==============================")

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
    print("\n==============================")
    print("Пробую отправить изменения на GitHub")
    print("==============================")

    if not (PROJECT_DIR / ".git").exists():
        print("ℹ️ Git-репозиторий не найден. Пропускаю commit/push.")
        return

    run("git add .", check=False)

    status = run("git status --short", check=False)

    if not status.stdout.strip():
        print("ℹ️ Нет изменений для коммита.")
        return

    commit = run('git commit -m "v1.1.2 stress test and performance"', check=False)

    if commit.returncode != 0:
        combined = (commit.stdout + commit.stderr).lower()

        if "nothing to commit" in combined:
            print("ℹ️ Коммит не нужен.")
        else:
            print("⚠️ Commit завершился нестандартно. Продолжаю push.")

    push = run("git push", check=False)

    if push.returncode == 0:
        print("✅ Изменения отправлены на GitHub. Streamlit Cloud скоро обновится.")
    else:
        print("⚠️ Не удалось автоматически сделать git push.")
        print("Можно вручную выполнить:")
        print("git add .")
        print('git commit -m "v1.1.2 stress test and performance"')
        print("git push")


def main():
    print("====================================")
    print(" v1.1.2 Stress Test & Performance")
    print(" Умный холодильник Мединки")
    print("====================================\n")

    backup_files()

    if not update_settings():
        return

    if not patch_app():
        return

    ok = compile_files()

    print("\n==============================")

    if ok:
        print("✅ v1.1.2 установлен.")
        git_commit_push()
        print("\nЧто делать дальше:")
        print("1. Локально: python -m streamlit run app.py")
        print("2. В облаке дождаться обновления или нажать Reboot app.")
        print("3. Открыть страницу 🧪 Стресс-тест.")
        print("4. Нажать «Запустить стресс-тест».")
    else:
        print("⚠️ Есть ошибки синтаксиса. Пришли текст ошибки, я поправлю.")


if __name__ == "__main__":
    main()