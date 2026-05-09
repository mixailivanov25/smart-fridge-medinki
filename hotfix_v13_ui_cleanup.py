from pathlib import Path
import re
import shutil
import py_compile
from datetime import datetime

ROOT = Path(__file__).parent.resolve()
APP = ROOT / "app.py"
UI_FILE = ROOT / "ui_cleanup_v13.py"


REQUEST_NAVIGATION_CODE = r'''
def request_navigation(target_page: str):
    """
    Безопасный переход между разделами.

    Быстрые кнопки не должны напрямую менять main_navigation после создания
    виджета навигации. Поэтому:
    1. пишем pending_navigation;
    2. пытаемся перейти сразу, если это безопасно;
    3. делаем st.rerun().
    """
    aliases = {
        "Быстрый экран": "📱 Быстрый экран",
        "Главная": "🏠 Главная",
        "Семейный режим": "👨‍👩‍👧 Семейный режим",
        "Сегодня": "📅 Сегодня",
        "Дневник питания": "📔 Дневник питания",
        "Добавить еду": "📔 Дневник питания",
        "Умные покупки": "🛒 Умные покупки",
        "Добавить покупку": "🛒 Умные покупки",
        "Аналитика": "📊 Аналитика",
        "Стресс-тест": "🧪 Стресс-тест",
        "Мои рецепты": "📝 Мои рецепты",
        "Мой холодильник": "🧊 Мой холодильник",
        "Холодильник": "🧊 Мой холодильник",
        "Добавить продукты": "➕ Добавить продукты",
        "Рецепты": "🍳 Рецепты",
        "Каталог блюд": "🍽️ Каталог блюд",
        "Меню": "🗓️ Меню на неделю",
        "Меню на неделю": "🗓️ Меню на неделю",
        "Список покупок": "🛒 Список покупок",
        "Питание и цели": "🎯 Питание и цели",
        "Любимые блюда": "❤️ Любимые блюда",
        "История": "📜 История",
        "Списания": "📉 Списания",
        "Демо-режим": "🧪 Демо-режим",
        "Скоро испортится": "⏰ Скоро испортится",
        "Фото и сканер": "📸 Фото и сканер",
        "Фото": "📸 Фото и сканер",
        "Сканер": "📸 Фото и сканер",
        "📸": "📸 Фото и сканер",
    }

    target_page = aliases.get(target_page, target_page)
    st.session_state["pending_navigation"] = target_page

    try:
        st.session_state["main_navigation"] = target_page
    except Exception:
        pass

    st.rerun()
'''


FAST_ACTIONS_CODE = r'''
def render_fast_action_buttons():
    """
    Быстрые действия для быстрого экрана.
    Все переходы идут через request_navigation().
    """
    st.markdown("## ⚡ Быстрые действия")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("➕ Добавить еду", key="fast_add_food_v13_fixed", use_container_width=True):
            request_navigation("📔 Дневник питания")

        if st.button("🧊 Холодильник", key="fast_fridge_v13_fixed", use_container_width=True):
            request_navigation("🧊 Мой холодильник")

        if st.button("🗓️ Меню", key="fast_menu_v13_fixed", use_container_width=True):
            request_navigation("🗓️ Меню на неделю")

        if st.button("📸 Фото и сканер", key="fast_photo_v13_fixed", use_container_width=True):
            request_navigation("📸 Фото и сканер")

    with col2:
        if st.button("🛒 Добавить покупку", key="fast_add_shopping_v13_fixed", use_container_width=True):
            request_navigation("🛒 Умные покупки")

        if st.button("⏰ Скоро испортится", key="fast_expiring_v13_fixed", use_container_width=True):
            request_navigation("⏰ Скоро испортится")

        if st.button("📊 Аналитика", key="fast_analytics_v13_fixed", use_container_width=True):
            request_navigation("📊 Аналитика")

        if st.button("🍳 Рецепты", key="fast_recipes_v13_fixed", use_container_width=True):
            request_navigation("🍳 Рецепты")
'''


