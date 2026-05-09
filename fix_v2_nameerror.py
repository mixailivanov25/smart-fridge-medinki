from pathlib import Path
from datetime import datetime
import re
import shutil
import py_compile
import subprocess
import sys
import socket
import time
import webbrowser
import os

ROOT = Path.cwd()
APP = ROOT / "app.py"


def backup(path: Path):
    if not path.exists():
        return

    backup_dir = ROOT / "backups" / f"fix_v2_nameerror_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    backup_dir.mkdir(parents=True, exist_ok=True)

    target = backup_dir / path.name
    shutil.copy2(path, target)
    print(f"Backup saved: {target}")


def compile_app():
    py_compile.compile(str(APP), doraise=True)
    print("app.py syntax OK ✅")


def remove_bad_v2_global_calls(text: str) -> str:
    """
    Убирает глобальные вызовы v2, которые могли быть вставлены в app.py:
    apply_v2_design()
    process_v2_query_navigation()

    Они не нужны на уровне app.py, потому что render_v2_app()
    сам вызывает нужный дизайн и обработку.
    """
    lines = []
    removed = 0

    bad_calls = {
        "apply_v2_design()",
        "process_v2_query_navigation()",
    }

    for line in text.splitlines():
        if line.strip() in bad_calls:
            removed += 1
            continue
        lines.append(line)

    print(f"Removed bad v2 global calls: {removed}")
    return "\n".join(lines) + "\n"


def fix_v2_import(text: str) -> str:
    """
    Оставляем безопасный импорт только render_v2_app.
    """
    lines = []
    removed = 0

    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("from v2_foundation import"):
            removed += 1
            continue
        lines.append(line)

    text = "\n".join(lines) + "\n"

    # Вставляем импорт после блока импортов.
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

    lines.insert(insert_idx, "from v2_foundation import render_v2_app")
    print(f"Fixed v2 import. Removed old imports: {removed}")
    return "\n".join(lines) + "\n"


def ensure_direct_v2_fallback(text: str) -> str:
    """
    Проверяет, что есть прямой вход:
    http://localhost:8501/?v2=1
    """
    if "AUTO_V2_DIRECT_ACCESS_START" in text:
        print("Direct v2 fallback already exists.")
        return text

    block = '''
# AUTO_V2_DIRECT_ACCESS_START
try:
    _v2_direct = st.query_params.get("v2", None)
    if isinstance(_v2_direct, list):
        _v2_direct = _v2_direct[0] if _v2_direct else None
    if str(_v2_direct) == "1":
        render_v2_app()
        st.stop()
except Exception:
    pass
# AUTO_V2_DIRECT_ACCESS_END

'''

    m = re.search(r"st\.set_page_config\s*\((?s:.*?)\)\s*", text)

    if m:
        text = text[:m.end()] + "\n" + block + text[m.end():]
        print("Added direct v2 fallback after st.set_page_config.")
        return text

    m = re.search(r"(?m)^def\s+", text)
    if m:
        text = text[:m.start()] + block + text[m.start():]
        print("Added direct v2 fallback before first function.")
        return text

    text = block + text
    print("Added direct v2 fallback at top.")
    return text


def ensure_v2_route(text: str) -> str:
    """
    Проверяет route для пункта меню.
    """
    if 'render_v2_app()' in text and 'Новый интерфейс v2' in text:
        print("v2 route/fallback seems present.")
        return text

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
                f'{indent}elif page in ("🌟 Новый интерфейс v2", "Новый интерфейс v2", "v2"):\n'
                f'{indent}    render_v2_app()\n'
            )
            text = text[:m.start()] + route + text[m.start():]
            print("Added v2 route.")
            return text

    print("Could not add v2 route, but direct fallback should work.")
    return text


def patch_app():
    if not APP.exists():
        raise FileNotFoundError("app.py not found")

    backup(APP)

    text = APP.read_text(encoding="utf-8")

    text = remove_bad_v2_global_calls(text)
    text = fix_v2_import(text)
    text = ensure_direct_v2_fallback(text)
    text = ensure_v2_route(text)

    APP.write_text(text, encoding="utf-8")
    compile_app()


def is_port_open(host="127.0.0.1", port=8501):
    try:
        with socket.create_connection((host, port), timeout=0.4):
            return True
    except Exception:
        return False


def start_streamlit():
    if is_port_open():
        print("Streamlit already running.")
        webbrowser.open("http://localhost:8501/?v2=1")
        return

    creationflags = 0
    if os.name == "nt":
        creationflags = subprocess.CREATE_NEW_CONSOLE

    subprocess.Popen(
        [sys.executable, "-m", "streamlit", "run", "app.py"],
        cwd=str(ROOT),
        creationflags=creationflags,
    )

    for _ in range(30):
        if is_port_open():
            print("Streamlit started.")
            webbrowser.open("http://localhost:8501/?v2=1")
            return
        time.sleep(0.5)

    print("Open manually: http://localhost:8501/?v2=1")


def main():
    print("=== Fix v2 NameError ===")

    patch_app()

    print()
    print("Готово ✅")
    print("Исправлено:")
    print("- удалены лишние apply_v2_design() / process_v2_query_navigation() из app.py;")
    print("- восстановлен безопасный импорт render_v2_app;")
    print("- прямой вход v2 доступен по ссылке:")
    print("  http://localhost:8501/?v2=1")
    print()
    print("Запускаю приложение...")
    print()

    start_streamlit()


if __name__ == "__main__":
    main()
