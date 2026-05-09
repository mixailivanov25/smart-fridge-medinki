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
    backup_dir = PROJECT_DIR / f"backup_before_v11_auth_{timestamp}"
    backup_dir.mkdir(exist_ok=True)

    for file_path in [APP_FILE, SETTINGS_FILE]:
        if file_path.exists():
            shutil.copy2(file_path, backup_dir / file_path.name)

    print(f"📦 Резервная копия создана: {backup_dir.name}")
    return backup_dir


def update_settings():
    if not SETTINGS_FILE.exists():
        print("❌ settings.py не найден.")
        return False

    text = SETTINGS_FILE.read_text(encoding="utf-8")

    if "APP_VERSION" in text:
        text = re.sub(r'APP_VERSION\s*=\s*"[^"]+"', 'APP_VERSION = "v1.1"', text)
    else:
        text += '\nAPP_VERSION = "v1.1"\n'

    if "DEFAULT_AUTH_PINS" not in text:
        text += r'''

# v1.1 Auth defaults
# Важно: для облака лучше задать PIN-коды в Streamlit Secrets.
DEFAULT_AUTH_PINS = {
    "Мишка": "1111",
    "Мединка": "2222"
}
'''

    SETTINGS_FILE.write_text(text, encoding="utf-8")
    print("✅ settings.py обновлён до v1.1")
    return True


def patch_settings_import(text):
    old = "from settings import APP_NAME, APP_VERSION, DEVELOPER, PEOPLE, NUTRITION_GOALS, APP_TAGLINE"

    new = "from settings import APP_NAME, APP_VERSION, DEVELOPER, PEOPLE, NUTRITION_GOALS, APP_TAGLINE, DEFAULT_AUTH_PINS"

    if new in text:
        print("ℹ️ Импорт DEFAULT_AUTH_PINS уже есть")
        return text

    if old in text:
        text = text.replace(old, new, 1)
        print("✅ Добавлен импорт DEFAULT_AUTH_PINS")
    else:
        print("⚠️ Не найден стандартный импорт settings. Пробую мягкую вставку.")
        if "DEFAULT_AUTH_PINS" not in text:
            text = text.replace(
                "from settings import ",
                "from settings import DEFAULT_AUTH_PINS, ",
                1
            )

    return text


def build_auth_helpers():
    return r'''

# -----------------------------
# v1.1 Auth & Family Mode
# -----------------------------
def get_auth_pins():
    """
    PIN-коды можно задать в Streamlit Secrets:
    AUTH_PIN_MISHKA = "1234"
    AUTH_PIN_MEDINKA = "5678"

    Если secrets не заданы, используются DEFAULT_AUTH_PINS из settings.py.
    """
    pins = dict(DEFAULT_AUTH_PINS)

    try:
        if "AUTH_PIN_MISHKA" in st.secrets:
            pins["Мишка"] = str(st.secrets["AUTH_PIN_MISHKA"])

        if "AUTH_PIN_MEDINKA" in st.secrets:
            pins["Мединка"] = str(st.secrets["AUTH_PIN_MEDINKA"])
    except Exception:
        pass

    return pins


def is_authenticated():
    return bool(st.session_state.get("auth_ok", False))


def get_current_person():
    return st.session_state.get("current_person", "")


def logout_user():
    st.session_state["auth_ok"] = False
    st.session_state["current_person"] = ""
    st.session_state["main_navigation"] = "Главная"


def render_login_screen():
    st.markdown(f"<div class='app-title'>🥦 {APP_NAME}</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='app-subtitle'>Семейный вход в холодильник Мединки</div>",
        unsafe_allow_html=True
    )

    st.markdown("""
    <div class="gradient-card">
        <h3>🔐 Вход в приложение</h3>
        <p>
            Приложение опубликовано в интернете, поэтому мы добавили простой PIN-код,
            чтобы данные холодильника, покупок и дневника не меняли случайные люди.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="soft-card">
        <h3>👨‍👩‍👧 Кто входит?</h3>
        <p class="muted">Выберите пользователя и введите PIN-код.</p>
    </div>
    """, unsafe_allow_html=True)

    pins = get_auth_pins()

    with st.form("login_form"):
        person = st.selectbox("Пользователь", PEOPLE)
        pin = st.text_input("PIN-код", type="password", placeholder="Введите PIN")

        submitted = st.form_submit_button("🔓 Войти")

        if submitted:
            expected_pin = str(pins.get(person, ""))

            if pin and pin == expected_pin:
                st.session_state["auth_ok"] = True
                st.session_state["current_person"] = person
                st.session_state["main_navigation"] = "Главная"
                st.success(f"Добро пожаловать, {person}!")
                st.rerun()
            else:
                st.error("Неверный PIN-код.")

    with st.expander("ℹ️ Подсказка для первого входа"):
        st.write(
            "Если вы ещё не меняли PIN-коды, временные значения: "
            "Мишка — 1111, Мединка — 2222. "
            "После проверки лучше заменить их в Streamlit Cloud Secrets."
        )


def require_auth():
    if not is_authenticated():
        render_login_screen()
        st.stop()


def render_current_user_sidebar():
    current_person = get_current_person()

    if current_person:
        st.sidebar.success(f"{get_person_emoji(current_person)} Вы вошли как: {current_person}")

        if st.sidebar.button("🚪 Выйти"):
            logout_user()
            st.rerun()
'''


