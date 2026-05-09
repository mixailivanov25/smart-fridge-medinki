from pathlib import Path
import re
import shutil
import py_compile
from datetime import datetime

ROOT = Path(__file__).parent.resolve()
APP = ROOT / "app.py"

PHOTO_PAGE = "📸 Фото и сканер"


REQUEST_NAVIGATION_CODE = r'''
def request_navigation(target_page: str):
    """
    Безопасный переход между разделами.

    Важно:
    - быстрые кнопки НЕ меняют main_navigation напрямую;
    - они пишут pending_navigation;
    - перед созданием виджета меню pending_navigation применяется.

    Также здесь есть алиасы: если кнопка просит "Дневник питания",
    а в меню страница называется "📔 Дневник питания", мы подставляем правильное имя.
    """
    aliases = {
        "Быстрый экран": "📱 Быстрый экран",
        "Главная": "🏠 Главная",
        "Семейный режим": "👨‍👩‍👧 Семейный режим",
        "Сегодня": "📅 Сегодня",
        "Дневник питания": "📔 Дневник питания",
        "Умные покупки": "🛒 Умные покупки",
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
    st.rerun()
'''


def backup_file(path: Path):
    backup_dir = ROOT / "backups" / f"hotfix_v13_buttons_photo_mobile_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    backup_dir.mkdir(parents=True, exist_ok=True)
    backup_path = backup_dir / path.name
    shutil.copy2(path, backup_path)
    print(f"Backup saved: {backup_path}")


def try_compile(path: Path):
    try:
        py_compile.compile(str(path), doraise=True)
        return True, None
    except py_compile.PyCompileError as e:
        return False, e


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


def ensure_media_import(text: str) -> str:
    if "from media_page import render_media_page" in text:
        return text

    lines = text.splitlines()

    for i, line in enumerate(lines):
        if line.strip() == "import streamlit as st":
            lines.insert(i + 1, "from media_page import render_media_page")
            print("Added media_page import after streamlit import.")
            return "\n".join(lines) + "\n"

    insert_idx = find_safe_insert_after_imports(text)
    lines.insert(insert_idx, "from media_page import render_media_page")
    print("Added media_page import after imports.")
    return "\n".join(lines) + "\n"


def replace_request_navigation(text: str) -> str:
    pattern = r'\n*def\s+request_navigation\s*\([^)]*\)\s*:\n.*?^\s*st\.rerun\(\)\s*\n?'
    text, count = re.subn(
        pattern,
        "\n\n" + REQUEST_NAVIGATION_CODE.strip() + "\n\n",
        text,
        flags=re.MULTILINE | re.DOTALL,
    )

    if count:
        print(f"Replaced request_navigation(): {count}")
        return text

    lines = text.splitlines()
    insert_idx = find_safe_insert_after_imports(text)
    block = [""] + REQUEST_NAVIGATION_CODE.strip().splitlines() + [""]
    lines[insert_idx:insert_idx] = block
    print("Inserted request_navigation()")
    return "\n".join(lines) + "\n"


def ensure_pending_navigation_block(text: str) -> str:
    if '"pending_navigation" in st.session_state' in text or "'pending_navigation' in st.session_state" in text:
        return text

    lines = text.splitlines()
    key_idx = None

    for i, line in enumerate(lines):
        if "main_navigation" in line and "key" in line:
            key_idx = i
            break

    if key_idx is None:
        print("WARNING: main_navigation widget not found.")
        return text

    widget_markers = [
        "st.sidebar.radio",
        "st.sidebar.selectbox",
        "st.radio",
        "st.selectbox",
        "option_menu",
    ]

    start_idx = key_idx
    for i in range(key_idx, max(-1, key_idx - 40), -1):
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
    print("Inserted pending_navigation block before navigation widget.")
    return "\n".join(lines) + "\n"


