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
    backup_dir = PROJECT_DIR / f"backup_before_v12_speed_{timestamp}"
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
            'APP_VERSION = "v1.2"',
            text
        )
    else:
        text += '\nAPP_VERSION = "v1.2"\n'

    SETTINGS_FILE.write_text(text, encoding="utf-8")
    print("✅ settings.py обновлён до v1.2")
    return True


def patch_login_default_page(text):
    changed = False

    # После успешного входа открываем быстрый экран
    if 'st.session_state["main_navigation"] = "Главная"' in text:
        text = text.replace(
            'st.session_state["main_navigation"] = "Главная"',
            'st.session_state["main_navigation"] = "Быстрый экран"'
        )
        changed = True

    # Если где-то одинарные кавычки
    if "st.session_state['main_navigation'] = 'Главная'" in text:
        text = text.replace(
            "st.session_state['main_navigation'] = 'Главная'",
            "st.session_state['main_navigation'] = 'Быстрый экран'"
        )
        changed = True

    if changed:
        print("✅ После входа будет открываться Быстрый экран")
    else:
        print("ℹ️ Не нашёл установку Главной после входа или она уже изменена")

    return text


def patch_nav(text):
    if '"Быстрый экран": "📱 Быстрый экран"' in text:
        print("ℹ️ Быстрый экран уже есть в навигации")
        return text

    marker = '    "Главная": "🏠 Главная",'

    if marker not in text:
        print("⚠️ Не найдено место для добавления Быстрого экрана в nav_labels")
        return text

    replacement = '''    "Быстрый экран": "📱 Быстрый экран",
    "Главная": "🏠 Главная",'''

    text = text.replace(marker, replacement, 1)
    print("✅ Быстрый экран добавлен первым пунктом навигации")
    return text


def build_speed_helpers():
    return r'''

# -----------------------------
# v1.2 Speed helpers
# -----------------------------
@st.cache_data(ttl=15)
def cached_fast_products():
    return get_products()


@st.cache_data(ttl=30)
def cached_fast_profiles():
    return get_user_profiles()


@st.cache_data(ttl=15)
def cached_fast_daily_calories(person, diary_date):
    return get_daily_calories(person, diary_date)


@st.cache_data(ttl=20)
def cached_fast_recipe_matches(products_as_tuple):
    products_list = list(products_as_tuple)
    return get_recipe_matches(products_list)


def clear_app_cache():
    try:
        st.cache_data.clear()
    except Exception:
        pass

    try:
        st.cache_resource.clear()
    except Exception:
        pass


def render_speed_refresh_button(location="main"):
    if st.button("🔄 Обновить данные", key=f"refresh_data_{location}", use_container_width=True):
        clear_app_cache()
        st.success("Данные обновлены.")
        st.rerun()


def get_today_name_ru():
    day_names = [
        "Понедельник",
        "Вторник",
        "Среда",
        "Четверг",
        "Пятница",
        "Суббота",
        "Воскресенье"
    ]

    return day_names[date.today().weekday()]


def get_urgent_products_for_fast_screen(products):
    urgent = []

    for product in products:
        status_text, status_color = expiration_status(product[6])

        if status_color in ["yellow", "red"]:
            urgent.append((product, status_text, status_color))

    return urgent


def render_fast_calorie_card(person):
    today_str = str(date.today())
    profile = get_user_profile(person)

    if profile:
        target = profile[1]
    else:
        target = 2000

    eaten = cached_fast_daily_calories(person, today_str)
    left = target - eaten

    progress = min(eaten / target, 1.0) if target else 0

    if left >= 0:
        status_class = "pill-green"
        status_text = f"Осталось: {left} ккал"
    else:
        status_class = "pill-red"
        status_text = f"Перебор: {abs(left)} ккал"

    st.markdown(f"""
    <div class="person-card">
        <h3>{get_person_emoji(person)} {person}</h3>
        <span class="status-pill pill-blue">Цель: {target} ккал</span>
        <span class="status-pill pill-purple">Съедено: {eaten} ккал</span>
        <span class="status-pill {status_class}">{status_text}</span>
    </div>
    """, unsafe_allow_html=True)

    st.progress(progress)


def render_fast_action_buttons():
    st.subheader("⚡ Быстрые действия")

    c1, c2 = st.columns(2)

    with c1:
        if st.button("➕ Добавить еду", use_container_width=True, key="fast_add_food"):
            st.session_state["main_navigation"] = "Дневник питания"
            st.rerun()

    with c2:
        if st.button("🛒 Добавить покупку", use_container_width=True, key="fast_add_purchase"):
            st.session_state["main_navigation"] = "Умные покупки"
            st.rerun()

    c3, c4 = st.columns(2)

    with c3:
        if st.button("🧊 Холодильник", use_container_width=True, key="fast_open_fridge"):
            st.session_state["main_navigation"] = "Мой холодильник"
            st.rerun()

    with c4:
        if st.button("⏰ Скоро испортится", use_container_width=True, key="fast_expiring"):
            st.session_state["main_navigation"] = "Скоро испортится"
            st.rerun()

    c5, c6 = st.columns(2)

    with c5:
        if st.button("🗓️ Меню", use_container_width=True, key="fast_menu"):
            st.session_state["main_navigation"] = "Меню на неделю"
            st.rerun()

    with c6:
        if st.button("📊 Аналитика", use_container_width=True, key="fast_analytics"):
            st.session_state["main_navigation"] = "Аналитика"
            st.rerun()
'''