def backup_file(path: Path):
    backup_dir = ROOT / "backups" / f"hotfix_v13_ui_cleanup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    backup_dir.mkdir(parents=True, exist_ok=True)
    backup_path = backup_dir / path.name
    if path.exists():
        shutil.copy2(path, backup_path)
        print(f"Backup saved: {backup_path}")


def try_compile(path: Path):
    try:
        py_compile.compile(str(path), doraise=True)
        return True, None
    except py_compile.PyCompileError as e:
        return False, e


def write_ui_cleanup_module():
    UI_FILE.write_text(
        r'''
import streamlit as st


def apply_ui_cleanup_v13():
    """
    Общая чистка интерфейса v1.3:
    - меньше обрезаний текста;
    - аккуратнее боковое меню;
    - скрытие лишних Streamlit-якорей;
    - более современный вид карточек и кнопок.
    """
    st.markdown(
        """
<style>
/* ===== Base layout ===== */

html, body, [data-testid="stAppViewContainer"] {
    background: #f6f8f7;
}

.block-container {
    padding-top: 1.8rem !important;
    padding-bottom: 3rem !important;
    max-width: 1320px !important;
}

/* Чтобы заголовки не обрезались */
h1, h2, h3 {
    line-height: 1.22 !important;
    overflow: visible !important;
    padding-bottom: 0.12em !important;
    color: #123321 !important;
}

/* Скрыть маленькие якоря-ссылки возле заголовков */
a[href^="#"] {
    display: none !important;
}

/* Скрыть кнопку Deploy и верхние лишние элементы Streamlit */
.stDeployButton {
    display: none !important;
}

[data-testid="stToolbar"] {
    display: none !important;
}

/* Скрыть кнопку сворачивания sidebar */
[data-testid="collapsedControl"] {
    display: none !important;
}

/* ===== Sidebar ===== */

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #f7fff9 0%, #ffffff 100%) !important;
    border-right: 1px solid rgba(18, 51, 33, 0.08);
}

[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    font-size: 1.15rem !important;
    line-height: 1.28 !important;
}

[data-testid="stSidebar"] .stButton > button {
    border-radius: 18px !important;
}

/* Радио-навигация аккуратнее */
[data-testid="stSidebar"] [role="radiogroup"] label {
    padding: 8px 10px !important;
    border-radius: 14px !important;
    margin-bottom: 4px !important;
    transition: all .16s ease;
}

[data-testid="stSidebar"] [role="radiogroup"] label:hover {
    background: rgba(34, 197, 94, 0.10) !important;
}

/* ===== Buttons ===== */

div.stButton > button {
    border-radius: 18px !important;
    min-height: 46px !important;
    font-weight: 700 !important;
    border: 1px solid rgba(18, 51, 33, 0.12) !important;
    box-shadow: 0 8px 20px rgba(15, 23, 42, 0.06);
    transition: transform .15s ease, box-shadow .15s ease, background .15s ease;
}

div.stButton > button:hover {
    transform: translateY(-1px);
    box-shadow: 0 12px 26px rgba(15, 23, 42, 0.10);
}

/* ===== Cards / expanders ===== */

[data-testid="stExpander"] {
    border-radius: 20px !important;
    overflow: hidden !important;
}

.stForm {
    border-radius: 22px !important;
}

/* ===== Inputs ===== */

input, textarea, select {
    border-radius: 16px !important;
}

/* ===== Mobile ===== */

@media (max-width: 760px) {
    .block-container {
        padding-top: 1.1rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }

    h1 {
        font-size: 2.0rem !important;
    }

    h2 {
        font-size: 1.55rem !important;
    }

    h3 {
        font-size: 1.28rem !important;
    }

    div.stButton > button {
        min-height: 50px !important;
        font-size: 1rem !important;
    }

    [data-testid="stSidebar"] {
        min-width: 300px !important;
        max-width: 320px !important;
    }
}
</style>
        """,
        unsafe_allow_html=True,
    )
'''.strip() + "\n",
        encoding="utf-8",
    )
    print("Written ui_cleanup_v13.py")


