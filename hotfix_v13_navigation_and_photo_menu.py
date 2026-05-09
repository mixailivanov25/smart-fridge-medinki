from pathlib import Path
import re
import shutil
import py_compile
from datetime import datetime

ROOT = Path(__file__).parent.resolve()
APP = ROOT / "app.py"

PHOTO_PAGE = "📸 Фото и сканер"


def backup_file(path: Path):
    if not path.exists():
        return None

    backup_dir = ROOT / "backups" / f"hotfix_v13_navigation_photo_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    backup_dir.mkdir(parents=True, exist_ok=True)
    backup_path = backup_dir / path.name
    shutil.copy2(path, backup_path)
    print(f"Backup saved: {backup_path}")
    return backup_path


def try_compile(path: Path):
    try:
        py_compile.compile(str(path), doraise=True)
        return True, None
    except py_compile.PyCompileError as e:
        return False, e


def ensure_import(text: str) -> str:
    if "from media_page import render_media_page" in text:
        return text

    if re.search(r"^import streamlit as st\s*$", text, flags=re.MULTILINE):
        text = re.sub(
            r"^import streamlit as st\s*$",
            "import streamlit as st\nfrom media_page import render_media_page",
            text,
            count=1,
            flags=re.MULTILINE,
        )
        print("Added import: render_media_page")
        return text

    text = "from media_page import render_media_page\n" + text
    print("Added import at file top: render_media_page")
    return text


def ensure_request_navigation_helper(text: str) -> str:
    if "def request_navigation(" in text:
        return text

    helper = r'''

def request_navigation(target_page: str):
    """
    Безопасный переход между разделами.

    Streamlit запрещает менять st.session_state["main_navigation"]
    после создания виджета меню с key="main_navigation".
    Поэтому быстрые кнопки пишут желаемую страницу в pending_navigation,
    а перед созданием меню это значение применяется.
    """
    st.session_state["pending_navigation"] = target_page
    st.rerun()
'''

    # Вставляем после импортов.
    lines = text.splitlines()
    insert_idx = 0

    for i, line in enumerate(lines):
        stripped = line.strip()

        if stripped.startswith("import ") or stripped.startswith("from "):
            insert_idx = i + 1
            continue

        if stripped == "":
            continue

        break

    lines.insert(insert_idx, helper)
    print("Added request_navigation() helper")
    return "\n".join(lines) + "\n"


def patch_fast_action_buttons(text: str) -> str:
    """
    Меняем внутри render_fast_action_buttons прямые присваивания:

        st.session_state["main_navigation"] = "..."

    на:

        request_navigation("...")

    Это убирает ошибку StreamlitAPIException.
    """

    func_match = re.search(
        r"(?ms)^def\s+render_fast_action_buttons\s*\([^)]*\)\s*:\n.*?(?=^def\s+|\Z)",
        text,
    )

    if not func_match:
        print("WARNING: render_fast_action_buttons() not found. Skipping fast button patch.")
        return text

    block = func_match.group(0)
    old_block = block

    pattern = r'(?m)^(\s*)st\.session_state\[\s*["\']main_navigation["\']\s*\]\s*=\s*(.+?)\s*$'

    def repl(m):
        indent = m.group(1)
        target = m.group(2).strip()
        return f"{indent}request_navigation({target})"

    block = re.sub(pattern, repl, block)

    if block != old_block:
        text = text[:func_match.start()] + block + text[func_match.end():]
        print("Patched direct main_navigation assignments inside render_fast_action_buttons()")
    else:
        print("No direct main_navigation assignments found inside render_fast_action_buttons()")

    return text


def find_widget_statement_start(lines, key_line_idx):
    """
    Ищем начало вызова виджета, где используется key="main_navigation".
    Например:

        page = st.sidebar.radio(
            ...
            key="main_navigation"
        )

    Нужно вставить pending-navigation блок ДО строки page = st.sidebar.radio(...),
    а не перед самой строкой key=...
    """
    widget_markers = [
        "st.sidebar.radio",
        "st.sidebar.selectbox",
        "st.radio",
        "st.selectbox",
        "option_menu",
    ]

    for i in range(key_line_idx, max(-1, key_line_idx - 30), -1):
        line = lines[i]
        if any(marker in line for marker in widget_markers):
            return i

    return key_line_idx