def patch_speed_helpers(text):
    if "def cached_fast_products(" in text:
        print("ℹ️ Speed helpers уже добавлены")
        return text

    marker = "def render_person_card(profile):"

    if marker not in text:
        print("⚠️ Не найден render_person_card для вставки Speed helpers")
        return text

    text = text.replace(marker, build_speed_helpers() + "\n\n" + marker, 1)
    print("✅ Добавлены Speed helper-функции")
    return text


def patch_sidebar_refresh(text):
    if 'render_speed_refresh_button("sidebar")' in text:
        print("ℹ️ Кнопка обновления в sidebar уже есть")
        return text

    marker = 'st.sidebar.caption(f"{APP_VERSION} · {DEVELOPER}")'

    if marker not in text:
        print("⚠️ Не найден sidebar.caption для вставки кнопки обновления")
        return text

    replacement = '''st.sidebar.caption(f"{APP_VERSION} · {DEVELOPER}")

render_speed_refresh_button("sidebar")'''

    text = text.replace(marker, replacement, 1)
    print("✅ Добавлена кнопка обновления данных в sidebar")
    return text


def build_fast_screen_page():
    return r'''

elif page == "Быстрый экран":
    st.header("📱 Быстрый экран")

    current_person = get_current_person()
    today_name = get_today_name_ru()

    render_page_intro(
        "Быстрый мобильный экран",
        "Самые нужные действия на одном экране: калории, меню на сегодня, холодильник, покупки и срочные продукты.",
        "📱"
    )

    render_current_datetime_card()

    render_speed_refresh_button("fast_screen_top")

    if current_person:
        st.markdown(f"""
        <div class="gradient-card">
            <h3>{get_person_emoji(current_person)} Активный пользователь: {current_person}</h3>
            <p>Сегодня: {today_name}. Быстрые действия будут удобнее для текущего пользователя.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("Активный пользователь не выбран.")

    render_fast_action_buttons()

    st.divider()

    st.subheader("🍽️ Калории сегодня")

    if current_person:
        render_fast_calorie_card(current_person)

        other_people = [person for person in PEOPLE if person != current_person]

        with st.expander("Показать второго пользователя"):
            for person in other_people:
                render_fast_calorie_card(person)
    else:
        cols = st.columns(2)

        for index, person in enumerate(PEOPLE):
            with cols[index % 2]:
                render_fast_calorie_card(person)

    st.divider()

    st.subheader("⏰ Срочные продукты")

    try:
        fast_products = cached_fast_products()
        urgent_products = get_urgent_products_for_fast_screen(fast_products)

        if not urgent_products:
            st.success("Срочных продуктов нет.")
        else:
            for product, status_text, status_color in urgent_products[:5]:
                badge = "badge-red" if status_color == "red" else "badge-yellow"

                st.markdown(f"""
                <div class="card">
                    <h3>{product[1]}</h3>
                    <p><b>{product[2]}</b> {product[3]} · {product[5] or "Без категории"}</p>
                    <span class="{badge}">{status_text}</span>
                </div>
                """, unsafe_allow_html=True)

            if len(urgent_products) > 5:
                st.caption(f"Ещё продуктов требуют внимания: {len(urgent_products) - 5}")

    except Exception as e:
        st.error(f"Не удалось загрузить срочные продукты: {e}")

    st.divider()

    st.subheader("🗓️ Меню на сегодня")

    try:
        fast_products = cached_fast_products()

        people_to_show = [current_person] if current_person else PEOPLE

        for person in people_to_show:
            if not person:
                continue

            menu_data = build_personal_week_menu(person, fast_products)

            if not menu_data:
                st.warning(f"Не удалось построить меню для {person}.")
                continue

            day_plan = next(
                (day for day in menu_data["week"] if day["day"] == today_name),
                None
            )

            if not day_plan:
                st.info(f"На сегодня нет плана для {person}.")
                continue

            st.markdown(f"""
            <div class="menu-day-card">
                <h3>{get_person_emoji(person)} Сегодня для {get_person_genitive(person)}</h3>
                <span class="status-pill pill-blue">Итого: {day_plan["calories"]} ккал</span>
                <span class="status-pill pill-gray">Цель: {day_plan["target_calories"]} ккал</span>
                <span class="status-pill pill-green">{day_plan["status"]}</span>
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

    except Exception as e:
        st.error(f"Не удалось построить меню на сегодня: {e}")

    st.divider()

    st.caption(
        "Быстрый экран использует кэш на несколько секунд, чтобы приложение быстрее открывалось на телефоне. "
        "Если данные не обновились сразу — нажмите «Обновить данные»."
    )
'''