def find_safe_insert_after_imports(text: str) -> int:
    lines = text.splitlines()
    insert_idx = 0
    depth = 0
    in_imports = False

    def delta(line):
        cleaned = re.sub(r'".*?"', '""', line)
        cleaned = re.sub(r"'.*?'", "''", cleaned)
        return (
            cleaned.count("(")
            + cleaned.count("[")
            + cleaned.count("{")
            - cleaned.count(")")
            - cleaned.count("]")
            - cleaned.count("}")
        )

    for i, line in enumerate(lines):
        stripped = line.strip()

        if not stripped or stripped.startswith("#"):
            if i == insert_idx:
                insert_idx = i + 1
            continue

        is_import = stripped.startswith("import ") or stripped.startswith("from ")

        if is_import and depth == 0:
            in_imports = True
            depth += delta(line)
            insert_idx = i + 1
            if depth <= 0:
                depth = 0
            continue

        if in_imports and depth > 0:
            depth += delta(line)
            insert_idx = i + 1
            if depth <= 0:
                depth = 0
            continue

        if is_import and depth == 0:
            insert_idx = i + 1
            continue

        break

    return insert_idx


def ensure_import_and_css_call(text: str) -> str:
    if "from ui_cleanup_v13 import apply_ui_cleanup_v13" not in text:
        lines = text.splitlines()
        insert_idx = find_safe_insert_after_imports(text)
        lines.insert(insert_idx, "from ui_cleanup_v13 import apply_ui_cleanup_v13")
        text = "\n".join(lines) + "\n"
        print("Added import apply_ui_cleanup_v13")

    if "apply_ui_cleanup_v13()" not in text:
        # Лучше вызвать сразу после st.set_page_config, если есть.
        m = re.search(r"st\.set_page_config\s*\((?s:.*?)\)\s*", text)
        if m:
            insert_pos = m.end()
            text = text[:insert_pos] + "\napply_ui_cleanup_v13()\n" + text[insert_pos:]
            print("Inserted apply_ui_cleanup_v13() after st.set_page_config")
        else:
            # Иначе после импортов.
            lines = text.splitlines()
            insert_idx = find_safe_insert_after_imports(text)
            lines.insert(insert_idx + 1, "apply_ui_cleanup_v13()")
            text = "\n".join(lines) + "\n"
            print("Inserted apply_ui_cleanup_v13() after imports")

    return text


def replace_request_navigation(text: str) -> str:
    pattern = r'\n*def\s+request_navigation\s*\([^)]*\)\s*:\n.*?^\s*st\.rerun\(\)\s*\n?'
    new_text, count = re.subn(
        pattern,
        "\n\n" + REQUEST_NAVIGATION_CODE.strip() + "\n\n",
        text,
        flags=re.MULTILINE | re.DOTALL,
    )

    if count:
        print(f"Replaced request_navigation(): {count}")
        return new_text

    lines = text.splitlines()
    insert_idx = find_safe_insert_after_imports(text)
    block = [""] + REQUEST_NAVIGATION_CODE.strip().splitlines() + [""]
    lines[insert_idx:insert_idx] = block
    print("Inserted request_navigation()")
    return "\n".join(lines) + "\n"


def replace_fast_actions(text: str) -> str:
    pattern = r'(?ms)^def\s+render_fast_action_buttons\s*\([^)]*\)\s*:\n.*?(?=^def\s+|\Z)'
    new_text, count = re.subn(pattern, FAST_ACTIONS_CODE.strip() + "\n\n", text)

    if count:
        print(f"Replaced render_fast_action_buttons(): {count}")
        return new_text

    # Если функции нет, добавим в конец.
    text += "\n\n" + FAST_ACTIONS_CODE.strip() + "\n"
    print("Added render_fast_action_buttons()")
    return text