def ensure_pending_navigation_applied_before_widget(text: str) -> str:
    if 'pending_navigation" in st.session_state' in text or "pending_navigation' in st.session_state" in text:
        return text

    lines = text.splitlines()

    key_idx = None
    for i, line in enumerate(lines):
        if "main_navigation" in line and "key" in line:
            key_idx = i
            break

    if key_idx is None:
        print("WARNING: main_navigation widget key not found. Could not insert pending navigation block.")
        return text

    start_idx = find_widget_statement_start(lines, key_idx)
    indent = re.match(r"\s*", lines[start_idx]).group(0)

    block = [
        f'{indent}# Применяем переходы от быстрых кнопок ДО создания виджета меню.',
        f'{indent}if "pending_navigation" in st.session_state:',
        f'{indent}    st.session_state["main_navigation"] = st.session_state.pop("pending_navigation")',
        "",
    ]

    lines[start_idx:start_idx] = block
    print("Inserted pending_navigation block before main_navigation widget")
    return "\n".join(lines) + "\n"


def remove_broken_photo_lines(text: str) -> str:
    """
    Удаляем одиночные неправильные строки, которые могли попасть в словари/не туда.
    Потом ниже добавим пункт правильно.
    """
    lines = text.splitlines()
    new_lines = []
    removed = 0

    for line in lines:
        stripped = line.strip()
        if stripped in [
            '"📸 Фото и сканер",',
            "'📸 Фото и сканер',",
            '"📸 Фото и сканер"',
            "'📸 Фото и сканер'",
        ]:
            removed += 1
            continue
        new_lines.append(line)

    if removed:
        print(f"Removed broken standalone photo menu lines: {removed}")

    return "\n".join(new_lines) + "\n"


def find_matching(text: str, start_idx: int, open_ch: str, close_ch: str):
    depth = 0
    in_str = None
    escape = False

    for i in range(start_idx, len(text)):
        ch = text[i]

        if in_str:
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == in_str:
                in_str = None
            continue

        if ch in ("'", '"'):
            in_str = ch
            continue

        if ch == open_ch:
            depth += 1
        elif ch == close_ch:
            depth -= 1
            if depth == 0:
                return i

    return -1


def looks_like_page_container(block: str) -> bool:
    markers = [
        "Быстрый экран",
        "Главная",
        "Дневник",
        "Холодильник",
        "Рецепты",
        "Меню",
        "Аналитика",
        "Демо",
    ]
    count = sum(1 for m in markers if m in block)
    return count >= 2


def add_photo_to_list_container(text: str) -> tuple[str, bool]:
    """
    Добавляет "📸 Фото и сканер" в список страниц.
    """
    quick_markers = [
        '"📱 Быстрый экран"',
        "'📱 Быстрый экран'",
        '"Быстрый экран"',
        "'Быстрый экран'",
    ]

    for marker in quick_markers:
        search_from = 0

        while True:
            idx = text.find(marker, search_from)
            if idx == -1:
                break

            search_from = idx + len(marker)

            list_start = text.rfind("[", 0, idx)
            dict_start = text.rfind("{", 0, idx)

            if list_start == -1:
                continue

            # Если ближайший контейнер — словарь, это не список.
            if dict_start > list_start:
                continue

            list_end = find_matching(text, list_start, "[", "]")
            if list_end == -1 or not (list_start < idx < list_end):
                continue

            block = text[list_start:list_end + 1]

            if PHOTO_PAGE in block:
                return text, True

            if not looks_like_page_container(block):
                continue

            line_start = text.rfind("\n", 0, idx) + 1
            line_end = text.find("\n", idx)
            if line_end == -1:
                line_end = idx + len(marker)

            line = text[line_start:line_end]
            indent = re.match(r"\s*", line).group(0)

            insertion = f'\n{indent}"{PHOTO_PAGE}",'
            text = text[:line_end] + insertion + text[line_end:]

            print("Added photo page to list-style menu")
            return text, True

    return text, False


def extract_dict_value_for_key(block: str, key_variants: list[str]) -> str:
    """
    Пытаемся взять тип значения у существующего пункта меню.
    Например:
        "📱 Быстрый экран": "📱",
    Тогда для фото добавим:
        "📸 Фото и сканер": "📸",
    """
    for key in key_variants:
        # Ищем значение до запятой на этой же строке.
        pattern = rf'(["\']{re.escape(key)}["\']\s*:\s*)(.+?)(,?\s*$)'
        m = re.search(pattern, block, flags=re.MULTILINE)
        if m:
            value = m.group(2).strip()

            # Если это простой string — заменим на иконку.
            if re.match(r'''^["'].*["']$''', value):
                return '"📸"'

            # Если это dict — попробуем сделать похожий dict.
            if value.startswith("{") and value.endswith("}"):
                return value

            # Если это функция/непонятное значение — лучше безопасная строка.
            return '"📸"'

    return '"📸"'