def fix_fast_button_targets(text: str) -> str:
    replacements = {
        'request_navigation("Дневник питания")': 'request_navigation("📔 Дневник питания")',
        "request_navigation('Дневник питания')": 'request_navigation("📔 Дневник питания")',

        'request_navigation("Умные покупки")': 'request_navigation("🛒 Умные покупки")',
        "request_navigation('Умные покупки')": 'request_navigation("🛒 Умные покупки")',

        'request_navigation("Мой холодильник")': 'request_navigation("🧊 Мой холодильник")',
        "request_navigation('Мой холодильник')": 'request_navigation("🧊 Мой холодильник")',

        'request_navigation("Холодильник")': 'request_navigation("🧊 Мой холодильник")',
        "request_navigation('Холодильник')": 'request_navigation("🧊 Мой холодильник")',

        'request_navigation("Скоро испортится")': 'request_navigation("⏰ Скоро испортится")',
        "request_navigation('Скоро испортится')": 'request_navigation("⏰ Скоро испортится")',

        'request_navigation("Меню")': 'request_navigation("🗓️ Меню на неделю")',
        "request_navigation('Меню')": 'request_navigation("🗓️ Меню на неделю")',

        'request_navigation("Меню на неделю")': 'request_navigation("🗓️ Меню на неделю")',
        "request_navigation('Меню на неделю')": 'request_navigation("🗓️ Меню на неделю")',

        'request_navigation("Аналитика")': 'request_navigation("📊 Аналитика")',
        "request_navigation('Аналитика')": 'request_navigation("📊 Аналитика")',

        'request_navigation("Фото и сканер")': 'request_navigation("📸 Фото и сканер")',
        "request_navigation('Фото и сканер')": 'request_navigation("📸 Фото и сканер")',
    }

    count = 0
    for old, new in replacements.items():
        if old in text:
            text = text.replace(old, new)
            count += 1

    print(f"Fixed fast button targets: {count}")
    return text


def fix_photo_menu_label_and_icon(text: str) -> str:
    """
    Исправляет варианты, когда пункт меню попал как один значок
    или как неправильная emoji-иконка для option_menu.
    """

    # Если где-то пункт был добавлен только как "📸", заменяем на полное имя.
    text = re.sub(
        r'(["\'])📸\1\s*,',
        r'"📸 Фото и сканер",',
        text,
    )

    # Если это dict вида "📸 Фото и сканер": "📸",
    # для streamlit-option-menu лучше использовать bootstrap icon name: "camera".
    text = re.sub(
        r'(["\'])📸 Фото и сканер\1\s*:\s*(["\'])📸\2',
        r'"📸 Фото и сканер": "camera"',
        text,
    )

    # Если кто-то добавил просто "Фото и сканер": "📸"
    text = re.sub(
        r'(["\'])Фото и сканер\1\s*:\s*(["\'])📸\2',
        r'"📸 Фото и сканер": "camera"',
        text,
    )

    print("Fixed photo menu label/icon variants.")
    return text


def add_photo_to_menu_if_missing(text: str) -> str:
    if "📸 Фото и сканер" in text:
        return text

    # Пробуем добавить после быстрого экрана в список.
    patterns = [
        r'(["\']📱 Быстрый экран["\']\s*,)',
        r'(["\']Быстрый экран["\']\s*,)',
    ]

    for pattern in patterns:
        m = re.search(pattern, text)
        if m:
            line_start = text.rfind("\n", 0, m.start()) + 1
            indent = re.match(r"\s*", text[line_start:m.start()]).group(0)
            insert = m.group(1) + f'\n{indent}"📸 Фото и сканер",'
            text = text[:m.start()] + insert + text[m.end():]
            print("Added photo page after fast screen in list menu.")
            return text

    # Пробуем добавить в dict после быстрого экрана.
    patterns = [
        r'(["\']📱 Быстрый экран["\']\s*:\s*.+?,)',
        r'(["\']Быстрый экран["\']\s*:\s*.+?,)',
    ]

    for pattern in patterns:
        m = re.search(pattern, text)
        if m:
            line_start = text.rfind("\n", 0, m.start()) + 1
            indent = re.match(r"\s*", text[line_start:m.start()]).group(0)
            insert = m.group(1) + f'\n{indent}"📸 Фото и сканер": "camera",'
            text = text[:m.start()] + insert + text[m.end():]
            print("Added photo page after fast screen in dict menu.")
            return text

    print("WARNING: Could not add photo page to menu automatically.")
    return text