def patch_auth_helpers(text):
    if "def get_auth_pins(" in text:
        print("ℹ️ Auth helpers уже есть")
        return text

    marker = "def render_person_card(profile):"

    if marker not in text:
        print("⚠️ Не найден render_person_card для вставки auth helpers.")
        return text

    text = text.replace(marker, build_auth_helpers() + "\n\n" + marker, 1)
    print("✅ Добавлены функции авторизации")
    return text


def patch_require_auth_call(text):
    if "require_auth()" in text and "# v1.1 auth gate" in text:
        print("ℹ️ Auth gate уже добавлен")
        return text

    marker = 'st.sidebar.markdown(f"## 🥦 {APP_NAME}")'

    if marker not in text:
        print("⚠️ Не найдено место перед sidebar для auth gate.")
        return text

    insert = '''# v1.1 auth gate
require_auth()

'''

    text = text.replace(marker, insert + marker, 1)
    print("✅ Добавлен auth gate перед интерфейсом")
    return text


def patch_sidebar_user(text):
    if "render_current_user_sidebar()" in text:
        print("ℹ️ Текущий пользователь уже выводится в sidebar")
        return text

    marker = '''st.sidebar.divider()'''

    if marker not in text:
        print("⚠️ Не найден st.sidebar.divider для вставки пользователя.")
        return text

    replacement = '''render_current_user_sidebar()

st.sidebar.divider()'''

    text = text.replace(marker, replacement, 1)
    print("✅ Добавлен текущий пользователь в sidebar")
    return text


def patch_nav(text):
    if '"Семейный режим": "👨‍👩‍👧 Семейный режим"' in text:
        print("ℹ️ Семейный режим уже есть в навигации")
        return text

    marker = '''    "Главная": "🏠 Главная",'''

    if marker not in text:
        print("⚠️ Не найдено место для Семейного режима в nav_labels.")
        return text

    replacement = '''    "Главная": "🏠 Главная",
    "Семейный режим": "👨‍👩‍👧 Семейный режим",'''

    text = text.replace(marker, replacement, 1)
    print("✅ Добавлен пункт Семейный режим")
    return text


def build_family_page():
    return r'''

elif page == "Семейный режим":
    st.header("👨‍👩‍👧 Семейный режим")

    render_page_intro(
        "Пользователи холодильника Мединки",
        "Здесь видно, кто сейчас вошёл в приложение, можно переключить пользователя и посмотреть настройки Мишки и Мединки.",
        "👨‍👩‍👧"
    )

    current_person = get_current_person()

    if current_person:
        st.markdown(f"""
        <div class="gradient-card">
            <h3>{get_person_emoji(current_person)} Сейчас активен: {current_person}</h3>
            <p>
                Быстрые действия, дневник питания и любимые блюда можно вести от имени выбранного пользователя.
            </p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.warning("Пользователь не выбран.")

    st.subheader("👥 Профили")

    profiles = get_user_profiles()

    if profiles:
        cols = st.columns(2)

        for index, profile in enumerate(profiles):
            with cols[index % 2]:
                render_person_card(profile)

    st.divider()

    st.subheader("🔄 Переключить пользователя")

    st.info("Для переключения нужно ввести PIN нового пользователя.")

    pins = get_auth_pins()

    with st.form("switch_user_form"):
        new_person = st.selectbox("Кто будет пользоваться?", PEOPLE, key="switch_user_person")
        new_pin = st.text_input("PIN-код", type="password", key="switch_user_pin")

        submitted = st.form_submit_button("🔄 Переключиться")

        if submitted:
            expected_pin = str(pins.get(new_person, ""))

            if new_pin and new_pin == expected_pin:
                st.session_state["auth_ok"] = True
                st.session_state["current_person"] = new_person
                st.success(f"Теперь активен пользователь: {new_person}")
                st.rerun()
            else:
                st.error("Неверный PIN-код.")

    st.divider()

    st.subheader("🔐 Безопасность")

    st.markdown("""
    <div class="soft-card">
        <h3>Как поменять PIN-коды?</h3>
        <p>
            Откройте Streamlit Cloud → Manage app → Settings → Secrets
            и добавьте свои значения:
        </p>
        <pre>
AUTH_PIN_MISHKA = "ваш_PIN_для_Мишки"
AUTH_PIN_MEDINKA = "ваш_PIN_для_Мединки"
        </pre>
        <p class="muted">
            После сохранения secrets нужно перезапустить приложение через Reboot.
        </p>
    </div>
    """, unsafe_allow_html=True)
'''


