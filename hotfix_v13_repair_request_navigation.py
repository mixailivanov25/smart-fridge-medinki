from pathlib import Path
import re
import shutil
import py_compile
from datetime import datetime

ROOT = Path(__file__).parent.resolve()
APP = ROOT / "app.py"


HELPER_CODE = r'''

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


def backup_file(path: Path):
    backup_dir = ROOT / "backups" / f"hotfix_v13_repair_request_navigation_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
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


def remove_broken_request_navigation(text: str) -> str:
    """
    Удаляет ранее вставленную функцию request_navigation(),
    даже если она была вставлена в неправильное место.
    """

    # Самый ожидаемый вариант: от def request_navigation до st.rerun()
    pattern = r'\n*def\s+request_navigation\s*\(\s*target_page\s*:\s*str\s*\)\s*:\n.*?^\s*st\.rerun\(\)\s*\n?'
    new_text, count = re.subn(pattern, "\n", text, flags=re.MULTILINE | re.DOTALL)

    if count:
        print(f"Removed broken request_navigation() blocks: {count}")
        return new_text

    # Запасной вариант, если сигнатура изменилась.
    pattern2 = r'\n*def\s+request_navigation\s*\([^)]*\)\s*:\n.*?^\s*st\.rerun\(\)\s*\n?'
    new_text, count = re.subn(pattern2, "\n", text, flags=re.MULTILINE | re.DOTALL)

    if count:
        print(f"Removed broken request_navigation() blocks by fallback: {count}")
        return new_text

    print("No existing request_navigation() block found.")
    return text


def line_paren_delta(line: str) -> int:
    """
    Примерно считает изменение глубины скобок в строке.
    Игнорировать строки полностью идеально не нужно, здесь достаточно для импортов.
    """
    # Убираем строковые литералы грубо, чтобы скобки в строках не мешали.
    cleaned = re.sub(r'".*?"', '""', line)
    cleaned = re.sub(r"'.*?'", "''", cleaned)
    return cleaned.count("(") + cleaned.count("[") + cleaned.count("{") - cleaned.count(")") - cleaned.count("]") - cleaned.count("}")


def find_safe_insert_after_imports(text: str) -> int:
    """
    Находит индекс строки после полного блока импортов.
    Учитывает многострочные импорты вида:

        from settings import (
            A,
            B,
        )

    Возвращает номер строки, куда можно безопасно вставить helper.
    """

    lines = text.splitlines()
    depth = 0
    insert_idx = 0
    in_import_block = False

    for i, line in enumerate(lines):
        stripped = line.strip()

        if not stripped:
            # Пустые строки в начале/между импортами можно проходить.
            if insert_idx == i:
                insert_idx = i + 1
            continue

        if stripped.startswith("#"):
            if insert_idx == i:
                insert_idx = i + 1
            continue

        is_import_start = stripped.startswith("import ") or stripped.startswith("from ")

        if is_import_start and depth == 0:
            in_import_block = True
            depth += line_paren_delta(line)
            insert_idx = i + 1

            # Если импорт однострочный, блок импорта всё равно продолжается,
            # потому что дальше могут быть другие import/from.
            if depth <= 0:
                depth = 0
            continue

        if in_import_block and depth > 0:
            depth += line_paren_delta(line)
            insert_idx = i + 1

            if depth <= 0:
                depth = 0
            continue

        if is_import_start and depth == 0:
            insert_idx = i + 1
            continue

        # Первый обычный код после импортов.
        break

    return insert_idx


def insert_request_navigation_safely(text: str) -> str:
    if "def request_navigation(" in text:
        print("request_navigation() already exists after cleanup, not inserting.")
        return text

    lines = text.splitlines()
    insert_idx = find_safe_insert_after_imports(text)

    helper_lines = HELPER_CODE.strip("\n").splitlines()

    # Добавим пустую строку перед и после helper.
    block = [""] + helper_lines + [""]

    lines[insert_idx:insert_idx] = block

    print(f"Inserted request_navigation() safely after imports at line {insert_idx + 1}")
    return "\n".join(lines) + "\n"


def ensure_media_import_not_inside_bad_place(text: str) -> str:
    """
    Проверяет импорт media_page. Если его нет — добавляет после import streamlit as st
    или в конец блока импортов.
    """

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
    print("Added media_page import after imports block.")
    return "\n".join(lines) + "\n"


def main():
    if not APP.exists():
        print("app.py not found")
        return

    print("=== hotfix_v13_repair_request_navigation.py ===")

    backup_file(APP)

    text = APP.read_text(encoding="utf-8")

    text = remove_broken_request_navigation(text)
    text = ensure_media_import_not_inside_bad_place(text)
    text = insert_request_navigation_safely(text)

    APP.write_text(text, encoding="utf-8")

    ok, err = try_compile(APP)

    if ok:
        print()
        print("Готово ✅")
        print("request_navigation() перенесён в безопасное место.")
        print("app.py снова синтаксически корректен.")
        print()
        print("Теперь запусти:")
        print("python -m streamlit run app.py")
    else:
        print()
        print("Синтаксис всё ещё сломан ❌")
        print(err)
        print()
        print("Пришли, пожалуйста, первые 40 строк app.py и строки 1180-1280.")


if __name__ == "__main__":
    main()