def patch_fast_screen_page(text):
    if 'elif page == "Быстрый экран":' in text:
        print("ℹ️ Страница Быстрый экран уже добавлена")
        return text

    # Вставляем перед Главной, если возможно
    marker = 'if page == "Главная":'

    if marker not in text:
        print("⚠️ Не найден if page == Главная для вставки Быстрого экрана")
        return text

    text = text.replace(marker, build_fast_screen_page() + "\n\n" + marker, 1)
    print("✅ Добавлена страница Быстрый экран")
    return text


def patch_bootstrap_cache_ttl(text):
    """
    Если bootstrap_database_once уже есть, оставляем.
    Если нет — не трогаем, потому что v1.1.2 уже должен был добавить.
    """
    if "bootstrap_database_once()" in text:
        print("✅ Bootstrap БД уже кэшируется")
    else:
        print("ℹ️ Bootstrap cache не найден. Это не критично, но v1.1.2 желательно установить.")
    return text


def patch_app():
    if not APP_FILE.exists():
        print("❌ app.py не найден.")
        return False

    text = APP_FILE.read_text(encoding="utf-8")

    text = patch_login_default_page(text)
    text = patch_nav(text)
    text = patch_speed_helpers(text)
    text = patch_sidebar_refresh(text)
    text = patch_fast_screen_page(text)
    text = patch_bootstrap_cache_ttl(text)

    APP_FILE.write_text(text, encoding="utf-8")
    print("✅ app.py обновлён до v1.2")
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

    commit = run('git commit -m "v1.2 speed edition fast mobile screen"', check=False)

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
        print('git commit -m "v1.2 speed edition fast mobile screen"')
        print("git push")


def main():
    print("====================================")
    print(" v1.2 Speed Edition")
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
        print("✅ v1.2 Speed Edition установлен.")
        git_commit_push()
        print("\nЧто делать дальше:")
        print("1. Локально: python -m streamlit run app.py")
        print("2. В облаке дождаться обновления или нажать Reboot app.")
        print("3. Войти по PIN.")
        print("4. Должен открыться 📱 Быстрый экран.")
    else:
        print("⚠️ Есть ошибки синтаксиса. Пришли текст ошибки, я поправлю.")


if __name__ == "__main__":
    main()