def ensure_pending_navigation_before_widget(text: str) -> str:
    if '"pending_navigation" in st.session_state' in text or "'pending_navigation' in st.session_state" in text:
        return text

    lines = text.splitlines()
    key_idx = None

    for i, line in enumerate(lines):
        if "main_navigation" in line and "key" in line:
            key_idx = i
            break

    if key_idx is None:
        print("WARNING: navigation widget with key main_navigation not found")
        return text

    widget_markers = [
        "st.sidebar.radio",
        "st.sidebar.selectbox",
        "st.radio",
        "st.selectbox",
        "option_menu",
    ]

    start_idx = key_idx
    for i in range(key_idx, max(-1, key_idx - 50), -1):
        if any(marker in lines[i] for marker in widget_markers):
            start_idx = i
            break

    indent = re.match(r"\s*", lines[start_idx]).group(0)

    block = [
        f'{indent}# Применяем переходы от быстрых кнопок ДО создания виджета меню.',
        f'{indent}if "pending_navigation" in st.session_state:',
        f'{indent}    st.session_state["main_navigation"] = st.session_state.pop("pending_navigation")',
        "",
    ]

    lines[start_idx:start_idx] = block
    print("Inserted pending_navigation block before menu widget")
    return "\n".join(lines) + "\n"


def remove_indented_block_containing(text: str, needles: list[str], mode: str = "remove") -> str:
    """
    Удаляет или раскрывает блок, начинающийся со строки, содержащей одну из needles.
    mode:
    - remove: удалить строку и вложенный блок;
    - unwrap: удалить строку, а вложенный блок поднять на один уровень.
    """
    lines = text.splitlines()
    out = []
    i = 0
    changed = 0

    while i < len(lines):
        line = lines[i]
        if any(n in line for n in needles):
            base_indent = len(line) - len(line.lstrip(" "))
            j = i + 1

            block = []
            while j < len(lines):
                next_line = lines[j]
                stripped = next_line.strip()

                if not stripped:
                    block.append(next_line)
                    j += 1
                    continue

                next_indent = len(next_line) - len(next_line.lstrip(" "))
                if next_indent <= base_indent:
                    break

                block.append(next_line)
                j += 1

            if mode == "unwrap":
                for b in block:
                    if b.startswith(" " * 4):
                        out.append(b[4:])
                    else:
                        out.append(b)
                print(f"Unwrapped block containing: {needles}")
            else:
                print(f"Removed block containing: {needles}")

            changed += 1
            i = j
            continue

        out.append(line)
        i += 1

    if changed:
        return "\n".join(out) + "\n"

    return text


def remove_single_lines_containing(text: str, needles: list[str]) -> str:
    lines = text.splitlines()
    new_lines = []
    removed = 0

    for line in lines:
        if any(n in line for n in needles):
            removed += 1
            continue
        new_lines.append(line)

    if removed:
        print(f"Removed single lines containing {needles}: {removed}")

    return "\n".join(new_lines) + "\n"


def cleanup_texts(text: str) -> str:
    replacements = {
        "Быстрый мобильный экран": "Главное на сегодня",
        "Самые нужные действия на одном экране: калории, меню на сегодня, холодильник, покупки и срочные продукты.": "Калории, меню, покупки, холодильник и срочные продукты — всё в одном месте.",
        "Кто входит?": "Вход в приложение",
        "Выберите пользователя и введите PIN-код.": "Введите логин и PIN-код.",
        "Пользователь": "Логин",
        "Семейный вход в холодильник Мединки": "Семейный вход",
        "Приложение опубликовано в интернете, поэтому мы добавили простой PIN-код, чтобы данные холодильника, покупок и дневника не меняли случайные люди.": "Введите логин и PIN-код, чтобы открыть семейный холодильник.",
    }

    for old, new in replacements.items():
        if old in text:
            text = text.replace(old, new)
            print(f"Text replaced: {old} -> {new}")

    return text


def remove_refresh_buttons(text: str) -> str:
    return remove_indented_block_containing(
        text,
        [
            "Обновить данные",
            "🔄 Обновить данные",
        ],
        mode="remove",
    )


def remove_first_login_hint(text: str) -> str:
    text = remove_indented_block_containing(
        text,
        [
            "Подсказка для первого входа",
            "первого входа",
        ],
        mode="remove",
    )

    text = remove_single_lines_containing(
        text,
        [
            "1111",
            "2222",
            "временные значения",
            "Streamlit Cloud Secrets",
        ],
    )

    return text