def find_function_span(text: str, func_name: str):
    pattern = rf'(?m)^def\s+{re.escape(func_name)}\s*\([^)]*\)\s*:'
    m = re.search(pattern, text)
    if not m:
        return None

    start = m.start()
    next_m = re.search(r'(?m)^(def\s+|if\s+__name__\s*==)', text[m.end():])
    if next_m:
        end = m.end() + next_m.start()
    else:
        end = len(text)

    return start, end


def ensure_photo_fast_button(text: str) -> str:
    span = find_function_span(text, "render_fast_action_buttons")
    if not span:
        print("WARNING: render_fast_action_buttons() not found. Cannot add mobile photo button.")
        return text

    start, end = span
    block = text[start:end]

    if "fast_photo_scanner_v13_mobile" in block:
        return text

    add_code = r'''

    # Мобильный доступ к фото-сканеру: если боковое меню на телефоне неудобно,
    # эта кнопка всегда ведёт в раздел фото.
    st.markdown("---")
    if st.button("📸 Фото и сканер", key="fast_photo_scanner_v13_mobile", use_container_width=True):
        request_navigation("📸 Фото и сканер")
'''

    block = block.rstrip() + "\n" + add_code + "\n"
    text = text[:start] + block + text[end:]

    print("Added photo scanner button to quick actions.")
    return text


def ensure_photo_route(text: str) -> str:
    if "render_media_page()" in text:
        # Расширим условие, если есть только часть вариантов.
        text = re.sub(
            r'page\s+in\s+\((["\'])📸 Фото и сканер\1,\s*(["\'])Фото и сканер\2\)',
            'page in ("📸 Фото и сканер", "Фото и сканер", "📸")',
            text,
        )
        return text

    route_patterns = [
        r'(?m)^(\s*)elif\s+page\s*==\s*["\']🏠\s*Главная["\']\s*:',
        r'(?m)^(\s*)elif\s+page\s*==\s*["\']Главная["\']\s*:',
        r'(?m)^(\s*)elif\s+page\s*==\s*["\'][^"\']+["\']\s*:',
    ]

    for pattern in route_patterns:
        m = re.search(pattern, text)
        if m:
            indent = m.group(1)
            route = (
                f'{indent}elif page in ("📸 Фото и сканер", "Фото и сканер", "📸"):\n'
                f'{indent}    render_media_page()\n'
            )
            text = text[:m.start()] + route + text[m.start():]
            print("Added photo route.")
            return text

    print("WARNING: Could not add photo route automatically.")
    return text


def main():
    if not APP.exists():
        print("app.py not found")
        return

    print("=== hotfix_v13_buttons_photo_mobile.py ===")
    backup_file(APP)

    text = APP.read_text(encoding="utf-8")

    text = ensure_media_import(text)
    text = replace_request_navigation(text)
    text = ensure_pending_navigation_block(text)
    text = fix_fast_button_targets(text)
    text = fix_photo_menu_label_and_icon(text)
    text = add_photo_to_menu_if_missing(text)
    text = ensure_photo_fast_button(text)
    text = ensure_photo_route(text)

    APP.write_text(text, encoding="utf-8")

    ok, err = try_compile(APP)

    if ok:
        print()
        print("Готово ✅")
        print("Исправлено:")
        print("- быстрые кнопки переходят через безопасный request_navigation")
        print("- добавлены алиасы страниц с emoji")
        print("- добавлена кнопка 📸 Фото и сканер в быстрые действия")
        print("- исправлен пункт меню фото/сканера")
        print("- расширен роут фото-страницы")
        print()
        print("Теперь запусти:")
        print("python -m streamlit run app.py")
    else:
        print()
        print("Синтаксис всё ещё сломан ❌")
        print(err)
        print()
        print("Пришли, пожалуйста:")
        print("- первые 50 строк app.py")
        print("- функцию render_fast_action_buttons")
        print("- блок меню примерно 1180-1280")


if __name__ == "__main__":
    main()