def add_photo_to_dict_container(text: str) -> tuple[str, bool]:
    """
    Добавляет "📸 Фото и сканер": "📸" в словарь страниц,
    если меню построено через dict.keys().
    """
    quick_markers = [
        '"📱 Быстрый экран"',
        "'📱 Быстрый экран'",
        '"Быстрый экран"',
        "'Быстрый экран'",
    ]

    key_names = [
        "📱 Быстрый экран",
        "Быстрый экран",
    ]

    for marker in quick_markers:
        search_from = 0

        while True:
            idx = text.find(marker, search_from)
            if idx == -1:
                break

            search_from = idx + len(marker)

            dict_start = text.rfind("{", 0, idx)
            list_start = text.rfind("[", 0, idx)

            if dict_start == -1:
                continue

            # Нужен именно словарь.
            if list_start > dict_start:
                continue

            dict_end = find_matching(text, dict_start, "{", "}")
            if dict_end == -1 or not (dict_start < idx < dict_end):
                continue

            block = text[dict_start:dict_end + 1]

            if PHOTO_PAGE in block:
                return text, True

            if not looks_like_page_container(block):
                continue

            # Убедимся, что это реально словарь: у строки с быстрым экраном есть двоеточие.
            quick_line_match = re.search(
                r'(?m)^(\s*)(["\'](?:📱\s*)?Быстрый экран["\']\s*:\s*.+?,?\s*)$',
                block,
            )

            if not quick_line_match:
                continue

            line_indent = quick_line_match.group(1)
            line_end_in_block = quick_line_match.end(2)
            insert_pos = dict_start + quick_line_match.end(0)

            value = extract_dict_value_for_key(block, key_names)

            insertion = f'\n{line_indent}"{PHOTO_PAGE}": {value},'

            text = text[:insert_pos] + insertion + text[insert_pos:]

            print("Added photo page to dict-style menu")
            return text, True

    return text, False


def ensure_photo_menu_item(text: str) -> str:
    if PHOTO_PAGE in text:
        # Может быть только в роутинге/импорте, но не в меню.
        # Всё равно попробуем проверить контейнеры. Сначала удалим плохие одиночные строки.
        pass

    text = remove_broken_photo_lines(text)

    text, ok_list = add_photo_to_list_container(text)
    if ok_list:
        return text

    text, ok_dict = add_photo_to_dict_container(text)
    if ok_dict:
        return text

    print("WARNING: Could not safely add photo page to sidebar menu.")
    print("If menu still does not show it, send app.py lines around the navigation block.")
    return text


def ensure_photo_route(text: str) -> str:
    if "render_media_page()" in text:
        return text

    route = 'elif page in ("📸 Фото и сканер", "Фото и сканер"):\n{indent}    render_media_page()\n'

    # Ищем место перед Главной или любым elif page == ...
    patterns = [
        r'(?m)^(\s*)elif\s+page\s*==\s*["\']🏠\s*Главная["\']\s*:',
        r'(?m)^(\s*)elif\s+page\s*==\s*["\']Главная["\']\s*:',
        r'(?m)^(\s*)elif\s+page\s*==\s*["\'][^"\']+["\']\s*:',
    ]

    for pattern in patterns:
        m = re.search(pattern, text)
        if m:
            indent = m.group(1)
            new_route = f'{indent}elif page in ("📸 Фото и сканер", "Фото и сканер"):\n{indent}    render_media_page()\n'
            text = text[:m.start()] + new_route + text[m.start():]
            print("Added photo page route")
            return text

    print("WARNING: Could not add photo page route automatically.")
    return text


def main():
    if not APP.exists():
        print("app.py not found")
        return

    print("=== hotfix_v13_navigation_and_photo_menu.py ===")
    backup_file(APP)

    text = APP.read_text(encoding="utf-8")

    text = ensure_import(text)
    text = ensure_request_navigation_helper(text)

    # Сначала исправляем быстрые кнопки.
    text = patch_fast_action_buttons(text)

    # Затем добавляем безопасное применение pending_navigation перед созданием меню.
    text = ensure_pending_navigation_applied_before_widget(text)

    # Добавляем пункт меню и роут страницы.
    text = ensure_photo_menu_item(text)
    text = ensure_photo_route(text)

    APP.write_text(text, encoding="utf-8")

    ok, err = try_compile(APP)

    if ok:
        print()
        print("Готово ✅")
        print("Исправлено:")
        print("- быстрые кнопки больше не меняют main_navigation напрямую")
        print("- pending_navigation применяется до создания виджета меню")
        print("- добавлен/проверен импорт render_media_page")
        print("- добавлен/проверен пункт меню 📸 Фото и сканер")
        print("- добавлен/проверен роут страницы")
        print()
        print("Теперь запусти:")
        print("python -m streamlit run app.py")
    else:
        print()
        print("Синтаксис всё ещё сломан ❌")
        print(err)
        print()
        print("Пришли, пожалуйста, кусок app.py примерно строки 960-1020 и 1180-1280.")


if __name__ == "__main__":
    main()