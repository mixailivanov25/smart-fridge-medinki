from pathlib import Path
import re
import shutil
import py_compile
from datetime import datetime

ROOT = Path(__file__).parent.resolve()
APP = ROOT / "app.py"


def backup_file(path: Path):
    if not path.exists():
        return
    backup_dir = ROOT / "backups" / f"hotfix_v13_photo_menu_syntax_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    backup_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(path, backup_dir / path.name)
    print(f"Backup saved: {backup_dir / path.name}")


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
        return re.sub(
            r"^import streamlit as st\s*$",
            "import streamlit as st\nfrom media_page import render_media_page",
            text,
            count=1,
            flags=re.MULTILINE,
        )

    return "from media_page import render_media_page\n" + text


def fix_broken_dict_insertion(text: str) -> str:
    """
    Исправляет ошибочную вставку вида:

        "📱 Быстрый экран",
            "📸 Фото и сканер": something,

    обратно в:

        "📱 Быстрый экран": something,

    То есть убирает ошибочную строку только в случае словаря.
    """

    patterns = [
        r'(["\']📱\s*Быстрый экран["\']),\s*\n\s*["\']📸 Фото и сканер["\'](?=\s*:)',
        r'(["\']Быстрый экран["\']),\s*\n\s*["\']📸 Фото и сканер["\'](?=\s*:)',
    ]

    for pattern in patterns:
        text = re.sub(pattern, r"\1", text)

    return text


def remove_offending_photo_line_if_needed(text: str) -> str:
    """
    Если после основного исправления SyntaxError всё ещё указывает
    на одиночную строку '📸 Фото и сканер', удаляем именно её.
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


def find_matching_bracket(text: str, start: int, open_ch="[", close_ch="]"):
    depth = 0
    for i in range(start, len(text)):
        ch = text[i]
        if ch == open_ch:
            depth += 1
        elif ch == close_ch:
            depth -= 1
            if depth == 0:
                return i
    return -1


def ensure_menu_item_in_list(text: str) -> str:
    """
    Добавляет '📸 Фото и сканер' только в список страниц.
    Специально не трогает словари.
    """

    if '"📸 Фото и сканер"' in text or "'📸 Фото и сканер'" in text:
        # Строка уже может быть в роутинге. Поэтому ниже проверим именно списки.
        pass

    occurrences = []
    for marker in ['"📱 Быстрый экран"', "'📱 Быстрый экран'", '"Быстрый экран"', "'Быстрый экран'"]:
        start = 0
        while True:
            idx = text.find(marker, start)
            if idx == -1:
                break
            occurrences.append((idx, marker))
            start = idx + len(marker)

    occurrences.sort()

    for idx, marker in occurrences:
        list_start = text.rfind("[", 0, idx)
        dict_start = text.rfind("{", 0, idx)
        paren_start = text.rfind("(", 0, idx)

        # Нужен именно список, а не словарь.
        if list_start == -1:
            continue

        # Если ближайший контейнер перед строкой — словарь, пропускаем.
        if dict_start > list_start:
            continue

        list_end = find_matching_bracket(text, list_start, "[", "]")
        if list_end == -1 or not (list_start < idx < list_end):
            continue

        block = text[list_start:list_end + 1]

        if "Фото и сканер" in block:
            return text

        # Проверяем, что это похоже на список страниц.
        page_markers = [
            "Главная",
            "Холодильник",
            "Рецепты",
            "Меню",
            "Дневник",
            "Аналитика",
            "Демо",
        ]
        if not any(p in block for p in page_markers):
            continue

        line_start = text.rfind("\n", 0, idx) + 1
        line_end = text.find("\n", idx)
        if line_end == -1:
            line_end = idx + len(marker)

        line = text[line_start:line_end]
        indent = re.match(r"\s*", line).group(0)

        insert_line = f'\n{indent}"📸 Фото и сканер",'

        text = text[:line_end] + insert_line + text[line_end:]
        print("Menu item added to pages list.")
        return text

    print("WARNING: Could not safely add menu item to pages list.")
    print("App will still compile, but page may not appear in sidebar until menu is patched.")
    return text


def ensure_route(text: str) -> str:
    if "render_media_page()" in text:
        return text

    route = 'elif page in ("📸 Фото и сканер", "Фото и сканер"):\n{indent}    render_media_page()\n'

    # Вставляем перед Главной, сохраняя отступ.
    patterns = [
        r'(?m)^(\s*)elif\s+page\s*==\s*["\']🏠\s*Главная["\']\s*:',
        r'(?m)^(\s*)elif\s+page\s*==\s*["\']Главная["\']\s*:',
    ]

    for pattern in patterns:
        m = re.search(pattern, text)
        if m:
            indent = m.group(1)
            new_route = f'{indent}elif page in ("📸 Фото и сканер", "Фото и сканер"):\n{indent}    render_media_page()\n'
            text = text[:m.start()] + new_route + text[m.start():]
            print("Route added before Главная.")
            return text

    print("WARNING: Could not safely add route for photo page.")
    return text


def main():
    if not APP.exists():
        print("app.py not found")
        return

    backup_file(APP)

    text = APP.read_text(encoding="utf-8")

    print("Fixing broken v1.3 photo menu insertion...")

    text = fix_broken_dict_insertion(text)
    text = ensure_import(text)
    text = ensure_menu_item_in_list(text)
    text = ensure_route(text)

    APP.write_text(text, encoding="utf-8")

    ok, err = try_compile(APP)

    if not ok:
        print("First compile failed. Trying emergency cleanup...")
        text = APP.read_text(encoding="utf-8")
        text = remove_offending_photo_line_if_needed(text)
        APP.write_text(text, encoding="utf-8")

        ok, err = try_compile(APP)

    if ok:
        print()
        print("Готово ✅")
        print("app.py снова синтаксически корректен.")
        print()
        print("Теперь запусти:")
        print("python -m streamlit run app.py")
    else:
        print()
        print("Не удалось автоматически исправить синтаксис ❌")
        print("Ошибка:")
        print(err)
        print()
        print("Пришли, пожалуйста, кусок app.py примерно строки 1185-1210.")


if __name__ == "__main__":
    main()