def remove_sidebar_demo_and_phone_info(text: str) -> str:
    # Убрать блок кнопки демо из sidebar.
    text = remove_indented_block_containing(
        text,
        [
            "Быстро заполнить демо",
            "Быстро заполнить демо-данными",
            "демо-данными",
        ],
        mode="remove",
    )

    # Убрать строки про телефон.
    text = remove_single_lines_containing(
        text,
        [
            "Откройте ссылку на телефоне",
            "добавьте на главный экран",
            "главный экран",
            "телефоне",
        ],
    )

    return text


def unwrap_second_user_expander(text: str) -> str:
    return remove_indented_block_containing(
        text,
        [
            "Показать второго пользователя",
            "второго пользователя",
        ],
        mode="unwrap",
    )


def fix_photo_menu_dict_value(text: str) -> str:
    # Если пункт фото в словаре записан как значение-иконка, оставляем нормальную подпись.
    text = re.sub(
        r'(["\'])📸 Фото и сканер\1\s*:\s*(["\'])📸\2',
        r'"📸 Фото и сканер": "camera"',
        text,
    )

    # Если где-то оказался только значок как пункт.
    text = re.sub(
        r'(["\'])📸\1\s*,',
        r'"📸 Фото и сканер",',
        text,
    )

    return text


def ensure_photo_route(text: str) -> str:
    if "render_media_page()" in text:
        return text

    if "from media_page import render_media_page" not in text:
        lines = text.splitlines()
        insert_idx = find_safe_insert_after_imports(text)
        lines.insert(insert_idx, "from media_page import render_media_page")
        text = "\n".join(lines) + "\n"
        print("Added media_page import")

    patterns = [
        r'(?m)^(\s*)elif\s+page\s*==\s*["\']🏠\s*Главная["\']\s*:',
        r'(?m)^(\s*)elif\s+page\s*==\s*["\']Главная["\']\s*:',
        r'(?m)^(\s*)elif\s+page\s*==\s*["\'][^"\']+["\']\s*:',
    ]

    for pattern in patterns:
        m = re.search(pattern, text)
        if m:
            indent = m.group(1)
            route = (
                f'{indent}elif page in ("📸 Фото и сканер", "Фото и сканер", "📸"):\n'
                f'{indent}    render_media_page()\n'
            )
            text = text[:m.start()] + route + text[m.start():]
            print("Added photo scanner route")
            return text

    print("WARNING: could not add photo route")
    return text


def main():
    if not APP.exists():
        print("app.py not found")
        return

    print("=== hotfix_v13_ui_cleanup.py ===")

    backup_file(APP)
    write_ui_cleanup_module()

    text = APP.read_text(encoding="utf-8")

    text = ensure_import_and_css_call(text)
    text = replace_request_navigation(text)
    text = ensure_pending_navigation_before_widget(text)
    text = replace_fast_actions(text)

    text = cleanup_texts(text)
    text = remove_refresh_buttons(text)
    text = remove_first_login_hint(text)
    text = remove_sidebar_demo_and_phone_info(text)
    text = unwrap_second_user_expander(text)
    text = fix_photo_menu_dict_value(text)
    text = ensure_photo_route(text)

    APP.write_text(text, encoding="utf-8")

    ok, err = try_compile(APP)

    if ok:
        print()
        print("Готово ✅")
        print("Сделана чистка интерфейса v1.3.")
        print()
        print("Проверь:")
        print("1. экран входа;")
        print("2. быстрый экран;")
        print("3. быстрые кнопки;")
        print("4. боковое меню;")
        print("5. фото и сканер на компьютере и телефоне.")
        print()
        print("Запуск:")
        print("python -m streamlit run app.py")
    else:
        print()
        print("Синтаксис всё ещё сломан ❌")
        print(err)
        print()
        print("Пришли, пожалуйста:")
        print("- первые 80 строк app.py")
        print("- функцию render_fast_action_buttons")
        print("- блок авторизации")
        print("- блок sidebar/menu")


if __name__ == "__main__":
    main()