def patch_family_page(text):
    if 'elif page == "Семейный режим":' in text:
        print("ℹ️ Страница Семейный режим уже есть")
        return text

    marker = 'elif page == "Сегодня":'

    if marker not in text:
        marker = 'elif page == "Мой холодильник":'

    if marker not in text:
        print("⚠️ Не найдено место для вставки страницы Семейный режим.")
        return text

    text = text.replace(marker, build_family_page() + "\n\n" + marker, 1)
    print("✅ Добавлена страница Семейный режим")
    return text


def patch_quick_actions_person_awareness(text):
    """
    Мягко улучшаем надпись быстрых действий, если функция есть.
    """
    if "Активный пользователь" in text:
        print("ℹ️ Быстрые действия уже знают активного пользователя")
        return text

    marker = '''def render_quick_actions():
    st.subheader("⚡ Быстрые действия")'''

    if marker not in text:
        print("ℹ️ render_quick_actions не найден или уже изменён")
        return text

    replacement = '''def render_quick_actions():
    current_person = get_current_person()
    if current_person:
        st.subheader(f"⚡ Быстрые действия · Активный пользователь: {current_person}")
    else:
        st.subheader("⚡ Быстрые действия")'''

    text = text.replace(marker, replacement, 1)
    print("✅ Быстрые действия учитывают активного пользователя")
    return text


def patch_app():
    if not APP_FILE.exists():
        print("❌ app.py не найден.")
        return False

    text = APP_FILE.read_text(encoding="utf-8")

    text = patch_settings_import(text)
    text = patch_auth_helpers(text)
    text = patch_require_auth_call(text)
    text = patch_sidebar_user(text)
    text = patch_nav(text)
    text = patch_family_page(text)
    text = patch_quick_actions_person_awareness(text)

    APP_FILE.write_text(text, encoding="utf-8")
    print("✅ app.py обновлён до v1.1")
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

    commit = run('git commit -m "v1.1 auth and family mode"', check=False)

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
        print('git commit -m "v1.1 auth and family mode"')
        print("git push")


def print_next_steps():
    print("\n==============================")
    print("Что сделать после обновления")
    print("==============================")

    print("""
1. Запусти локально:
   python -m streamlit run app.py

2. Проверь вход:
   Мишка   → PIN 1111
   Мединка → PIN 2222

3. Потом лучше поменять PIN-коды в Streamlit Cloud:
   Manage app → Settings → Secrets

   Добавь:

   AUTH_PIN_MISHKA = "твой_PIN_для_Мишки"
   AUTH_PIN_MEDINKA = "твой_PIN_для_Мединки"

4. Нажми Save.

5. Нажми Reboot app.

6. После обновления приложение будет требовать PIN при входе.
""")


def main():
    print("====================================")
    print(" v1.1 Auth & Family Mode")
    print(" Умный холодильник Мединки")
    print("====================================\n")

    if not APP_FILE.exists():
        print("❌ app.py не найден.")
        return

    if not SETTINGS_FILE.exists():
        print("❌ settings.py не найден.")
        return

    backup_files()

    if not update_settings():
        return

    if not patch_app():
        return

    ok = compile_files()

    print("\n==============================")

    if ok:
        print("✅ v1.1 Auth & Family Mode установлен.")
        git_commit_push()
        print_next_steps()
    else:
        print("⚠️ Есть ошибки синтаксиса. Пришли текст ошибки, я поправлю.")


if __name__ == "__main__":
    main()